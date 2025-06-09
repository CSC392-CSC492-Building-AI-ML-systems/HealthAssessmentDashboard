from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
import time
import re
import ast

# Config
CSV_FILE = "cda_amc_cleaned.csv"
HEADERS = [
    "Title", "Brand Name", "Generic Name", "PDF Links",
    "Therapeutic Area", "Recommendation", "Status",
    "Submission Date", "Recommendation Date", "Project Number"
]

# browser
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://www.cda-amc.ca/find-reports")
time.sleep(5)

with open(CSV_FILE, mode="w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(HEADERS)

    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find("table")
        if not table or not table.tbody:
            print("⚠️ No valid table found.")
            break

        for row in table.tbody.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 10:
                print("⚠️ Skipping incomplete row")
                continue

            try:
                link_tag = cells[0].find("a")
                if link_tag and link_tag.get("href"):
                    slug = re.sub(r"-\d+$", "", link_tag["href"].rstrip("/").split("/")[-1])
                    title = slug.replace("-", " ").strip()
                    # if title has 'details' in it, remove it
                    if "details" in title.lower():
                        title = re.sub(r"details.*", "", title).strip()
                else:
                    title = cells[0].get_text(strip=True)

                brand_name = cells[1].get_text(strip=True)
                generic_name = cells[2].get_text(strip=True)

                # PDF Links:
                pdf_links = []
                for a in cells[3].find_all("a", href=True):
                    link = a["href"].strip()
                    if not link.startswith("http"):
                        link = "https://www.cda-amc.ca" + link
                    pdf_links.append(link)
                pdf_links_str = "; ".join(sorted(set(pdf_links))) if pdf_links else ""

                therapeutic_area = cells[4].get_text(" ", strip=True).replace("\n", " ").strip()
                recommendation = cells[5].get_text(" ", strip=True).replace("\n", " ").strip()

                status = cells[6].get_text(strip=True).capitalize()
                if status.lower() == "completed":
                    status = "Complete"
                elif status.lower() != "complete":
                    continue

                submission_date = cells[7].get_text(strip=True)
                recommendation_date = cells[8].get_text(strip=True) or "N/A"
                project_number = cells[9].get_text(strip=True)

                row_data = [
                    title.strip(),
                    brand_name.strip() if brand_name else "N/A",
                    generic_name.strip() if generic_name else "N/A",
                    pdf_links_str if pdf_links_str else "N/A",
                    therapeutic_area if therapeutic_area else "N/A",
                    recommendation if recommendation else "N/A",
                    status if status else "N/A",
                    submission_date or "N/A",
                    recommendation_date or "N/A",
                    project_number if project_number else "N/A"
                ]

                writer.writerow(row_data)

            except Exception as e:
                print(f"❌ Error parsing row: {e}")
                continue

        try: # next page
            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[rel='next']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(1)
            next_button.click()
            time.sleep(3)
        except Exception as e:
            print("✅ No more pages or next button missing:", repr(e))
            break

driver.quit()
print(f"✅ Scraping finished. Cleaned data saved to: {CSV_FILE}")
