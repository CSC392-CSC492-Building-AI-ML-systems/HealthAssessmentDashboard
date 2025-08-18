from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from data.Preprocessing.addedParams.utils import initialize_driver, selenium_screenshot

driver = None


def get_health_canada_data(dins: list[str]):
    """Collect all necessary information from the Health Canada Drug Database for a DIN drug entry:

        - PARAM #5 (ORIGINAL MARKET DATE): Time from NOC to pCPA Engagement / Reimbursement Listing
        - PARAM #8 (ATC CODE, DOSAGE FORMS): Drug Type (Biologic, Rare Disease, Oncology, etc.)
        """
    global driver

    driver = initialize_driver("https://health-products.canada.ca/dpd-bdpp/search")
    all_health_canada_entry_fields = extract_all_health_canada_entry_fields(dins)
    original_health_canada_entry_fields = all_health_canada_entry_fields[0]

    # PARAM #5 (ORIGINAL MARKET DATE): Time from NOC to pCPA Engagement / Reimbursement Listing
    original_market_date = original_health_canada_entry_fields["original_market_date"]

    # PARAM #8 (ATC CODE, DOSAGE FORMS): Drug Type (Biologic, Rare Disease, Oncology, etc.)
    atc_code = original_health_canada_entry_fields["anatomical_therapeutic_chemical"]
    dosage_forms = original_health_canada_entry_fields["dosage_forms"]

    driver.quit()

    return original_market_date, atc_code, dosage_forms


def extract_all_health_canada_entry_fields(dins: list[str]):
    """Extract structured field information from a Health Canada NoC Database entry page."""
    global driver

    entries = []
    for din in dins:
        driver.get("https://health-products.canada.ca/dpd-bdpp/search")
        try:
            keyword_input = driver.find_element(By.ID, "din")

            keyword_input.clear()
            keyword_input.send_keys(din)

            search_button = driver.find_element(By.CSS_SELECTOR, "input.btn.btn-primary[value='Search']")
            search_button.click()

            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'DIN invalid')]"))
                )
                print("Invalid DIN")

                return {}
            except:
                print("Valid DIN")

                rows = driver.find_elements(By.CSS_SELECTOR, "div.row")

                data = {}
                for row in rows:
                    try:
                        label = row.find_element(By.CSS_SELECTOR, "p.col-sm-4 strong").text.strip().rstrip(":")
                        value = row.find_element(By.CSS_SELECTOR, "p.col-sm-8").text.strip()
                        data[label] = value
                    except:
                        continue

                entry_fields = {
                    "current_status": data.get("Current status"),
                    "current_status_date": data.get("Current status date"),
                    "original_market_date": data.get("Original market date"),
                    "company": data.get("Company"),
                    "dosage_forms": data.get("Dosage form(s)"),
                    "routes_of_administration": data.get("Route(s) of administration"),
                    "number_of_active_ingredients": data.get("Number of active ingredient(s)"),
                    "schedules": data.get("Schedule(s)"),
                    "american_hospital_formulary_service": data.get("American Hospital Formulary Service (AHFS)"),
                    "active_ingredient_group_number": data.get("Active ingredient group (AIG) number"),
                    "anatomical_therapeutic_chemical": data.get("Anatomical Therapeutic Chemical (ATC)")
                }

                entries.append(entry_fields)

        except Exception as e:
            print(f"Error for DIN '{din}': {e}")
            continue

    return entries