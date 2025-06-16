import os
import requests
from PyPDF2 import PdfReader
from config import PDF_DIR
import pdfplumber

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
    all_blocks = []
    for path in filepaths:
        blocks = extract_text_with_structure(path)
        all_blocks.extend(blocks)
    print(f"Extracted {len(all_blocks)} text blocks from {len(filepaths)} PDFs.", flush=True)
    return all_blocks

def extract_text_with_structure(filepath):
    text_blocks = []
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                lines = page.extract_text(layout=True).split('\n')
                for line in lines:
                    text_blocks.append(line.strip())
    except Exception as e:
        print(f"Error reading {filepath} with pdfplumber: {e}")
    print(f"Extracted {len(text_blocks)} text blocks from {filepath}.", flush=True)
    return text_blocks
