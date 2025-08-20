from typing import List, Dict, Optional

def _primary_class(val) -> Optional[str]:
    if isinstance(val, list) and val:
        return str(val[0]).strip()
    if isinstance(val, str):
        return val.strip()
    return None

def _class_contains(neighbor_cls, primary: Optional[str]) -> bool:
    if not primary:
        return False
    p = primary.lower()
    if isinstance(neighbor_cls, list):
        return any(isinstance(x, str) and p in x.lower() for x in neighbor_cls)
    if isinstance(neighbor_cls, str):
        return p in neighbor_cls.lower()
    return False

def _brand_map(records: List[Dict]) -> Dict[str, Dict]:
    out = {}
    for r in records:
        name = str(r.get("Brand Name", "")).strip().lower()
        if name and name not in out:
            out[name] = r
    return out

def _query_text(drug: Dict) -> str:
    return (
        drug.get("Use Case / Indication")
        or drug.get("Brand Name")
        or ""
    )

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
    - Filter neighbors by same Therapeutic Class (first entry if list)
    - Rank by similarity using FAISS over indication text
    - Average neighbor MSPs
    - Ratio = target MSP / comparator average
    """
    # Target MSP
    target_msp = drug.get("Manufacturer Submitted Price")
    if target_msp is None:
        return {
            "Comparator Price": None,
            "Comparator Ratio": None,
            "Comparator Neighbor IDs": [],
            "Comparator Notes": "target_missing_msp",
        }

    # Class filter
    primary_cls = _primary_class(drug.get("Therapeutic Class"))
    if not primary_cls:
        return {
            "Comparator Price": None,
            "Comparator Ratio": None,
            "Comparator Neighbor IDs": [],
            "Comparator Notes": "no_primary_class",
        }

    # FAISS must be available
    if not index or not meta:
        return {
            "Comparator Price": None,
            "Comparator Ratio": None,
            "Comparator Neighbor IDs": [],
            "Comparator Notes": "no_index",
        }

    # Retrieve top chunks by indication text
    try:
        from data.Preprocessing.embeddings_utils import retrieve_top_k
    except Exception:
        return {
            "Comparator Price": None,
            "Comparator Ratio": None,
            "Comparator Neighbor IDs": [],
            "Comparator Notes": "no_retrieve_fn",
        }

    query = _query_text(drug)
    hits = retrieve_top_k(index, meta, query, k=k_hits)

    # Map chunks back to distinct neighbor drugs
    brand_by_name = _brand_map(all_records)
    neighbors = []
    seen_ids = set()
    self_pid = drug.get("Project ID")

    for h in hits:
        name = str(h.get("drug_name") or "").strip().lower()
        if not name:
            continue
        rec = brand_by_name.get(name)
        if not rec:
            continue
        if rec.get("Project ID") == self_pid:
            continue
        if not _class_contains(rec.get("Therapeutic Class"), primary_cls):
            continue
        msp = rec.get("Manufacturer Submitted Price")
        if msp is None:
            continue
        pid = rec.get("Project ID")
        if pid in seen_ids:
            continue
        seen_ids.add(pid)
        neighbors.append(rec)
        if len(neighbors) >= top_n:
            break

    # Compute outputs
    if len(neighbors) < min_neighbors:
        return {
            "Comparator Price": None,
            "Comparator Ratio": None,
            "Comparator Neighbor IDs": [n.get("Project ID") for n in neighbors],
            "Comparator Notes": "neighbors_missing_msp",
        }

    comp_price = sum(n.get("Manufacturer Submitted Price") for n in neighbors) / len(neighbors)
    ratio = (target_msp / comp_price) if comp_price else None

    return {
        "Comparator Price": comp_price,
        "Comparator Ratio": ratio,
        "Comparator Neighbor IDs": [n.get("Project ID") for n in neighbors],
        "Comparator Notes": "ok",
    }
