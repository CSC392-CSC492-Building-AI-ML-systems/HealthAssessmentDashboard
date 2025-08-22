import os
import re
import json
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv
from openai import OpenAI

from data.Preprocessing.Data.azure_blob_store import load_embeddings
from data.Preprocessing.embeddings_utils import retrieve_top_k

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ICER_PATTERNS = [
    r'(?:\$|C\$|CAD)\s?([0-9][0-9,\.]+)\s*/\s*(?:QALY|quality[- ]adjusted\s+life\s+year[s]?)',
    r'ICER[:\s]+(?:of\s+)?(?:\$|C\$|CAD)?\s?([0-9][0-9,\.]+)\b',
    r'incremental\s+cost[- ]effectiveness\s+ratio.*?(?:\$|C\$|CAD)\s?([0-9][0-9,\.]+)',
    r'cost\s+per\s+QALY[:\s]+(?:\$|C\$|CAD)?\s?([0-9][0-9,\.]+)\b',
]

DOMINANT_RE = re.compile(r'\bdominant\b', re.I)
DOMINATED_RE = re.compile(r'\bdominated\b', re.I)

def _make_snippet(text: str, start: int, end: int, radius: int = 120) -> str:
    s = max(0, start - radius)
    e = min(len(text), end + radius)
    return (text[s:e] or "").replace("\n", " ").strip()

def _clean_money(val: str) -> Optional[float]:
    try:
        return float(val.replace(",", ""))
    except Exception:
        return None

def _scan_for_icer(text: str) -> Tuple[Optional[float], str, Optional[str]]:
    if not text:
        return None, "not_found", None

    m = DOMINANT_RE.search(text)
    if m:
        return 0.0, "dominant", _make_snippet(text, m.start(), m.end())

    m = DOMINATED_RE.search(text)
    if m:
        return None, "dominated", _make_snippet(text, m.start(), m.end())

    for pat in ICER_PATTERNS:
        for m in re.finditer(pat, text, re.I | re.S):
            num = _clean_money(m.group(1))
            if num is not None:
                return num, "numeric", _make_snippet(text, m.start(), m.end())

    return None, "not_found", None

def retrieve_context(drug_name: str, k_total: int = 20) -> List[Dict]:
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
        f"{drug_name} ICER",
        f"{drug_name} cost per QALY",
        f"{drug_name} incremental cost-effectiveness ratio",
        f"{drug_name} base case cost-utility",
        f"{drug_name} economic evaluation results",
        f"{drug_name} dominant dominated",
    ]
    results = []
    per_q = max(3, k_total // len(queries))
    for q in queries:
        results.extend(retrieve_top_k(index, meta, q, k=per_q))
    results.sort(key=lambda r: r["score"])
    unique = []
    seen_keys = set()
    for r in results:
        key = (r.get("source"), r.get("page"), r.get("text", "")[:80])
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique.append(r)
        if len(unique) >= k_total:
            break
    return unique

def llm_disambiguate(drug_name: str, chunks: List[Dict]) -> Dict:
    context_blocks = []
    for c in chunks[:6]:
        loc = f"{c.get('source','?')}:p{c.get('page','?')}"
        txt = c.get("text", "")
        context_blocks.append(f"[{loc}]\n{txt}")

    context_str = "\n\n".join(context_blocks)
    prompt = f"""
You extract the base-case ICER for a Canadian drug assessment.
Rules:
- Prefer base case over scenarios.
- If the text says "dominant" for base case, set icer_value_numeric = 0 and icer_note = "dominant".
- If the text says "dominated" for base case and no number is given, set icer_value_numeric = null and icer_note = "dominated".
- If multiple ICERs exist, choose base case for the primary population.
- Return a single strict JSON object only.

DRUG: {drug_name}

CONTEXT:
{context_str}

Return schema:
{{
 "icer_value_numeric": float|null,
 "icer_currency": "CAD"|"USD"|null,
 "icer_unit": "cost_per_QALY"|null,
 "evidence_quote": string|null,
 "icer_year": int|null,
 "icer_perspective": "public"|"payer"|"societal"|null,
 "icer_population": string|null,
 "icer_comparator": string|null,
 "icer_note": string|null,
 "status": "found"|"ambiguous"|"not_found",
 "source_page_refs": [string]
}}
""".strip()
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL_ICER", "gpt-4o-mini"),
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
            "icer_value_numeric": None,
            "icer_currency": None,
            "icer_unit": None,
            "icer_year": None,
            "icer_perspective": None,
            "icer_population": None,
            "icer_comparator": None,
            "icer_note": "parse_error",
            "status": "not_found",
            "source_page_refs": [],
            "evidence_quote": None
        }
    if data.get("icer_value_numeric") is not None:
        try:
            data["icer_value_numeric"] = float(data["icer_value_numeric"])
        except Exception:
            data["icer_value_numeric"] = None
            data["icer_note"] = "invalid_numeric"
            data["status"] = "ambiguous"
    if not data.get("icer_unit"):
        data["icer_unit"] = "cost_per_QALY"
    if not data.get("icer_currency"):
        data["icer_currency"] = "CAD"
    return data

def extract_icer(drug_name: str, pdf_text: str) -> Dict:
    """
    Returns a normalized ICER record with provenance fields.
    Strategy:
      1) Regex over provided PDF text and stop if given.
      2) Otherwise retrieve top chunks and regex them.
      3) If still not decisive, call LLM disambiguation.
    """
    # Step 1: if caller provided text, do regex-only and stop here
    if pdf_text and pdf_text.strip():
        v, note, snip = _scan_for_icer(pdf_text)
        if note in ("dominant", "dominated", "numeric"):
            return {
                "icer_value_numeric": v,
                "icer_currency": "CAD",
                "icer_unit": "cost_per_QALY",
                "icer_year": None,
                "icer_perspective": None,
                "icer_population": None,
                "icer_comparator": None,
                "icer_note": note,
                "status": "found",
                "source_page_refs": ["combined_pdf_text"],
                "icer_context_text": snip,
                "icer_match_type": "regex_pdf"
            }
        return {
            "icer_value_numeric": None,
            "icer_currency": "CAD",
            "icer_unit": "cost_per_QALY",
            "icer_year": None,
            "icer_perspective": None,
            "icer_population": None,
            "icer_comparator": None,
            "icer_note": "no_match_in_pdf_text",
            "status": "not_found",
            "source_page_refs": [],
            "icer_context_text": None,
            "icer_match_type": "none"
        }

    # Step 2: retrieval and regex over top chunks
    chunks = retrieve_context(drug_name, k_total=20)
    # for ch in chunks:
    #     vv, nn, snip = _scan_for_icer(ch.get("text", ""))
    #     if nn in ("dominant", "dominated", "numeric"):
    #         ref = f"{ch.get('source','?')}:p{ch.get('page','?')}"
    #         return {
    #             "icer_value_numeric": vv,
    #             "icer_currency": "CAD",
    #             "icer_unit": "cost_per_QALY",
    #             "icer_year": None,
    #             "icer_perspective": None,
    #             "icer_population": None,
    #             "icer_comparator": None,
    #             "icer_note": nn,
    #             "status": "found",
    #             "source_page_refs": [ref],
    #             "icer_context_text": snip,
    #             "icer_match_type": "regex_retrieval"
    #         }

    # Step 3: LLM disambiguation
    llm_res = llm_disambiguate(drug_name, chunks)
    if not llm_res.get("source_page_refs"):
        llm_res["source_page_refs"] = [
            f"{c.get('source','?')}:p{c.get('page','?')}" for c in chunks[:6]
        ]
    if llm_res.get("evidence_quote"):
        llm_res["icer_context_text"] = llm_res["evidence_quote"]
    llm_res["icer_match_type"] = "llm"
    return llm_res
