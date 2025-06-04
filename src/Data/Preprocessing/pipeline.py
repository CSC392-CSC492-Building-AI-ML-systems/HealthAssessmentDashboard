import os
import ast
import csv
import json
from config import INPUT_CSV, OUTPUT_DIR
from utils import download_pdfs, text_from_pdfs
from processor import gpt_analyzer


def run_pipeline():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    summaries = []

    with open(INPUT_CSV, newline="", encoding="utf-8-sig") as csvfile:
        print(f"📂 Reading input CSV: {INPUT_CSV}")
        reader = csv.DictReader(csvfile)
        print(f"Reader: {reader.fieldnames}")
        for row in reader:
            print(f"🔍 Processing row: {row['Project Number']} - {row['Title']}")
            try:
                print(f"🔍 Processing row: {row}")
                print(f"🔍 Processing row: {row['Project Number']} - {row['Title']}")
                links = [link.strip() for link in row["PDF Links"].split(";") if link.strip()]
                print(f"Links found: {links}")
                project_id = row["Project Number"]
                generic_name = row["Generic Name"]

                pdf_files = download_pdfs(links, project_id)
                combined_text = text_from_pdfs(pdf_files)

                if not combined_text.strip():
                    print(f"No text extracted for {project_id}")
                    continue

                summary = json.loads(gpt_analyzer(combined_text))
                print(f"Summary for {project_id}: {summary}")

                if summary:
                    tmp = {
                        "Project ID": project_id,
                        "Generic Name": generic_name,
                        "Status": row["Status"],
                    }
                    for key, value in summary.items():
                        tmp[key] = value
                    summaries.append(tmp)
                    break

            except Exception as e:
                print(f"Failed on {row['Project Number']}: {e}")

    output_path = os.path.join(OUTPUT_DIR, "summaries.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)
    print(f"\nSaved summaries to {output_path}")


if __name__ == "__main__":
    run_pipeline()
    print("🚀 Pipeline completed successfully!")
