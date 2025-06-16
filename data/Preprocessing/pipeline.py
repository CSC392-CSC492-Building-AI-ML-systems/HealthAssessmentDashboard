import os
import ast
import csv
import json
from config import INPUT_CSV, OUTPUT_DIR, PDF_DIR
from utils import text_from_pdfs, download_pdfs
from processor import gpt_analyzer
from datetime import datetime


def run_pipeline():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(INPUT_CSV, newline="", encoding="utf-8-sig") as csvfile:
        print(f"Reading input CSV: {INPUT_CSV}", flush=True)
        reader = csv.DictReader(csvfile)
        print(f"Reader: {reader.fieldnames}", flush=True)
        for row in reader:
            try:
                print(f"Processing row: {row['Project Number']} - {row['Title']}", flush=True)
                links = [link.strip() for link in row["PDF Links"].split(";") if link.strip()]
                project_id = row["Project Number"]
                generic_name = row["Generic Name"]

                if generic_name == "N/A":
                    continue
                
                pdf_files = []
                expected_files = [
                    os.path.join(PDF_DIR, f"{project_id}_{i}.pdf") for i in range(len(links))
            ]

                if all(os.path.exists(f) for f in expected_files):
                    print(f"PDFs already exist for {project_id}, skipping download", flush=True)
                    pdf_files = expected_files
                else:
                    print(f"Downloading PDFs for {project_id}", flush=True)
                    pdf_files = download_pdfs(links, project_id)

                if not pdf_files:
                    print(f"No PDFs downloaded for {project_id}", flush=True)
                    continue
                
                combined_text = text_from_pdfs(pdf_files)

                if not combined_text:
                    print(f"No text extracted for {project_id}", flush=True)
                    continue

                summary_json = gpt_analyzer(combined_text, project_id, generic_name)
                if not summary_json:
                    print(f"No summary returned for {project_id}", flush=True)
                    continue

                summary = json.loads(summary_json)
                print(f"Summary for {project_id}: {summary}", flush=True)
                
                submission_date = datetime.strptime(row.get("Submission Date", "N/A").strip(), "%b %d, %Y").date().isoformat()
                recommendation_date = datetime.strptime(row.get("Recommendation Date", "N/A").strip(), "%b %d, %Y").date().isoformat()
                    
                tmp = {
                    "Project ID": project_id,
                    "Brand Name": row["Brand Name"],
                    "Generic Name": generic_name,
                    "Status": row["Status"],
                    "Therapeutic Area": row["Therapeutic Area"],
                    "Submission Date": submission_date,
                    "Recommendation Date": recommendation_date,
                }
                for key, value in summary.items():
                    tmp[key] = value
                
                output_path = os.path.join(OUTPUT_DIR, f"{project_id}.json")
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(tmp, f, indent=2, ensure_ascii=False)
                print(f"Saved summary for {project_id} to {output_path}", flush=True)

            except Exception as e:
                print(f"Failed on {row['Project Number']}: {e}", flush=True)


if __name__ == "__main__":
    run_pipeline()
    print("Pipeline completed successfully!", flush=True)
