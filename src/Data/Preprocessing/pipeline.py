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

    with open(INPUT_CSV, newline="", encoding="utf-8") as csvfile:
        print(f"📂 Reading input CSV: {INPUT_CSV}")
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(f"🔍 Processing row: {row['Project Number']} - {row['Drug Name']}")
            if row["Status"] in ("Completed", "Complete"):
                continue
            try:
                print(f"🔍 Processing row: {row['Project Number']} - {row['Drug Name']}")
                links = ast.literal_eval(row["PDF Links"])
                project_id = row["Project Number"]
                drug_name = row["Drug Name"]
                print(f"\n📄 Processing: {project_id} - {drug_name}")

                pdf_files = download_pdfs(links, project_id)
                combined_text = text_from_pdfs(pdf_files)

                if not combined_text.strip():
                    print(f"No text extracted for {project_id}")
                    continue

                summary = gpt_analyzer(combined_text)

                if summary:
                    summaries.append(
                        {
                            "Project Number": project_id,
                            "Drug Name": drug_name,
                            "Summary": summary,
                        }
                    )

            except Exception as e:
                print(f"Failed on {row['Project Number']}: {e}")

    output_path = os.path.join(OUTPUT_DIR, "summaries.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)
    print(f"\nSaved summaries to {output_path}")


if __name__ == "__main__":
    run_pipeline()
    print("🚀 Pipeline completed successfully!")
