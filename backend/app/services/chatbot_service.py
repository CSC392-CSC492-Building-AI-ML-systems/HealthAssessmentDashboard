from fastapi import UploadFile
from app.models.user import User
from app.models.chat_message import ChatMessage
from app.models.chat_history import ChatHistory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.rag_tools.intent_classifier.intent_classifier import intent_classifier
from typing import List, Dict, Any, Optional, Tuple
from app.models.enums import IntentEnum
from app.services.agent_tools import (
    retriever_service,
    price_rec_service,
    timeline_rec_service,
)
# STEP 3 Imports
import asyncio
import json
import logging
from app.rag_tools.llm_response_formatter import reformat



class ChatbotService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_user(self, user_id: int) -> User:
        """Helper to get and validate user existence."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        return user

    async def _get_session(self, session_id: int, user_id: int) -> ChatHistory:
        """Helper to get and validate chat session existence."""
        result = await self.db.execute(
            select(ChatHistory).where(
                ChatHistory.id == session_id,
                ChatHistory.user_id == user_id
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise ValueError("Session not found")
        return session

    async def create_chat(self, user_id: int, title: str):
        """Create a new chat session for a user"""
        # Validate user exists
        await self._get_user(user_id)
        
        chat = ChatHistory(chat_summary=title, user_id=user_id)
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        return chat

    async def get_sessions(self, user_id: int):
        """Retrieve all chat sessions for a specific user"""
        # Validate user exists
        await self._get_user(user_id)

        result = await self.db.execute(
            select(ChatHistory).where(ChatHistory.user_id == user_id)
        )
        return result.scalars().all()

    async def get_session(self, session_id: int, user_id: int):
        """Retrieve a specific chat session by session_id and user_id"""
        # Validate user exists
        await self._get_user(user_id)
        
        # Get and validate session
        return await self._get_session(session_id, user_id)

    async def rename_session(self, session_id: int, user_id: int, new_title: str):
        """Rename a chat session by updating its title"""
        # Validate both user and session exist
        await self._get_user(user_id)
        await self._get_session(session_id, user_id)

        result = await self.db.execute(
            update(ChatHistory)
            .where(ChatHistory.id == session_id, ChatHistory.user_id == user_id)
            .values(chat_summary=new_title)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.commit()
        return result.rowcount > 0

    async def delete_session(self, session_id: int, user_id: int):
        """Delete a chat session by session_id and user_id"""
        # Validate both user and session exist
        await self._get_user(user_id)
        await self._get_session(session_id, user_id)

        result = await self.db.execute(
            delete(ChatHistory).where(ChatHistory.id == session_id, ChatHistory.user_id == user_id)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def send_message(self, session_id: int, user_id: int, message: str):
        """Send a message in a chat session and return the bot's response"""
        # Validate both user and session exist
        await self._get_user(user_id)
        session = await self._get_session(session_id, user_id)

        user_msg = ChatMessage(
            role="USER",
            content=message,
            chat_history_id=session_id
        )
        self.db.add(user_msg)

        # TODO: Implement actual bot response logic involves implementing the 
        # RAG pipeline and LLM response generation - OUR-45

        bot_msg = ChatMessage(
            role="ASSISTANT",
            content=f"Bot received: '{message}'",
            chat_history_id=session_id
        )
        self.db.add(bot_msg)
        await self.db.commit()

        return {"user_message": user_msg.content, "bot_response": bot_msg.content}

    async def get_messages(self, session_id: int, user_id: int):
        """Retrieve all messages in a chat session"""
        # Validate both user and session exist
        await self._get_user(user_id)
        await self._get_session(session_id, user_id)

        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.chat_history_id == session_id)
            .order_by(ChatMessage.created_at)
        )
        return result.scalars().all()

    async def upload_context_file(self, session_id: int, user_id: int, file: UploadFile) -> bool:
        """Upload a context file for a chat session"""
        # Validate both user and session exist
        await self._get_user(user_id)
        await self._get_session(session_id, user_id)

        # Save the file and optionally extract content or embeddings
        return True  # Placeholder
    
    async def call_tools(self, query: str) -> List[Dict[str, Any]]:
        """Route *query* to the appropriate tools based on classified intents.

        The function executes the following high-level flow:

            1. Use the intent classifier to detect which tools are required.
            2. For each intent, invoke the matching tool in the correct order.
               • VECTORDB is a retriever returning metadata (list of dictionaries).
               • PRICE_REC_SERVICE is an ML service that depends on metadata
                 returned from a retriever; therefore it is executed after
                 the relevant retriever to build its input.
               • TIMELINE_REC_SERVICE is independent and can be called at any
                 point.
            3. Collect every individual tool response inside *responses*.
            4. Return the list of responses.

        The return value is a list of dictionaries, each having the shape:
            {
                "intent": IntentEnum value,
                "response": <tool-specific output>,
            }
        """
        # 1) Classify the query.
        intents = intent_classifier(query)
        if not intents:
            return []

        # 2) Establish order of execution of the tools
        ordered_intents = [
            IntentEnum.VECTORDB,
            IntentEnum.PRICE_REC_SERVICE,
            IntentEnum.TIMELINE_REC_SERVICE,
        ]
        execution_plan = [i for i in ordered_intents if i in intents]

        responses: List[Dict[str, Any]] = []
        metadata: List[Dict[str, Any]] | None = None

        for intent in execution_plan:
            if intent == IntentEnum.VECTORDB:
                metadata = retriever_service.retrieve(query)
                responses.append({"intent": intent, "response": metadata})

            elif intent == IntentEnum.PRICE_REC_SERVICE:
                # Metadata from the USER vector-DB
                meta_data = metadata or {}
                # TODO: Structure the metadata into the structure expected by the ML model.
                prediction = price_rec_service.predict({"metadata": meta_data})
                responses.append({"intent": intent, "response": prediction})

            elif intent == IntentEnum.TIMELINE_REC_SERVICE:
                timeline_data = timeline_rec_service.query(query)
                responses.append({"intent": intent, "response": timeline_data})

        return responses
    
    # STEP 3: Normalizer pre-calling LLM response formatter
    def normalize_tool_responses(self, query: str, responses: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        """Normalize STEP-2 outputs into tuple of (data_dict, prediction) for the LLM response formatter.
        Keeps <=6 snippets, <=8 deduped sources; copies easy structured facts, picks one prediction (price or timeline), sets jurisdiction=Canada (+province if detected).

        data_dict fields:
        - snippets:   <=6 short evidence texts (best-first; deduped)
        - sources:    <=8 deduped citation entries {title, url, agency, date, snippet}
        - structured: “easy win” fields if present (drug_name, din, cadth_status, etc.)
        - jurisdiction: {"country":"Canada", "province"?: str}  # best-effort from user query
        - intent_trace: lightweight log of which intents ran (for debugging)

        prediction (or None):
        - { "type": "price"|"timeline",
            "value": {...},        # e.g., {"range_cad":[lo,hi],"unit":"..."} OR {"milestones":[...]}
            "confidence": float|str|None,
            "assumptions": [str, ...]  # first 3 max
            }

        """
        import re
        from urllib.parse import urlparse

        # ------------------------------- constants -------------------------------
        MAX_SNIPPETS = 6
        MAX_SOURCES  = 8

        # ------------------------------- helper functions -------------------------------
        # Province detection: simple regex over user query (best-effort).
        def _detect_province(text: str) -> Optional[str]:
            pats = {
                r"\bontario\b|\bon\b": "Ontario",
                r"\bqu[eé]bec\b|\bqc\b": "Québec",
                r"\bbritish\s+columbia\b|\bbc\b": "British Columbia",
                r"\balberta\b|\bab\b": "Alberta",
                r"\bmanitoba\b|\bmb\b": "Manitoba",
                r"\bsaskatchewan\b|\bsk\b": "Saskatchewan",
                r"\bnova\s+scotia\b|\bns\b": "Nova Scotia",
                r"\bnew\s+brunswick\b|\bnb\b": "New Brunswick",
                r"\bnewfoundland(?:\s+and\s+labrador)?\b|\bnl\b": "Newfoundland and Labrador",
                r"\bprince\s+edward\s+island\b|\bpei\b": "Prince Edward Island",
                r"\byukon\b|\byt\b": "Yukon",
                r"\bnorthwest\s+territories\b|\bnt\b": "Northwest Territories",
                r"\bnunavut\b|\bnu\b": "Nunavut",
            }
            low = text.lower()
            for pat, name in pats.items():
                if re.search(pat, low):
                    return name
            return None

        # Whitespace/length normalizer: keeps snippets/titles compact (to control+reduce token cost).
        def _clean(s: Any, limit: int = 400) -> str:
            t = str(s or "").strip()
            t = re.sub(r"\s+", " ", t)
            return (t[:limit] + "…") if len(t) > limit else t

        # Retrieve a uniform hit list from different retriever shapes (list, {"hits": [...]}, {"documents": [...]}).
        def _hit_list(payload: Any) -> List[Dict[str, Any]]:
            if isinstance(payload, list):
                return [h for h in payload if isinstance(h, dict)]
            if isinstance(payload, dict):
                if isinstance(payload.get("hits"), list):
                    return [h for h in payload["hits"] if isinstance(h, dict)]
                if isinstance(payload.get("documents"), list):
                    return [h for h in payload["documents"] if isinstance(h, dict)]
            return []

        # Pick the best short text field available on a hit.
        def _snippet(hit: Dict[str, Any]) -> str:
            for k in ("snippet", "text", "content", "passage", "summary"):
                if hit.get(k):
                    return _clean(hit[k])
            return ""

        # Human-friendly title for Sources (fall back to "source"/"document_title").
        def _title(hit: Dict[str, Any]) -> str:
            for k in ("title", "source", "document_title"):
                if hit.get(k):
                    return _clean(hit[k], 200)
            return ""

        # Prefer some explicit "agency"; otherwise infer from URL domain (Canadian regulators first).
        def _agency(hit: Dict[str, Any]) -> str:
            a = (hit.get("agency") or hit.get("source") or "").strip()
            if a:
                return a
            url = (hit.get("url") or "").strip()
            host = urlparse(url).netloc.lower() if url else ""
            if "cadth" in host: return "CADTH"
            if "inesss" in host: return "INESSS"
            if "pmprb" in host: return "PMPRB"
            if "pcpa"  in host: return "pCPA"
            if "canada.ca" in host or "health-products.canada" in host: return "Health Canada"
            return ""

        # Pull “easy win” fields if present; accept nested "structured" or top-level keys.
        def _merge_structured(hit: Dict[str, Any], into: Dict[str, Any]) -> None:
            src = hit.get("structured") if isinstance(hit.get("structured"), dict) else hit
            for k in ("drug_name", "sponsor", "indication", "din", "noc_date",
                    "cadth_status", "inesss_status", "pcpa_status"):
                v = src.get(k)
                if v is not None and str(v).strip() and k not in into:
                    into[k] = v

        # Deduplicate sources by (title, url) and cap list length.
        def _dedupe_sources(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            seen, out = set(), []
            for s in items:
                key = (s.get("title") or "", s.get("url") or "")
                if key not in seen:
                    seen.add(key)
                    out.append(s)
                if len(out) >= MAX_SOURCES:
                    break
            return out

        # Accept enums or strings for intent; normalize to string name for routing/logging.
        def _as_name(v: Any) -> str:
            return getattr(v, "name", str(v))

        # Normalize price-model payload into one tidy shape for STEP-3.
        def _norm_price(p: Dict[str, Any]) -> Dict[str, Any]:
            val: Dict[str, Any] = {}
            rng = p.get("range_cad")
            if isinstance(rng, (list, tuple)) and len(rng) == 2:
                val["range_cad"] = [rng[0], rng[1]]
            else:
                # Support alternate shapes (min/max)
                lo = p.get("low_cad") or p.get("min_cad")
                hi = p.get("high_cad") or p.get("max_cad")
                if lo is not None and hi is not None:
                    val["range_cad"] = [lo, hi]
            if p.get("point_cad") is not None:
                val["point_cad"] = p["point_cad"]
            if p.get("unit"):
                val["unit"] = p["unit"]
            return {
                "type": "price",
                "value": val,
                "confidence": p.get("confidence"),
                "assumptions": list(p.get("assumptions") or [])[:3],
            }

        # Normalize timeline-model payload; keep it compact.
        def _norm_timeline(p: Dict[str, Any]) -> Dict[str, Any]:
            v: Dict[str, Any] = {}
            if isinstance(p.get("milestones"), list):
                v["milestones"] = [
                    {k: m.get(k) for k in ("name", "milestone", "date", "eta") if m.get(k) is not None}
                    for m in p["milestones"][:5]
                    if isinstance(m, dict)
                ]
            if p.get("interval_months") is not None:
                v["interval_months"] = p["interval_months"]
            if p.get("eta_date"):
                v["eta_date"] = p["eta_date"]
            return {
                "type": "timeline",
                "value": v,
                "confidence": p.get("confidence"),
                "assumptions": list(p.get("assumptions") or [])[:3],
            }

        # ------------------------------- init state -------------------------------
        data_dict: Dict[str, Any] = {
            "snippets": [],
            "sources": [],
            "structured": {},
            "jurisdiction": {"country": "Canada"},
            "intent_trace": [],
        }
        province = _detect_province(query)
        if province:
            data_dict["jurisdiction"]["province"] = province

        prediction: Optional[Dict[str, Any]] = None

        # Treat any of these as "retrieval" intents (depending on your IntentEnum).
        retrieval_intents = {"VECTORDB", "CDA_VECTORDB", "USER_VECTORDB"}

        # ------------------------------- main loop --------------------------------
        for item in (responses or []):
            intent_name = _as_name(item.get("intent"))
            payload = item.get("response")
            data_dict["intent_trace"].append({"intent": intent_name})

            # --- RETRIEVER PATH: collect evidence & metadata ----------------------
            if intent_name in retrieval_intents:
                hits = _hit_list(payload)

                # Sort by score descending if provided; otherwise stable order.
                def _score(h: Dict[str, Any]) -> float:
                    try:
                        return float(h.get("score", 0.0))
                    except Exception:
                        return 0.0
                hits.sort(key=_score, reverse=True)

                for h in hits:
                    # snippets: short, readable, deduped later
                    snip = _snippet(h)
                    if snip:
                        one = {"text": snip}
                        try:
                            if "score" in h:  # keep the score if it exists (nice for debugging)
                                one["score"] = float(h["score"])
                        except Exception:
                            pass
                        data_dict["snippets"].append(one)

                    # sources: used for the final "Sources:" section
                    src = {
                        "title": _title(h),
                        "url": (h.get("url") or "").strip(),
                        "agency": _agency(h),
                        "date": (h.get("date") or "").strip(),
                        "snippet": snip,
                    }
                    # Only add if we have at least a title or a URL
                    if src["title"] or src["url"]:
                        data_dict["sources"].append(src)

                    # structured: convenient fields if present (no NLP needed)
                    _merge_structured(h, data_dict["structured"])

            # --- PRICE MODEL PATH -------------------------------------------------
            elif intent_name == "PRICE_REC_SERVICE" and isinstance(payload, dict):
                # If both price & timeline appear, we prefer price as the primary prediction (business rule).
                prediction = _norm_price(payload)

            # --- TIMELINE MODEL PATH ----------------------------------------------
            elif intent_name == "TIMELINE_REC_SERVICE" and isinstance(payload, dict):
                # Only take timeline if price hasn't already been set as the primary prediction.
                if not prediction or prediction.get("type") != "price":
                    prediction = _norm_timeline(payload)

            # Unknown intents are ignored gracefully.

        # ------------------------------ post-processing ---------------------------
        # 1) Dedupe snippets by text and cap to MAX_SNIPPETS
        dedup_snips, seen = [], set()
        for s in data_dict["snippets"]:
            txt = s.get("text", "")
            if txt and txt not in seen:
                seen.add(txt)
                dedup_snips.append(s)
            if len(dedup_snips) >= MAX_SNIPPETS:
                break
        data_dict["snippets"] = dedup_snips

        # 2) Dedupe sources and cap to MAX_SOURCES
        data_dict["sources"] = _dedupe_sources(data_dict["sources"])

        # 3) Drop empty province key for a cleaner payload
        if not data_dict["jurisdiction"].get("province"):
            data_dict["jurisdiction"].pop("province", None)

        return data_dict, prediction