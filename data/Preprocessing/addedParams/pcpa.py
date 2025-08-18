from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from data.Preprocessing.addedParams.utils import initialize_driver, selenium_screenshot

driver = None


def get_pcpa_data(brand_name: str, cda_project_number: str):
    """Collect all necessary information from the pCPA Database for a DIN drug entry:

        - PARAM #5 (pCPA ENGAGEMENT LETTER ISSUED, NEGOTIATION PROCESS CONCLUDED):
        Time from NOC to pCPA Engagement / Reimbursement Listing
        """
    global driver

    driver = initialize_driver("https://www.pcpacanada.ca/negotiations")
    pcpa_entries = get_pcpa_row_data(brand_name)

    # THE pCPA CAN BE INDEXED BY THE SAME PROJECT NUMBER AS CDA, SO FIND THE ENTRY WITH THE MATCHING PROJECT NUMBER
    associated_entry_fields = None
    for entry in pcpa_entries:
        driver.get(entry["product_link"])
        entry_fields = extract_all_pcpa_entry_fields(entry["product_link"])
        print("ENTRY NUMBER", entry_fields["cda_project_number"])
        print("CDA NUMBER", cda_project_number)
        if entry_fields["cda_project_number"] == cda_project_number:
            associated_entry_fields = entry_fields
            break

    if associated_entry_fields:
        print("Successfully found an associated pCPA entry by CDA project number.")

        # PARAM #5 (pCPA ENGAGEMENT LETTER ISSUED): Time from NOC to pCPA Engagement / Reimbursement Listing
        pcpa_engagement_letter_issued = associated_entry_fields["original_market_date"]
        # PARAM #5 (NEGOTIATION PROCESS CONCLUDED): Time from NOC to pCPA Engagement / Reimbursement Listing
        negotiation_process_concluded = associated_entry_fields["original_market_date"]
    else:
        print("Failed to find an associated pCPA entry by CDA project number.")
        pcpa_engagement_letter_issued = None
        negotiation_process_concluded = None

    driver.quit()

    return pcpa_engagement_letter_issued, negotiation_process_concluded


def get_pcpa_row_data(product_name: str):
    """Scrape pCPA Database for data entries using Selenium"""
    global driver

    search_variants = [product_name]

    print(search_variants, flush=True)

    for variant in search_variants:
        try:
            # TRY TO QUERY BY Product Name
            keyword_input = driver.find_element(By.CSS_SELECTOR, "input[type='search'][aria-controls='datatable']")

            keyword_input.clear()
            keyword_input.send_keys(variant)

            selenium_screenshot(driver, "pcpa_search.png")

            rows = []
            try:
                table = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "datatable"))
                )
                # print(rows.get_attribute("outerHTML"))

                rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            except:
                continue

            # print(rows)

            # total_height = driver.execute_script("return document.body.scrollHeight")
            # driver.set_window_size(1920, total_height)
            # driver.save_screenshot(f"after_search_{variant}.png")

            print("ALL ROWS", rows)
            print("Length of rows:", len(rows))

            entries = []

            for i in range(len(rows)):
                cells = rows[i].find_elements(By.TAG_NAME, "td")

                print(cells)

                if len(cells) >= 4:
                    product_cell = cells[0]
                    product = product_cell.text.strip()
                    product_link = product_cell.find_element(By.TAG_NAME, "a").get_attribute("href")

                    manufacturer = cells[1].text.strip()
                    status = cells[2].text.strip()
                    indication = cells[3].text.strip()

                    entries.append({
                        "product": product,
                        "product_link": product_link,
                        "manufacturer": manufacturer,
                        "status": status,
                        "indication": indication
                    })

            return entries

        except Exception as e:
            print(f"Error for variant '{variant}': {e}")
            continue


def extract_all_pcpa_entry_fields(url: str):
    """Extract structured field information from a pCPA Database entry page."""
    global driver

    driver.get(url)

    table = driver.find_element(By.CSS_SELECTOR, "div.views-view-grid.vertical.cols-1.clearfix.col > div > div")

    print("TABLE")
    print(table)

    entry_fields = {}

    entry_fields["pcpa_file_number"] = table.find_element(By.CSS_SELECTOR,
                                                          "div.views-field-nid span.field-content").text.strip()
    entry_fields["negotiation_status"] = table.find_element(By.CSS_SELECTOR,
                                                            "div.views-field-field-status div.field-content").text.strip()
    entry_fields["indications"] = table.find_element(By.CSS_SELECTOR,
                                                     "div.views-field-field-indication-txt div.field-content").text.strip()
    entry_fields["manufacturer"] = table.find_element(By.CSS_SELECTOR,
                                                      "div.views-field-field-manufacturer-name div.field-content").text.strip()
    entry_fields["cda_project_number"] = table.find_element(By.CSS_SELECTOR,
                                                            "div.views-field-field-cadth-project-id div.field-content").text.strip()
    entry_fields["pcpa_engagement_letter_issued"] = table.find_element(
        By.CSS_SELECTOR,
        "div.views-field-field-engagement-date div.field-content"
    ).text.strip()
    entry_fields["negotiation_process_concluded"] = table.find_element(By.CSS_SELECTOR,
                                                                       "div.views-field-field-close-date time").get_attribute(
        "datetime").strip()

    return entry_fields
