import sys
import requests
from io import BytesIO
from PyPDF2 import PdfReader
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


# import your extractor
from data.Preprocessing.addedParams.icer_extractor import extract_icer
from data.Preprocessing.addedParams.msp_extractor import extract_msp

def pdf_text_from_url(url: str) -> str:
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=45)
    r.raise_for_status()
    reader = PdfReader(BytesIO(r.content))
    parts = []
    for p in reader.pages:
        try:
            parts.append(p.extract_text() or "")
        except Exception:
            parts.append("")
    return "\n".join(parts).strip()

def main():
    if len(sys.argv) < 3:
        print("Usage: python quick_test_pdf.py <BRAND_NAME> <PDF_URL1> [PDF_URL2 ...]")
        sys.exit(1)

    brand = sys.argv[1]
    urls  = sys.argv[2:]

    for url in urls:
        print("\n" + "="*80)
        print(f"Testing brand: {brand}")
        print(f"PDF: {url}")
        print("="*80)

        text = pdf_text_from_url(url)
        if not text:
            print("No text extracted. Likely a scanned PDF. Skipping.")
            continue


        res = extract_icer(brand, text)  # force regex-first on this PDF
        print("Result:", res)

if __name__ == "__main__":
    main()
