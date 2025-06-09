from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import shutil


def setup_driver(download_dir):
    chrome_options = Options()
    chrome_options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        },
    )
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)


def scrape_all_csv(download_dir, base_url="https://www.cda-amc.ca/find-reports"):
    driver = setup_driver(download_dir)
    driver.get(base_url)
    page = 0

    while True:
        print(f"Processing page {page}...")

        try:  # Export CSV
            export_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.export-link"))
            )
            driver.execute_script("arguments[0].click();", export_button)

            timeout = 20
            while timeout > 0:
                if any(
                    f.startswith("page_") and f.endswith(".csv")
                    for f in os.listdir(download_dir)
                ):
                    break
                time.sleep(1)
                timeout -= 1

            downloaded_file = max(
                [os.path.join(download_dir, f) for f in os.listdir(download_dir)],
                key=os.path.getctime,
            )
            new_filename = os.path.join(download_dir, f"page_{page}.csv")
            shutil.move(downloaded_file, new_filename)

        except Exception as e:
            print(f"Failed to download CSV on page {page}: {e}")

        try:  # Next page
            next_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@title="Go to next page"]'))
            )
            next_btn.click()
            page += 1
            time.sleep(3)
        except:
            print("No more pages.")
            break

    driver.quit()


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(script_dir, "tmpData/cda_downloads")
    if os.path.exists(download_dir):
        shutil.rmtree(download_dir)
    os.makedirs(download_dir, exist_ok=True)
    scrape_all_csv(download_dir)
