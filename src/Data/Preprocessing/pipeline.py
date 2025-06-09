import os
import ast
import csv
import json
from config import INPUT_CSV, OUTPUT_DIR
from utils import download_pdfs, text_from_pdfs
from processor import gpt_analyzer


def run_pipeline():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

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

                if generic_name == "N/A":
                    continue

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
                        "Brand Name": row["Brand Name"],
                        "Generic Name": generic_name,
                        "Status": row["Status"],
                        "Therapeutic Area": row["Therapeutic Area"],
                    }
                    for key, value in summary.items():
                        tmp[key] = value
                    
                    output_path = os.path.join(OUTPUT_DIR, f"{project_id}.json")
                    with open(output_path, "w", encoding="utf-8") as f:
                        json.dump(tmp, f, indent=2, ensure_ascii=False)
                    print(f"✅ Saved summary for {project_id} to {output_path}")

            except Exception as e:
                print(f"Failed on {row['Project Number']}: {e}")


if __name__ == "__main__":
    run_pipeline()
    print("🚀 Pipeline completed successfully!")
