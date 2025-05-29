from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# Start selenium browser
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://www.cda-amc.ca/find-reports")
time.sleep(5)  # wait for JS to load the table
data = []

while True:
    soup = BeautifulSoup(driver.page_source, "html.parser")

    table = soup.find("table")
    rows = table.tbody.find_all("tr")

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 10:
            print("Incomplete Data")
            continue

        # Drug name
        link = cells[0].find("a")["href"]
        url_slug = link.rstrip("/").split("/")[-1]
        url_slug = re.sub(r"-\d+$", "", url_slug)  
        drug_name = url_slug.replace("-", " ").strip()


        brand_name = cells[1].get_text(strip=True)
        generic_name = cells[2].get_text(strip=True)

        # Extract PDF links
        pdf_links = [a["href"] for a in cells[3].find_all("a", href=True)]

        therapeutic_area = cells[4].get_text(strip=True)
        recommendation = cells[5].get_text(strip=True)

        # Normalizing status values
        status = cells[6].get_text(strip=True)
        if status.lower() == "completed":
            status = "Complete"

        submission_date = cells[7].get_text(strip=True)
        recommendation_date = cells[8].get_text(strip=True)
        project_number = cells[9].get_text(strip=True)

        data.append(
            {
                "Drug Name": drug_name,
                "Brand Name": brand_name,
                "Generic Name": generic_name,
                "PDF Links": pdf_links,
                "Therapeutic Area": therapeutic_area,
                "Recommendation": recommendation,
                "Status": status,
                "Submission Date": submission_date,
                "Recommendation Date": recommendation_date,
                "Project Number": project_number,
            }
        )

    try:
        # Find and click the Next button using XPath targeting the span
        next_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[rel='next']"))
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", next_button
        )
        time.sleep(1)

        next_button.click()
        time.sleep(2)  # wait for table to load
    except Exception as e:
        driver.quit()
        print("Error: ", repr(e))
        break

df = pd.DataFrame(data)
df.to_csv("cda_amc_data.csv", index=False, encoding="utf-8-sig")
