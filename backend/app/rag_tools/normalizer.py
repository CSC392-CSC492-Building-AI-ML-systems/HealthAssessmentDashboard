from typing import Any, Dict, List, Optional, Tuple
import re
from urllib.parse import urlparse

def normalize_tool_responses(
    query: str, 
    responses: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
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

    # ---- constants
    MAX_SNIPPETS = 6
    MAX_SOURCES  = 8

    # ---- helper functions
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
        a = str(hit.get("agency") or hit.get("source") or "").strip()
        if a:
            return a
        url = str(hit.get("url") or "").strip()
        host = urlparse(url).netloc.lower() if url else ""
        if "cadth" in host: return "CADTH"
        if "inesss" in host: return "INESSS"
        if "pcpa" in host:  return "pCPA"
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

    # Normalize timeline-model payload, keep things compact.
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

    # ---- init
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
    # Treat any of these as "retrieval" intents depending on IntentEnum
    retrieval_intents = {"VECTORDB", "CDA_VECTORDB", "USER_VECTORDB"}

    # ---- main
    for item in (responses or []):
        intent_name = _as_name(item.get("intent"))
        payload = item.get("response")
        data_dict["intent_trace"].append({"intent": intent_name})

        # --- RETRIEVER PATH: collect evidence & metadata
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
                        if "score" in h: # keep the score if it exists for debugging
                            one["score"] = float(h["score"])
                    except Exception:
                        pass
                    data_dict["snippets"].append(one)

                # sources: used for the final "Sources:" section
                src = {
                    "title": _title(h),
                    "url": str(h.get("url") or "").strip(),
                    "agency": _agency(h),
                    "date": str(h.get("date") or "").strip(),
                    "snippet": snip,
                }
                # Only add if we have at least a title or a URL
                if src["title"] or src["url"]:
                    data_dict["sources"].append(src)

                 # structured: convenient fields if present (no NLP needed)
                _merge_structured(h, data_dict["structured"])

        # --- PRICE MODEL PATH
        elif intent_name == "PRICE_REC_SERVICE" and isinstance(payload, dict):
            prediction = _norm_price(payload)

        # --- TIMELINE MODEL PATH
        elif intent_name == "TIMELINE_REC_SERVICE" and isinstance(payload, dict):
            if not prediction or prediction.get("type") != "price":
                prediction = _norm_timeline(payload)

    # ---- post
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

    # 3) Drop empty province key
    if not data_dict["jurisdiction"].get("province"):
        data_dict["jurisdiction"].pop("province", None)

    return data_dict, prediction
