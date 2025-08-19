import os, re, json
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv
from openai import OpenAI

from data.Preprocessing.Data.azure_blob_store import load_embeddings
from data.Preprocessing.embeddings_utils import retrieve_top_k

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Broadened patterns to catch "Submitted price Dupilumab: $978.70 ..."
MSP_PATTERNS = [
    r"(?:manufacturer[’']?s submitted price|submitted price(?: to cadth)?|sponsor[’']?s submitted price)"
    r"\s*[:\-]?\s*(?:[^\$]{0,60})?(?:C\$|CAD|\$)\s*([0-9][0-9,\.]+)",
    r"\bMSP\b\s*[:\-]?\s*(?:C\$|CAD|\$)\s*([0-9][0-9,\.]+)",
    r"(?:list price|submitted list price)\s*[:\-]?\s*(?:[^\$]{0,60})?(?:C\$|CAD|\$)\s*([0-9][0-9,\.]+)"
]

UNIT_HINT_RE = re.compile(
    r"(?:per|/)\s*(?:vial|pack|package|kit|pen|syringe|pre[- ]?filled syringe|28[- ]day|month|cycle|mg|mL)\b",
    re.I
)

def _make_snippet(text: str, start: int, end: int, radius: int = 120) -> str:
    s = max(0, start - radius)
    e = min(len(text), end + radius)
    return (text[s:e] or "").replace("\n", " ").strip()

def _clean_money(s: str) -> Optional[float]:
    try:
        return float(s.replace(",", ""))
    except Exception:
        return None

def _scan_for_msp(text: str) -> Tuple[Optional[float], Optional[str], Optional[str]]:
    if not text:
        return None, None, None
    for pat in MSP_PATTERNS:
        for m in re.finditer(pat, text, re.I | re.S):
            val = _clean_money(m.group(1))
            if val is not None:
                tail = text[m.end(): m.end() + 80]
                um = UNIT_HINT_RE.search(tail)
                unit = um.group(0) if um else None
                return val, unit, _make_snippet(text, m.start(), m.end())
    return None, None, None

def _retrieve_context(drug_name: str, k_total: int = 20) -> List[Dict]:
    # lazy import so quick PDF tests do not touch Azure
    try:
        from data.Preprocessing.Data.azure_blob_store import load_embeddings
        index, meta = load_embeddings()
    except Exception:
        index, meta = None, None
    if not index or not meta:
        return []

    from data.Preprocessing.embeddings_utils import retrieve_top_k

    queries = [
        f"{drug_name} manufacturer's submitted price",
        f"{drug_name} MSP",
        f"{drug_name} submitted list price",
        f"{drug_name} submitted price to CADTH",
        f"{drug_name} sponsor submitted price",
    ]
    out = []
    per = max(3, k_total // len(queries))
    for q in queries:
        out.extend(retrieve_top_k(index, meta, q, k=per))
    out.sort(key=lambda r: r["score"])
    # de-dup by (source,page,text[:80])
    seen, uniq = set(), []
    for r in out:
        key = (r.get("source"), r.get("page"), r.get("text", "")[:80])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)
        if len(uniq) >= k_total:
            break
    return uniq

def _llm_disambiguate(drug_name: str, chunks: List[Dict]) -> Dict:
    ctx = []
    for c in chunks[:6]:
        loc = f"{c.get('source','?')}:p{c.get('page','?')}"
        ctx.append(f"[{loc}]\n{c.get('text','')}")
    prompt = f"""
You extract the Manufacturer's Submitted Price from CADTH docs.
Rules:
- Prefer the explicit "Manufacturer's submitted price" or MSP list price.
- Ignore recommended price reductions, post-rebate prices, and scenarios.
- Return a single strict JSON object only.

DRUG: {drug_name}

CONTEXT:
{os.linesep.join(ctx)}

Return schema:
{{
 "msp_value_numeric": float|null,
 "msp_currency": "CAD"|"USD"|null,
 "msp_unit": string|null,
 "msp_note": string|null,
 "evidence_quote": string|null,
 "status": "found"|"ambiguous"|"not_found",
 "source_page_refs": [string]
}}
""".strip()
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL_MSP", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    txt = resp.choices[0].message.content.strip()
    if txt.startswith("```"):
        txt = txt.strip("`")
        if txt.startswith("json"):
            txt = txt[4:]
        txt = txt.strip()
    try:
        data = json.loads(txt)
    except Exception:
        data = {
            "msp_value_numeric": None, "msp_currency": "CAD", "msp_unit": None,
            "msp_note": "parse_error", "evidence_quote": None,
            "status": "not_found", "source_page_refs": []
        }
    return data

def extract_msp(drug_name: str, pdf_text: str = "") -> Dict:
    # If caller passed text, do regex-only and stop. No embeddings. No Azure.
    if pdf_text and pdf_text.strip():
        val, unit, snip = _scan_for_msp(pdf_text)
        if val is not None:
            return {
                "Manufacturer Submitted Price": val,
                "MSP Status": "numeric",
                "MSP Currency": "CAD",
                "MSP Source Refs": ["combined_pdf_text"],
                "MSP Context Text": snip,
                "MSP Unit Hint": unit,
                "MSP Match Type": "regex_pdf"
            }
        return {
            "Manufacturer Submitted Price": None,
            "MSP Status": "not_found",
            "MSP Currency": "CAD",
            "MSP Source Refs": [],
            "MSP Context Text": None,
            "MSP Unit Hint": None,
            "MSP Match Type": "none"
        }

    # Otherwise use retrieval + LLM
    chunks = _retrieve_context(drug_name, k_total=20)
    for ch in chunks:
        v, u, snip = _scan_for_msp(ch.get("text", ""))
        if v is not None:
            ref = f"{ch.get('source','?')}:p{ch.get('page','?')}"
            return {
                "Manufacturer Submitted Price": v,
                "MSP Status": "numeric",
                "MSP Currency": "CAD",
                "MSP Source Refs": [ref],
                "MSP Context Text": snip,
                "MSP Unit Hint": u,
                "MSP Match Type": "regex_retrieval"
            }

    llm = _llm_disambiguate(drug_name, chunks)
    if llm.get("status") == "found" and llm.get("msp_value_numeric") is not None:
        return {
            "Manufacturer Submitted Price": float(llm["msp_value_numeric"]),
            "MSP Status": "llm_parsed",
            "MSP Currency": llm.get("msp_currency") or "CAD",
            "MSP Source Refs": llm.get("source_page_refs") or [],
            "MSP Context Text": llm.get("evidence_quote"),
            "MSP Unit Hint": llm.get("msp_unit"),
            "MSP Match Type": "llm"
        }
    return {
        "Manufacturer Submitted Price": None,
        "MSP Status": "not_found",
        "MSP Currency": "CAD",
        "MSP Source Refs": [],
        "MSP Context Text": None,
        "MSP Unit Hint": None,
        "MSP Match Type": "none"
    }
