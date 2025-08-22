# data/Preprocessing/addedParams/comparator_price.py
from typing import List, Dict, Optional
from data.Preprocessing.embeddings_utils import retrieve_top_k


def compute_comparator_price(
    drug: Dict,
    all_records: List[Dict],
    index,
    meta,
    k_hits: int = 60,
    top_n: int = 10,
    min_neighbors: int = 3,
) -> Dict:
    """
    Param 4: Domestic Comparator Pricing
      - Find neighbors in the same Therapeutic Class
      - Rank by similarity using FAISS on indication text
      - Average neighbor MSPs
      - Ratio = target MSP / comparator average
    """

    # 1) target MSP
    try:
        target_msp = float(drug.get("Manufacturer Submitted Price"))
    except Exception:
        target_msp = None
    if target_msp is None:
        return {
            "Comparator Price": None,
            "Comparator Ratio": None,
            "Comparator Neighbor IDs": [],
            "Comparator Notes": "target_missing_msp",
        }

    # 2) primary therapeutic class
    tc = drug.get("Therapeutic Class")
    primary_class: Optional[str] = None
    if isinstance(tc, list) and tc:
        primary_class = str(tc[0]).strip()
    elif isinstance(tc, str) and tc.strip():
        primary_class = tc.strip()
    if not primary_class:
        return {
            "Comparator Price": None,
            "Comparator Ratio": None,
            "Comparator Neighbor IDs": [],
            "Comparator Notes": "no_primary_class",
        }
    primary_class = primary_class.lower()

    # 3) index ready
    if not index or not meta:
        return {
            "Comparator Price": None,
            "Comparator Ratio": None,
            "Comparator Neighbor IDs": [],
            "Comparator Notes": "no_index",
        }

    # 4) query text and retrieve similar chunks
    query = drug.get("Use Case / Indication") or drug.get("Brand Name") or ""
    hits = retrieve_top_k(index, meta, query, k=k_hits)

    # 5) quick brand lookup
    brand_map: Dict[str, Dict] = {}
    for r in all_records:
        name = str(r.get("Brand Name", "")).strip().lower()
        if name and name not in brand_map:
            brand_map[name] = r

    # 6) collect neighbors
    neighbors: List[Dict] = []
    seen_pids = set()
    self_pid = drug.get("Project ID")

    for h in hits:
        brand = str(h.get("drug_name") or "").strip().lower()
        if not brand:
            continue

        rec = brand_map.get(brand)
        if not rec:
            continue

        pid = rec.get("Project ID")
        if not pid or pid == self_pid or pid in seen_pids:
            continue

        # same class check
        n_cls = rec.get("Therapeutic Class")
        if isinstance(n_cls, list):
            n_text = " | ".join(str(x) for x in n_cls if isinstance(x, str)).lower()
        elif isinstance(n_cls, str):
            n_text = n_cls.lower()
        else:
            n_text = ""

        if not n_text or primary_class not in n_text:
            continue

        # neighbor MSP must exist
        try:
            msp_val = float(rec.get("Manufacturer Submitted Price"))
        except Exception:
            msp_val = None
        if msp_val is None:
            continue

        neighbors.append(rec)
        seen_pids.add(pid)
        if len(neighbors) >= top_n:
            break

    # 7) compute comparator average and ratio
    if len(neighbors) < min_neighbors:
        return {
            "Comparator Price": None,
            "Comparator Ratio": None,
            "Comparator Neighbor IDs": [n.get("Project ID") for n in neighbors],
            "Comparator Notes": "neighbors_missing_msp",
        }

    total = 0.0
    for n in neighbors:
        total += float(n.get("Manufacturer Submitted Price"))

    comp_price = total / len(neighbors) if neighbors else None
    ratio = (target_msp / comp_price) if comp_price else None

    return {
        "Comparator Price": comp_price,
        "Comparator Ratio": ratio,
        "Comparator Neighbor IDs": [n.get("Project ID") for n in neighbors],
        "Comparator Notes": "ok",
    }
