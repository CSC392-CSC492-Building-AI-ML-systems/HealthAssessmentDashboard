from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from data.Preprocessing.addedParams.utils import initialize_driver, selenium_screenshot

driver = None


def get_noc_data(brand_name: str):
    """Collect all necessary information from the Health Canada NoC Database for a brand_name drug entry:

    - ALL POSSIBLE DINs (TO QUERY Health Canada Drug Database)
    - PARAM #5 (ORIGINAL NOC DATE): Time from NOC to pCPA Engagement / Reimbursement Listing
    - PARAM #8 (SUPPORT ALTERNATIVE): Drug Type (Biologic, Rare Disease, Oncology, etc...) --> Therapeutic Class
    - PARAM #9: Submission Pathway (Standard, Priority, Conditional, etc.)
    """
    global driver

    driver = initialize_driver("https://health-products.canada.ca/noc-ac/newSearch?lang=eng")
    noc_entries = get_noc_row_data(brand_name)

    # print(noc_entries)

    # GET ALL POSSIBLE DINs
    dins = []
    for entry in noc_entries:
        raw_dins = entry["associated_dins"]
        if raw_dins:
            for din in raw_dins.split(","):
                din = din.strip()
                if din and "N/A" not in din.upper() and din not in dins:
                    dins.append(din)

    # USE THE ORIGINAL ENTRY IN NoC DATABASE FOR brand_name DRUG
    original_noc_entry_fields = extract_all_noc_entry_fields(noc_entries[-1]["product_link"])

    # GET PARAM #5 (ORIGINAL NOC DATE): Time from NOC to pCPA Engagement / Reimbursement Listing
    original_noc_date = original_noc_entry_fields["noc_date"]

    # GET PARAM #8 (SUPPORT ALTERNATIVE): Drug Type (Biologic, Rare Disease, Oncology, etc...)
    # --> Therapeutic Class
    therapeutic_class = original_noc_entry_fields["therapeutic_class"]

    # GET PARAM #9. Submission Pathway (Standard, Priority, Conditional, etc.)
    submission_class = original_noc_entry_fields["submission_class"]

    driver.quit()

    return dins, original_noc_date, therapeutic_class, submission_class


def get_noc_row_data(product_name: str):
    """Scrape Health Canada NoC Database for data entries using Selenium"""
    global driver

    search_variants = [product_name]

    print(search_variants, flush=True)

    for variant in search_variants:
        try:
            # TRY TO QUERY BY Product Name
            keyword_input = driver.find_element(By.ID, "productName")

            keyword_input.clear()
            keyword_input.send_keys(variant)

            # driver.save_screenshot(f"before_search_{variant}.png")

            search_button = driver.find_element(By.NAME, "submit")
            search_button.click()

            all_rows = []

            while True:
                print("LOOP")

                try:
                    table = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "wb-auto-4"))
                    )
                    # print(rows.get_attribute("outerHTML"))

                    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
                except:
                    rows = []

                # print(rows)

                # total_height = driver.execute_script("return document.body.scrollHeight")
                # driver.set_window_size(1920, total_height)
                # driver.save_screenshot(f"after_search_{variant}.png")

                all_rows.extend(rows)

                next_buttons = driver.find_elements(By.CSS_SELECTOR, "a.paginate_button.next")
                if next_buttons:
                    next_button = next_buttons[0]
                    print(next_button.get_attribute("outerHTML"))

                    classes = next_button.get_attribute("class")
                    if "disabled" in classes:
                        break
                    else:
                        print("CLICKING...")
                        next_button.click()
                        print("Clicked")
                        if rows:
                            WebDriverWait(driver, 5).until(EC.staleness_of(rows[0]))
                else:
                    break
            print("ALL ROWS", all_rows)
            print("Length of rows:", len(all_rows))

            entries = []

            for i in range(len(rows)):
                row = driver.find_elements(By.CSS_SELECTOR, "#wb-auto-4 tbody tr")[i]
                cells = row.find_elements(By.TAG_NAME, "td")

                if len(cells) >= 6:
                    product_cell = cells[0]
                    product = product_cell.text.strip()
                    product_link = product_cell.find_element(By.TAG_NAME, "a").get_attribute("href")

                    manufacturer = cells[1].text.strip()
                    noc_date = cells[3].text.strip()
                    medicinal_ingredient = cells[4].text.strip()
                    associated_dins = cells[5].text.strip()

                    entries.append({
                        "product": product,
                        "product_link": product_link,
                        "manufacturer": manufacturer,
                        "noc_date": noc_date,
                        "medicinal_ingredient": medicinal_ingredient,
                        "associated_dins": associated_dins
                    })

            return entries

        except Exception as e:
            print(f"Error for variant '{variant}': {e}")
            continue


def extract_all_noc_entry_fields(url: str):
    """Extract structured field information from a Health Canada NoC Database entry page."""
    global driver

    driver.get(url)

    details = driver.find_elements(By.CSS_SELECTOR, "dl dt, dl dd")

    raw_fields = {}
    for i in range(0, len(details), 2):
        key = details[i].text.strip().lower().rstrip(":").rstrip()
        value = details[i + 1].text.strip()
        raw_fields[key] = value

    field_map = {
        "notice of compliance date": "noc_date",
        "manufacturer": "manufacturer",
        "noc with conditions": "noc_with_conditions",
        "submission type": "submission_type",
        "submission class": "submission_class",
        "therapeutic class": "therapeutic_class",
    }

    entry_fields = {v: raw_fields.get(k) for k, v in field_map.items()}

    # Normalize therapeutic_class into a list
    therapeutic = entry_fields.get("therapeutic_class")
    if therapeutic:
        entry_fields["therapeutic_class"] = [t.strip() for t in therapeutic.split(";")]
    else:
        entry_fields["therapeutic_class"] = []

    return entry_fields