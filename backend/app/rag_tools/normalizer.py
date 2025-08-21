from typing import Any, Dict, List, Optional, Tuple
import re

# Country aliases for jurisdiction context
_COUNTRY_ALIASES = {
    "canada": "Canada",
    "united kingdom": "United Kingdom",
    "uk": "United Kingdom",
    "great britain": "United Kingdom",
    "england": "United Kingdom",
    "japan": "Japan",
    "spain": "Spain",
    "italy": "Italy",
    "netherlands": "Netherlands",
    "germany": "Germany",
    "norway": "Norway",
    "belgium": "Belgium",
    "sweden": "Sweden",
    "australia": "Australia",
    "france": "France",
}


def normalize_tool_responses(
    query: str, 
    responses: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """Normalize STEP-2 outputs into tuple of (data_dict, prediction) for the LLM response formatter.
    
    data_dict fields:
        - "query": <str>,
        - "jurisdiction": {"country": <str|None>, "province"?: <str>, "city"?: <str>},  # province/city optional
        - "snippets": [ {"text": <str>, "score"?: float, "rank"?: int}, ... ]           # ≤6 items
      }
      prediction = normalized price/timeline dict if provided by tools, else None

    prediction (or None):
        - { "type": "price"|"timeline",
            "value": {...},        # e.g., {"range_cad":[lo,hi],"unit":"..."} OR {"milestones":[...]}
            "confidence": float|str|None,
            "assumptions": [str, ...]  # first 3 max
            }

    """

    # ---- constants
    MAX_SNIPPETS = 6

    # Jurisdiction from query, regex-first
    jur = _fallback_jurisdiction(query)

    # Gather snippets + (optional) prediction from tool outputs
    snippets: List[Dict[str, Any]] = []
    prediction: Optional[Dict[str, Any]] = None

    for item in (responses or []):
        intent = _as_name(item.get("intent"))
        payload = item.get("response")

        # Retriever outputs: list of dataclass objects (RetrievalResult) OR dicts
        if intent in {"VECTORDB", "USER_VECTORDB", "CDA_VECTORDB"}:
            hits = payload if isinstance(payload, list) else []
            for h in hits:
                # Support dataclass or dict
                text = getattr(h, "text", None)
                if text is None and isinstance(h, dict):
                    text = h.get("text") or (h.get("metadata") or {}).get("text")
                text = (text or "").strip()
                if not text:
                    continue

                score = getattr(h, "score", None)
                if score is None and isinstance(h, dict):
                    score = h.get("score")

                rank = getattr(h, "rank", None)
                if rank is None and isinstance(h, dict):
                    rank = h.get("rank")

                one = {"text": _clean(text)}
                if score is not None: one["score"] = score
                if rank  is not None: one["rank"]  = rank
                snippets.append(one)

                if len(snippets) >= MAX_SNIPPETS:
                    break

        elif intent == "PRICE_REC_SERVICE" and isinstance(payload, dict):
            prediction = _norm_price(payload)

        elif intent == "TIMELINE_REC_SERVICE" and isinstance(payload, dict):
            # Prefer price if both are present (should not happen!)
            if not prediction or prediction.get("type") != "price":
                prediction = _norm_timeline(payload)

    data_dict = {
        "query": query,
        "jurisdiction": jur or {"country": None},
        "snippets": snippets[:MAX_SNIPPETS],
    }
    return data_dict, prediction


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

def _as_name(v: Any) -> str:
    return getattr(v, "name", str(v))

# Whitespace/length normalizer: keeps snippets/titles compact (to control+reduce token cost).
def _clean(s: Any, limit: int = 400) -> str:
    t = str(s or "").strip()
    t = re.sub(r"\s+", " ", t)
    return (t[:limit] + "…") if len(t) > limit else t

# Normalize price-model payload for STEP-3.
def _norm_price(p: Dict[str, Any]) -> Dict[str, Any]:
    val: Dict[str, Any] = {}
    rng = p.get("range_cad")
    if isinstance(rng, (list, tuple)) and len(rng) == 2:
        val["range_cad"] = [rng[0], rng[1]]
    else:
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

def _fallback_jurisdiction(query: str) -> Dict[str, Optional[str]]:
    q = query.lower()
    # country
    for k, v in _COUNTRY_ALIASES.items():
        if k in q:
            return {"country": v}
    # provinces (Canada)
    prov = _detect_province(query)
    if prov:
        return {"country": "Canada", "province": prov}
    return {"country": None}