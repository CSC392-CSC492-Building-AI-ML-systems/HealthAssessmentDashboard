from __future__ import annotations
from typing import Any, Dict, List, Optional
import os, textwrap
from openai import OpenAI   
import logging
logger = logging.getLogger(__name__)        

MODEL = "gpt-4o-mini"   # TBD if this is the right model

SYSTEM_PROMPT = """
You are a formal pharmaceutical market-access assistant for Canada.

Requirements:
    - Answer the user's question directly in the first 1–3 sentences.
    - Keep a concise, formal tone; context is medicines/drugs and market access.
    - Assume Canadian systems: Health Canada (NOC/DIN), CADTH, INESSS (Québec), pCPA.
    - Use CAD for currency and metric units.
    - Use only the provided context; if unknown, state that transparently.
    - If a prediction (price or timeline) is supplied, include it with uncertainty language.
    - Prefer short paragraphs and bullet points; avoid markdown tables.
    - Include a brief non-advice caveat.
    - If sources are provided, include a short "Sources:" section listing them.
Output layout (exact order):
    1) Direct answer (1–3 sentences).
    2) Key details (bullets).
    3) Caveats/assumptions if applicable (1–3 bullets; include uncertainty and non-advice disclaimer).
    4) Sources (only if provided).
"""

def reformat(
    user_query: str,
    data_dict: Dict[str, Any],
    prediction: Optional[Dict[str, Any]] = None,
    *,
    client: Optional[Any] = None,
    model: str = MODEL,
    temperature: float = 0.2,
    max_output_tokens: int = 700,
) -> str:
    """
    STEP-3: Given normalized retrieval + optional prediction, return the FINAL user-facing answer.
    Expects data_dict keys from your normalizer:
      - snippets: List[{ "text": str, "score"?: float }]
      - sources:  List[{ "title": str, "url": str, "agency"?: str, "date"?: str, "snippet"?: str }]
      - structured: Dict[str, Any]
      - jurisdiction: {"country":"Canada", "province"?: str}
    """
    if not isinstance(user_query, str) or not user_query.strip():
        raise ValueError("user_query must be a non-empty string")
    if not isinstance(data_dict, dict):
        raise ValueError("data_dict must be a dict")

    # Build/OpenAI client
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        client = OpenAI(api_key=api_key)

    # Compact prompt inputs (normalizer already capped/deduped)
    jurisdiction = _format_jurisdiction(data_dict.get("jurisdiction") or {"country": "Canada"})
    snippets_block = _format_snippets(data_dict.get("snippets") or [])
    structured_block = _format_structured(data_dict.get("structured") or {})
    prediction_block = _format_prediction(prediction)
    sources_list: List[Dict[str, str]] = list(data_dict.get("sources") or [])[:8]

    user_block = textwrap.dedent(f"""
    Question:
    {user_query.strip()}

    Jurisdiction:
    {jurisdiction}

    Context snippets (evidence):
    {snippets_block or "None."}

    Structured facts:
    {structured_block or "None."}

    Prediction (if any):
    {prediction_block or "None."}

    Please respond using exactly the required 4-part layout and avoid markdown tables.
    """).strip()

    # Single model call
    try:
        resp = client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=max_output_tokens,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_block},
            ],
        )
    except Exception:
        logger.exception("OpenAI chat.completions.create failed")
        return ("Sorry, I’m unable to generate a response right now. "
                "Please try again in a moment.")

    # Basic response validation
    choice = resp.choices[0] if getattr(resp, "choices", None) else None
    text = getattr(getattr(choice, "message", None), "content", None)
    if not text:
        logger.error("OpenAI returned no content: %r", resp)
        return ("Sorry, I couldn’t produce a response with the available context. "
                "Please try again.")

    text = text.strip()

    # Minimal post-check: append Sources only if we have them and the model forgot.
    if sources_list and "Sources:" not in text:
        text += "\n\nSources:\n" + "\n".join(_format_source_line(s) for s in sources_list)
    # If there are no sources, we do nothing; the model was told to omit the section.

    return text

# ----------------------------- helper functions ------------------------------

def _format_snippets(snippets: List[Any]) -> str:
    """List[{text}] -> bullet lines. Assumes ≤6 items from normalizer."""
    lines: List[str] = []
    for item in snippets:
        txt = (item.get("text") if isinstance(item, dict) else str(item)) or ""
        txt = " ".join(txt.split())
        if len(txt) > 400:
            txt = txt[:400] + "…"
        if txt:
            lines.append(f"- {txt}")
    return "\n".join(lines)

def _format_structured(structured: Dict[str, Any]) -> str:
    """Priority fields first; then a few extras."""
    priority = [
        "drug_name", "sponsor", "indication", "din", "noc_date",
        "cadth_status", "inesss_status", "pcpa_status",
    ]
    lines: List[str] = []
    for k in priority:
        v = structured.get(k)
        if v is not None and str(v).strip():
            lines.append(f"- {k}: {v}")
    if len(lines) < 8:
        for k, v in structured.items():
            if k in priority:
                continue
            if v is not None and str(v).strip():
                lines.append(f"- {k}: {v}")
            if len(lines) >= 8:
                break
    return "\n".join(lines)

def _format_prediction(pred: Optional[Dict[str, Any]]) -> str:
    """Render price or timeline into concise bullets (range/unit vs milestones/interval)."""
    if not pred:
        return ""
    ptype = (pred.get("type") or "").lower()
    conf = pred.get("confidence")
    val = pred.get("value") or {}
    assumptions = pred.get("assumptions") or []

    out: List[str] = []
    if ptype == "price":
        rng = val.get("range_cad")
        unit = val.get("unit")
        if isinstance(rng, (list, tuple)) and len(rng) == 2:
            out.append(f"- Price range (CAD): {rng[0]}–{rng[1]}" + (f" {unit}" if unit else ""))
        elif "point_cad" in val:
            out.append(f"- Predicted price (CAD): {val['point_cad']}" + (f" {unit}" if unit else ""))
    elif ptype == "timeline":
        if isinstance(val.get("milestones"), list) and val["milestones"]:
            out.append("- Timeline milestones:")
            for m in val["milestones"][:5]:
                name = m.get("name") or m.get("milestone") or "Milestone"
                date = m.get("date") or m.get("eta") or "TBD"
                out.append(f"  • {name}: {date}")
        elif "interval_months" in val:
            out.append(f"- Estimated interval: ~{val['interval_months']} months")
        if "eta_date" in val:
            out.append(f"- Estimated date: {val['eta_date']}")
    if conf is not None:
        out.append(f"- Confidence: {conf}")
    for a in assumptions[:3]:
        out.append(f"- Assumption: {a}")
    return "\n".join(out)

def _format_source_line(s: Dict[str, str]) -> str:
    title = str(s.get("title") or "Source").strip()
    agency = str(s.get("agency") or "").strip()
    date = str(s.get("date") or "").strip()
    url = str(s.get("url") or "").strip()
    parts = [title] + ([agency] if agency else []) + ([date] if date else [])
    line = " — ".join(parts)
    if url:
        line += f" — {url}"
    return f"- {line}"

# (Simple inline jurisdiction formatter; avoids extra helper noise)
def _format_jurisdiction(j: Dict[str, Any]) -> str:
    country = (j.get("country") or "Canada").strip()
    province = (j.get("province") or "").strip()
    return f"{country}" + (f" — {province}" if province else "")
