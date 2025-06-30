import os
import re
import time
import requests
from PyPDF2 import PdfReader
from config import PDF_DIR
import pdfplumber
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def download_pdfs(links, project_number):
    """Download PDFs from a list of links and save them with a project number prefix"""
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

def extract_text_with_structure(filepath):
    """
    Extracts text from each page of a PDF, preserving page numbers and rough structure.
    Returns a list of dicts: { 'source': filepath, 'page': int, 'text': str }.
    """
    results = []
    try:
        with pdfplumber.open(filepath) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                raw = page.extract_text(layout=True) or ""
                lines = [ln.strip() for ln in raw.split("\n") if ln.strip()]
                if not lines:
                    continue
                results.append({
                    "source": filepath,
                    "page": i,
                    "lines": lines
                })
    except Exception as e:
        print(f"[extract_text_with_structure] {filepath}: {e}")
    print(f"Extracted text from {filepath}: {len(results)} pages.", flush=True)
    return results

def text_from_pdfs(filepaths):
    """
    Converts each page → lines dict into a flat list of line‐blocks.
    """
    all_blocks = []
    for path in filepaths:
        pages = extract_text_with_structure(path)
        for p in pages:
            for line in p["lines"]:
                all_blocks.append({
                    "source": p["source"],
                    "page": p["page"],
                    "text": line
                })
    print(f"Extracted {len(all_blocks)} lines from {len(filepaths)} PDFs.", flush=True)
    return all_blocks

def normalize_generic_name(name: str):
    """
    Normalize generic drug name field and generating subcomponents for robust searching
    """
    name = name.strip()
    name = re.sub(r"\b(?:and|AND|&)\b", " ", name)
    name = re.sub(r"\([^)]*\)", "", name)
    name = re.sub(r"\b(in\s+combo(?:nation)?|combo(?:nation)?)\b", "", name, flags=re.IGNORECASE)
    name = name.replace("/", " ").replace(",", " ").replace("-", " ").replace("+", " ")
    name = re.sub(r"\s+", " ", name).strip()

    parts = name.split()
    variants = set()

    if name:
        variants.add(name)

    for part in parts:
        if len(part) > 2:
            variants.add(part)

    if len(parts) > 1:
        for i in range(len(parts)):
            for j in range(i+1, len(parts)+1):
                phrase = " ".join(parts[i:j])
                if phrase and len(phrase) > 3:
                    variants.add(phrase)

    return list(variants)


def get_price_from_formulary(generic_name: str):
    """Scrape Ontario Formulary for drug price using Selenium"""
    search_variants = normalize_generic_name(generic_name)
    print(search_variants, flush=True)
    for variant in search_variants:
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(options=options)

            url = "https://www.formulary.health.gov.on.ca/formulary/"
            driver.get(url)

            keyword_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "searchForm:keywordField"))
            )
            keyword_input.clear()
            keyword_input.send_keys(variant)
            search_button = driver.find_element(By.ID, "searchForm:searchButton")
            search_button.click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "j_id_l:searchResultFull_data"))
            )

            rows = driver.find_elements(By.CSS_SELECTOR, "#j_id_l\\:searchResultFull_data > tr")

            prices = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 5:
                    price_text = cells[4].text.strip().replace(",", "")
                    try:
                        prices.append(float(price_text))
                    except ValueError:
                        continue

            driver.quit()
            if prices:
                return max(prices)

            return None

        except Exception as e:
            continue
