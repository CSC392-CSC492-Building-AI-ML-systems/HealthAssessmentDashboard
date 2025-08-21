import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from data.Preprocessing.Data.azure_blob_store import download_jsonl_from_blob, upload_jsonl_to_blob
from health_canada_noc import get_noc_data
from health_canada_drug import get_health_canada_data
from pcpa import get_pcpa_data
from data.Preprocessing.addedParams.icer_extractor import extract_icer
from data.Preprocessing.addedParams.utils import classify_drug_type, calculate_time_difference
from data.Preprocessing.addedParams.msp_extractor import extract_msp
from data.Preprocessing.addedParams.price_context import extract_price_recommendation_context
from data.Preprocessing.addedParams.comparator_price import compute_comparator_price
from data.Preprocessing.Data.azure_blob_store import load_embeddings

def add_params_to_drug_records(start_index: int = 0, end_index: int = None):
    """Get all data that is useful from the three sources, which are the following parameters for
    prediction model training:

    - PARAM #5: Time from NOC to pCPA Engagement / Reimbursement Listing
    - PARAM #8: Drug Type (Biologic, Rare Disease, Oncology, etc.)
    - PARAM #9: Submission Pathway (Standard, Priority, Conditional, etc.)
    """
    drug_records = download_jsonl_from_blob()

    drug_records = drug_records[start_index:end_index]

    # Load the FAISS index and metadata once
    try:
        index, meta = load_embeddings()
    except Exception:
        index, meta = (None, None)

    for drug in drug_records:
        brand_name = drug["Brand Name"]
        cda_project_number = drug["Project ID"]

        # Add price recommendation context
        price_ctx = extract_price_recommendation_context(drug["Brand Name"], drug.get("Price Recommendation"))
        drug.update(price_ctx)

        # PARAM #2: ICER/QALY
        icer = extract_icer(brand_name, "")
        print("icer", icer)
        drug.update(icer)

        # COLLECT ALL DATA REQUIRED FROM NOC DATABASE
        dins, original_noc_date, therapeutic_class, submission_class = get_noc_data(brand_name)

        # COLLECT ALL DATA REQUIRED FROM THE HEALTH CANADA DATABASE
        original_market_date, atc_code, dosage_forms = get_health_canada_data(dins)

        # COLLECT ALL DATA REQUIRED FROM THE pCPA DATABASE
        pcpa_engagement_letter_issued, negotiation_process_concluded = get_pcpa_data(brand_name, cda_project_number)

        # PARAM #5: Time from NOC to pCPA Engagement / Reimbursement Listing
        print("ORIGINAL DATE", original_noc_date)
        print("pcpa engagement letter issued", pcpa_engagement_letter_issued)
        time_from_noc_to_pcpa = calculate_time_difference(original_noc_date, pcpa_engagement_letter_issued)

        
        msp = extract_msp(brand_name, "")
        print("msp", msp)
        drug.update(msp)

        # PARAM #8: Drug Type (Biologic, Rare Disease, Oncology, etc.)
        drug_type = classify_drug_type(
            atc_code=atc_code,
            active_ingredients=drug["Generic Name"],
            dosage_forms=dosage_forms,
            indication_text=drug["Use Case / Indication"],
            noc_pathway=submission_class
        )
        # ALSO INCLUDE therapeutic_class TO HELP
        # (THIS IS EQUIVALENT TO CALCULATING USING ATC TABLE, AND IS MORE SPECIFIC THAN THE EXISTING Therapeutic Area)

        # PARAM #9: Submission Pathway (Standard, Priority, Conditional, etc.)
        # THIS IS THE submission_class

        drug["Time from NoC to pCPA"] = time_from_noc_to_pcpa
        drug["Drug Type"] = drug_type
        drug["Therapeutic Class"] = therapeutic_class
        drug["Submission Pathway"] = submission_class

    # Pass 2: Comparator Price
    for drug in drug_records:
        comparator_price = compute_comparator_price(drug, drug_records, index, meta)
        print("comparator_price", comparator_price)
        drug.update(comparator_price)

    upload_jsonl_to_blob(drug_records, "params_5_8_9.jsonl")


if __name__ == "__main__":
    add_params_to_drug_records(1, 2)

