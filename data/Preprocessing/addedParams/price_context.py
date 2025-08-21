import os, re, json
from typing import Dict, List, Optional, Tuple, Union
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Phrases commonly used around recommended/annual price (kept for possible future regex use)
PHRASES = [
    r"(?:recommended|recommendation|should not exceed|price cap|price reduction.*?to|be reduced to|at a price of)",
    r"(?:treatment cost|expected to cost|annual cost|cost per year|per year|annually)"
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
    whole = f"{int(round(val))}"
    with_commas = f"{int(round(val)):,}"
    return rf"(?:C\$|CAD|\$)\s*(?:{with_commas}|{whole})(?:\.0+)?"

def _contains_any_target(txt: str, targets: List[float]) -> bool:
    if not txt:
        return False
    for v in targets:
        if f"{int(round(v)):,}" in txt or f"{int(round(v))}" in txt:
            return True
    return False

def _retrieve_context(drug_name: str, k_total: int = 30) -> List[Dict]:
    try:
        from data.Preprocessing.Data.azure_blob_store import load_embeddings
        index, meta = load_embeddings()
    except Exception:
        index, meta = None, None
    if not index or not meta:
        return []

    from data.Preprocessing.embeddings_utils import retrieve_top_k

    queries = [
        f"{drug_name} how much does * cost",
        f"{drug_name} treatment cost",
        f"{drug_name} expected to cost per year",
        f"{drug_name} annual cost per year",
        f"{drug_name} price should not exceed",
        f"{drug_name} price cap",
    ]

    out = []
    per = max(3, k_total // len(queries))
    for q in queries:
        out.extend(retrieve_top_k(index, meta, q, k=per))
    out.sort(key=lambda r: r["score"])

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

def _llm_price_rec(drug_name: str, targets: List[float], chunks: List[Dict]) -> Dict:
    """Ask for quotes that INCLUDE the exact targets, then hard-validate."""
    # Prefer chunks that already contain the numeric targets
    prioritized = [c for c in chunks if _contains_any_target(c.get("text",""), targets)]
    if not prioritized:
        prioritized = chunks  # fallback

    ctx_blocks = []
    for c in prioritized[:12]:
        loc = f"{c.get('source','?')}:p{c.get('page','?')}"
        ctx_blocks.append(f"[{loc}]\n{c.get('text','')}")
    context = os.linesep.join(ctx_blocks)

    target_str = ", ".join([f"${int(round(v)):,}" for v in targets])

    prompt = f"""
You must return sentence-level quotes from the CDA/CADTH document that literally include one of these exact values: {target_str}.
Rules:
- Only return quotes that CONTAIN one of those exact numbers (with comma formatting if shown).
- Prefer "How much does <drug> cost", "Treatment cost", "expected to cost", "per year", "annually".
- Return up to 3 matches.
- If none contain those exact numbers, return an empty list.

Return ONE strict JSON object:
{{
  "matches": [
    {{
      "quote": string,              // must include an exact target number
      "value": float,               // that exact target as a number (e.g., 12723)
      "unit_hint": string|null,     // e.g., "per year", "annually"
      "source_page_ref": string     // "<source>:p<page>"
    }}
  ]
}}

CONTEXT:
{context}
""".strip()

    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL_PRICECTX","gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    txt = resp.choices[0].message.content.strip()
    if txt.startswith("```"):
        txt = txt.strip("`")
        if txt.startswith("json"):
            txt = txt[4:]
        txt = txt.strip()

    data = {"matches": []}
    try:
        data = json.loads(txt)
    except Exception:
        pass

    # HARD VALIDATION: keep only quotes that literally include the exact target value.
    valid = []
    seen_vals = set()
    for m in data.get("matches", []):
        quote = (m.get("quote") or "").strip()
        val = m.get("value")
        if isinstance(val, str):
            try:
                val = float(val.replace(",", ""))
            except Exception:
                val = None
        ref = (m.get("source_page_ref") or "").strip()
        unit = m.get("unit_hint")

        if not quote or val is None:
            continue

        # check quote contains exact currency pattern for this val
        if not re.search(_value_regex(val), quote):
            continue

        # only keep targets we asked for
        rounded = float(int(round(val)))
        if rounded not in {float(int(round(v))) for v in targets}:
            continue

        if rounded in seen_vals:
            continue
        seen_vals.add(rounded)

        # Try to extract a unit hint if missing
        if not unit:
            um = UNIT_HINT_RE.search(quote)
            unit = um.group(0) if um else None

        valid.append({
            "quote": quote,
            "value": rounded,
            "unit_hint": unit,
            "source_page_ref": ref
        })

    # sort by value to keep output stable (min then max)
    valid.sort(key=lambda x: x["value"] if x["value"] is not None else 0)
    return {"matches": valid}

def extract_price_recommendation_context(
    drug_name: str,
    price_recommendation: Union[Dict, float, int, None],
    pdf_text: str = ""
) -> Dict:
    # Choose targets from min/max (rounded ints so 12,723.00 matches 12723)
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

    # 1) If PDF text provided, you could do regex here (left disabled per your request)
    if pdf_text and pdf_text.strip():
        # (regex path intentionally disabled)
        pass

    # 2) Retrieval (for LLM context only)
    chunks = _retrieve_context(drug_name, k_total=30)

    # 3) LLM-only path with hard validation
    llm = _llm_price_rec(drug_name, targets, chunks)
    hits = llm.get("matches", [])

    if not hits:
        return {
            "Price Rec Context Text": None,
            "Price Rec Unit Hint": None,
            "Price Rec Value Matched": None,
            "Price Rec Match Type": "none",
            "Price Rec Source Refs": [],
        }

    # Build simple, compact output:
    # - Join multiple quotes into a single string so your schema stays simple.
    joined_quote = " | ".join(m["quote"] for m in hits)
    # If only one value matched, expose it; if multiple, set None to avoid implying a single value.
    value_field = hits[0]["value"] if len(hits) == 1 else None
    # If all unit hints are the same, show it; otherwise None.
    units = [m.get("unit_hint") for m in hits if m.get("unit_hint")]
    unit_field = units[0] if units and all(u == units[0] for u in units) else None
    refs = [m.get("source_page_ref") for m in hits if m.get("source_page_ref")]

    return {
        "Price Rec Context Text": joined_quote,
        "Price Rec Unit Hint": unit_field,
        "Price Rec Value Matched": value_field,
        "Price Rec Match Type": "llm",
        "Price Rec Source Refs": refs,
    }
