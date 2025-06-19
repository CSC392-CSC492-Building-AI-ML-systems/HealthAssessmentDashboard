import os
import csv
import json
import argparse
from processor import gpt_analyzer
from datetime import datetime
from config import (
    INPUT_CSV, 
    OUTPUT_DIR, 
    PDF_DIR,
)
from Data.azure_blob_store import flush_embeddings_to_azure, upload_jsonl_to_blob, load_embeddings
from utils import text_from_pdfs, download_pdfs, get_price_from_formulary

def run_pipeline(start_index: int = 0, end_index: int = None):
    """Run the drug summarization pipeline in batches"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    load_embeddings()
    summaries = []

    with open(INPUT_CSV, newline="", encoding="utf-8-sig") as csvfile:
        print(f"Reading input CSV: {INPUT_CSV}", flush=True)
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        print(f"Total rows in CSV: {len(rows)}", flush=True)

        batch = rows[start_index:end_index]
        print(f"Processing rows from index {start_index} to {end_index or len(rows)}", flush=True)

        for idx, row in enumerate(batch, start=start_index):
            try:
                project_id = row["Project Number"]
                title = row.get("Title", "N/A")
                generic_name = row.get("Generic Name", "N/A")
                therapeutic_area = row.get("Therapeutic Area", "N/A")

                print(f"[{idx}] Processing {project_id} - {title}", flush=True)

                # Skip if already processed
                output_path = os.path.join(OUTPUT_DIR, f"{project_id}.json")
                if os.path.exists(output_path):
                    print(f"Summary already exists for {project_id}, skipping", flush=True)
                    continue

                if generic_name == "N/A":
                    print(f"No generic name for {project_id}, skipping", flush=True)
                    continue

                links = [link.strip() for link in row["PDF Links"].split(";") if link.strip()]
                expected_files = [
                    os.path.join(PDF_DIR, f"{project_id}_{i}.pdf") for i in range(len(links))
                ]

                # Download PDFs
                if all(os.path.exists(f) for f in expected_files):
                    print(f"PDFs already exist for {project_id}, skipping download", flush=True)
                    pdf_files = expected_files
                else:
                    print(f"Downloading PDFs for {project_id}", flush=True)
                    pdf_files = download_pdfs(links, project_id)

                if not pdf_files:
                    print(f"No PDFs downloaded for {project_id}, skipping", flush=True)
                    continue
                
                pdf_files = []
                expected_files = [
                    os.path.join(PDF_DIR, f"{project_id}_{i}.pdf") for i in range(len(links))
            ]


                combined_text = text_from_pdfs(pdf_files)
                if not combined_text:
                    print(f"No text extracted for {project_id}, skipping", flush=True)
                    continue

                summary_json = gpt_analyzer(
                    combined_text, 
                    generic_name, 
                    therapeutic_area)
                
                if not summary_json:
                    print(f"No summary returned for {project_id}, skipping", flush=True)
                    continue

                summary = json.loads(summary_json)
                print(f"Summary keys for {project_id}: {list(summary.keys())}", flush=True)

                # Format metadata
                try:
                    submission_date = datetime.strptime(row.get("Submission Date", "N/A").strip(), "%b %d, %Y").date().isoformat()
                except:
                    submission_date = None
                try:
                    recommendation_date = datetime.strptime(row.get("Recommendation Date", "N/A").strip(), "%b %d, %Y").date().isoformat()
                except:
                    recommendation_date = None

                final_summary = {
                    "Project ID": project_id,
                    "Brand Name": row.get("Brand Name", "N/A"),
                    "Generic Name": generic_name,
                    "Status": row.get("Status", "N/A"),
                    "Therapeutic Area": therapeutic_area,
                    "Submission Date": submission_date,
                    "Recommendation Date": recommendation_date,
                }
                final_summary.update(summary)

                # Get price recommendation
                price_info = final_summary.get("Price Recommendation", {})
                if price_info.get("min") is None or price_info.get("max") is None:
                    print(f"Missing price for {project_id}, querying formulary", flush=True)
                    fetched_price = get_price_from_formulary(generic_name)
                    if fetched_price is not None:
                        price_info["min"] = fetched_price
                        price_info["max"] = fetched_price
                        final_summary["Price Recommendation"] = price_info
                        final_summary["Price Source"] = "Ontario Drug Benefit Formulary/Comparative Drug Index"
                        print(f"Found price: ${fetched_price}", flush=True)
                else:
                    final_summary["Price Source"] = "CDA"

                summaries.append(final_summary)

            except Exception as e:
                print(f"[{idx}] Failed on {row.get('Project Number', 'N/A')}: {e}", flush=True)
        
        print("\nFlushing embeddings and jsons to Azure", flush=True)
        flush_embeddings_to_azure()
        upload_jsonl_to_blob(summaries)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run drug summarization pipeline in batches")
    parser.add_argument("--start", type=int, default=0, help="Start index (inclusive)")
    parser.add_argument("--end", type=int, default=None, help="End index (exclusive)")
    args = parser.parse_args()

    run_pipeline(start_index=args.start, end_index=args.end)
    print("Pipeline completed successfully!", flush=True)
