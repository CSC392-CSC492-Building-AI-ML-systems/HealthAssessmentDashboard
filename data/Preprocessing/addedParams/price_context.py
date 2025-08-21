import os, re, json
from typing import Dict, List, Optional, Tuple, Union
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# phrases commonly used around recommended price
PHRASES = [
    r"(?:recommended|recommendation|should not exceed|price cap|price reduction.*?to|be reduced to|at a price of)",
]

UNIT_HINT_RE = re.compile(
    r"(?:per|/)\s*(?:28[- ]day|30[- ]day|month|cycle|patient[- ]year|year|week|day|dose|vial|kit|pen|syringe|pre[- ]?filled syringe|mg|mL)\b",
    re.I
)

def _make_snippet(text: str, start: int, end: int, radius: int = 140) -> str:
    s = max(0, start - radius)
    e = min(len(text), end + radius)
    return (text[s:e] or "").replace("\n", " ").strip()

def _value_regex(val: float) -> str:
    # allow 9580, 9,580, 9,580.0, 9,580.00
    whole = f"{int(round(val))}"
    with_commas = f"{int(round(val)):,}"
    return rf"(?:C\$|CAD|\$)\s*(?:{with_commas}|{whole})(?:\.0+)?"

def _scan_for_price_rec(text: str, targets: List[float]) -> Tuple[Optional[str], Optional[str], Optional[float]]:
    if not text:
        return None, None, None
    # build combined pattern: a phrase near the exact money value
    value_pats = [ _value_regex(v) for v in targets ]
    money_alt  = "(?:" + "|".join(value_pats) + ")"
    phrase_alt = "(?:" + "|".join(PHRASES) + ")"
    pat = re.compile(rf"{phrase_alt}.{{0,120}}?{money_alt}|{money_alt}.{{0,120}}?{phrase_alt}", re.I | re.S)

    for m in pat.finditer(text):
        snip = _make_snippet(text, m.start(), m.end())
        pad  = text[max(0, m.start()-100): m.end()+100]
        um   = UNIT_HINT_RE.search(pad)
        unit = um.group(0) if um else None
        # figure out which target matched
        for v in targets:
            if re.search(_value_regex(v), m.group(0)):
                return snip, unit, v
        return snip, unit, None
    return None, None, None

def _retrieve_context(drug_name: str, k_total: int = 20) -> List[Dict]:
    try:
        from data.Preprocessing.Data.azure_blob_store import load_embeddings
        index, meta = load_embeddings()
    except Exception:
        index, meta = None, None
    if not index or not meta:
        return []
    from data.Preprocessing.embeddings_utils import retrieve_top_k
    queries = [
        f"{drug_name} recommended price",
        f"{drug_name} price should not exceed",
        f"{drug_name} price cap",
        f"{drug_name} price reduction to achieve",
        f"{drug_name} recommended list price",
    ]
    out = []
    per = max(3, k_total // len(queries))
    for q in queries:
        out.extend(retrieve_top_k(index, meta, q, k=per))
    out.sort(key=lambda r: r["score"])
    seen, uniq = set(), []
    for r in out:
        key = (r.get("source"), r.get("page"), r.get("text","")[:80])
        if key in seen: continue
        seen.add(key); uniq.append(r)
        if len(uniq) >= k_total: break
    return uniq

def _llm_price_rec(drug_name: str, targets: List[float], chunks: List[Dict]) -> Dict:
    ctx = []
    for c in chunks[:6]:
        loc = f"{c.get('source','?')}:p{c.get('page','?')}"
        ctx.append(f"[{loc}]\n{c.get('text','')}")
    target_str = ", ".join([f"${int(round(v)):,}" for v in targets])
    prompt = f"""
You must find the specific *recommended price* sentence for the drug and return a short quote that includes one of these exact values: {target_str}.
If you cannot find a sentence that includes any of those exact values, return status "not_found".

Return one strict JSON object with this schema:
{{
 "price_rec_context_text": string|null,
 "price_rec_value_matched": float|null,
 "price_rec_unit_hint": string|null,
 "source_page_refs": [string],
 "status": "found"|"not_found"
}}

CONTEXT:
{os.linesep.join(ctx)}
""".strip()
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL_PRICECTX","gpt-4o-mini"),
        messages=[{"role":"user","content":prompt}],
        temperature=0
    )
    txt = resp.choices[0].message.content.strip()
    if txt.startswith("```"):
        txt = txt.strip("`")
        if txt.startswith("json"): txt = txt[4:]
        txt = txt.strip()
    try:
        data = json.loads(txt)
    except Exception:
        data = {"price_rec_context_text": None, "price_rec_value_matched": None,
                "price_rec_unit_hint": None, "source_page_refs": [], "status": "not_found"}
    # best effort type fix
    if isinstance(data.get("price_rec_value_matched"), str):
        try:
            data["price_rec_value_matched"] = float(data["price_rec_value_matched"].replace(",",""))
        except Exception:
            data["price_rec_value_matched"] = None
    return data

def extract_price_recommendation_context(
    drug_name: str,
    price_recommendation: Union[Dict, float, int, None],
    pdf_text: str = ""
) -> Dict:
    # choose targets from min/max
    targets: List[float] = []
    if isinstance(price_recommendation, dict):
        for k in ("min","max"):
            v = price_recommendation.get(k)
            if isinstance(v, (int,float)):
                targets.append(float(v))
    elif isinstance(price_recommendation, (int,float)):
        targets.append(float(price_recommendation))

    targets = sorted({float(int(round(v))) for v in targets})

    if not targets:
        return {
            "Price Rec Context Text": None,
            "Price Rec Unit Hint": None,
            "Price Rec Value Matched": None,
            "Price Rec Match Type": "none",
            "Price Rec Source Refs": [],
        }

    # 1) If PDF text given, regex-only
    if pdf_text and pdf_text.strip():
        snip, unit, matched = _scan_for_price_rec(pdf_text, targets)
        if snip:
            return {
                "Price Rec Context Text": snip,
                "Price Rec Unit Hint": unit,
                "Price Rec Value Matched": matched,
                "Price Rec Match Type": "regex_pdf",
                "Price Rec Source Refs": ["combined_pdf_text"],
            }
        return {
            "Price Rec Context Text": None,
            "Price Rec Unit Hint": None,
            "Price Rec Value Matched": None,
            "Price Rec Match Type": "none",
            "Price Rec Source Refs": [],
        }

    # 2) Retrieval + regex
    chunks = _retrieve_context(drug_name, k_total=20)
    for ch in chunks:
        snip, unit, matched = _scan_for_price_rec(ch.get("text",""), targets)
        if snip:
            ref = f"{ch.get('source','?')}:p{ch.get('page','?')}"
            return {
                "Price Rec Context Text": snip,
                "Price Rec Unit Hint": unit,
                "Price Rec Value Matched": matched,
                "Price Rec Match Type": "regex_retrieval",
                "Price Rec Source Refs": [ref],
            }

    # 3) LLM fallback, tied to the exact value(s)
    llm = _llm_price_rec(drug_name, targets, chunks)
    if llm.get("status") == "found" and llm.get("price_rec_context_text"):
        return {
            "Price Rec Context Text": llm["price_rec_context_text"],
            "Price Rec Unit Hint": llm.get("price_rec_unit_hint"),
            "Price Rec Value Matched": llm.get("price_rec_value_matched"),
            "Price Rec Match Type": "llm",
            "Price Rec Source Refs": llm.get("source_page_refs") or [],
        }

    return {
        "Price Rec Context Text": None,
        "Price Rec Unit Hint": None,
        "Price Rec Value Matched": None,
        "Price Rec Match Type": "none",
        "Price Rec Source Refs": [],
    }
