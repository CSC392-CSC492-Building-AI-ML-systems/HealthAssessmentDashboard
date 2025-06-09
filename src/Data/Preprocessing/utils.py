import os
import requests
from PyPDF2 import PdfReader
from config import PDF_DIR


def download_pdfs(links, project_number):
    os.makedirs(PDF_DIR, exist_ok=True)
    filepaths = []
    for idx, link in enumerate(links):
        try:
            filename = f"{project_number}_{idx}.pdf"
            filepath = os.path.join(PDF_DIR, filename)
            response = requests.get(link)
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(response.content)
                filepaths.append(filepath)
        except Exception as e:
            print(f"Failed to download {link}: {e}")
    return filepaths


def text_from_pdfs(filepaths):
    all_text = ""
    for path in filepaths:
        try:
            reader = PdfReader(path)
            for page in reader.pages:
                all_text += page.extract_text() or ""
        except Exception as e:
            print(f"Error reading {path}: {e}")
    return all_text.strip()
