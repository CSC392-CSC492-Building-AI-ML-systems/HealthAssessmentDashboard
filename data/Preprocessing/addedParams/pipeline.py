from data.Preprocessing.Data.azure_blob_store import download_jsonl_from_blob
from health_canada_noc import get_noc_data
from health_canada_drug import get_health_canada_data
from pcpa import get_pcpa_data
from data.Preprocessing.addedParams.utils import classify_drug_type, calculate_time_difference
from data.Preprocessing.Data.azure_blob_store import upload_jsonl_to_blob


def get_noc_health_canada_and_pcpa_data(start_index: int = 0, end_index: int = None):
    """Get all data that is useful from the three sources, which are the following parameters for
    prediction model training:

    - PARAM #5: Time from NOC to pCPA Engagement / Reimbursement Listing
    - PARAM #8: Drug Type (Biologic, Rare Disease, Oncology, etc.)
    - PARAM #9: Submission Pathway (Standard, Priority, Conditional, etc.)
    """
    drug_records = download_jsonl_from_blob()

    drug_records = drug_records[start_index:end_index]

    for drug in drug_records:
        brand_name = drug["Brand Name"]
        cda_project_number = drug["Project ID"]

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

    upload_jsonl_to_blob(drug_records, "params_5_8_9.jsonl")


if __name__ == "__main__":
    get_noc_health_canada_and_pcpa_data(1, 2)

