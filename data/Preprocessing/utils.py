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

def text_from_pdfs(filepaths):
    """Extract text from a list of PDF filepaths using pdfplumber"""
    all_blocks = []
    for path in filepaths:
        blocks = extract_text_with_structure(path)
        all_blocks.extend(blocks)
    print(f"Extracted {len(all_blocks)} text blocks from {len(filepaths)} PDFs.", flush=True)
    return all_blocks

def extract_text_with_structure(filepath):
    """Extract text from PDF while preserving structure using pdfplumber
    Returns a list of text blocks"""
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