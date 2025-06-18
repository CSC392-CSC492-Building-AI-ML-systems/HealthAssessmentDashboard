import os
import ast
import csv
import json
import argparse
from config import INPUT_CSV, OUTPUT_DIR, PDF_DIR
from utils import text_from_pdfs, download_pdfs
from processor import gpt_analyzer
from datetime import datetime


def run_pipeline(start_index: int = 0, end_index: int = None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

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

                # Download PDFs if not already there
                if all(os.path.exists(f) for f in expected_files):
                    print(f"PDFs already exist for {project_id}, skipping download", flush=True)
                    pdf_files = expected_files
                else:
                    print(f"Downloading PDFs for {project_id}", flush=True)
                    pdf_files = download_pdfs(links, project_id)

                if not pdf_files:
                    print(f"No PDFs downloaded for {project_id}, skipping", flush=True)
                    continue

                combined_text = text_from_pdfs(pdf_files)
                if not combined_text:
                    print(f"No text extracted for {project_id}, skipping", flush=True)
                    continue

                summary_json = gpt_analyzer(combined_text, project_id, generic_name, therapeutic_area)
                if not summary_json:
                    print(f"No summary returned for {project_id}, skipping", flush=True)
                    continue

                summary = json.loads(summary_json)
                print(f"Summary keys for {project_id}: {list(summary.keys())}", flush=True)

                # Format and enrich metadata
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

                # Save result
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(final_summary, f, indent=2, ensure_ascii=False)
                print(f"Saved summary to {output_path}", flush=True)

            except Exception as e:
                print(f"[{idx}] Failed on {row.get('Project Number', 'N/A')}: {e}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run drug summarization pipeline in batches")
    parser.add_argument("--start", type=int, default=0, help="Start index (inclusive)")
    parser.add_argument("--end", type=int, default=None, help="End index (exclusive)")
    args = parser.parse_args()

    run_pipeline(start_index=args.start, end_index=args.end)
    print("Pipeline completed successfully!", flush=True)