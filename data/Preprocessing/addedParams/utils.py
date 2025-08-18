from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def initialize_driver(url: str):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    return driver


def selenium_screenshot(driver, name: str):
    total_height = driver.execute_script("return document.body.scrollHeight")
    driver.set_window_size(1920, total_height)
    driver.save_screenshot(name)


def calculate_time_difference(start_date, end_date):
    """
    Calculates the difference in days between two dates.
    Both dates must be strings in 'YYYY-MM-DD' format.
    """
    if not start_date or not end_date:
        return None  # Handle missing data gracefully

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        return (end - start).days
    except ValueError:
        return None


def classify_drug_type(atc_code: str, active_ingredients: str, dosage_forms: str, indication_text: str = '', noc_pathway: str = '') -> str:
    """
    Classify drug type in Canada using heuristics built from:
    - Health Canada Database Entry Fields
    - NoC Database Entry Fields
    - CDA Document Indication Summary
    """

    biologic_suffixes = ['mab', 'cept', 'kinra', 'fusp', 'tide', 'vaccine', 'gene', 'cell']
    active_parts = active_ingredients.lower().split()
    if any(part.endswith(suffix) for part in active_parts for suffix in biologic_suffixes):
        return "Biologic"

    dosage_parts = dosage_forms.lower().split()
    forms = ['injection', 'infusion', 'vial', 'prefilled syringe']
    if any(part.lower() in forms for part in dosage_parts):
        if any(part.endswith(suffix) for part in active_parts for suffix in ['mab', 'cept', 'kinra', 'fusp', 'tide']):
            return "Biologic"

    rare_keywords = ['rare', 'ultra-rare', 'enzyme replacement', 'lysosomal storage', 'orphan', 'genetic disorder']
    if noc_pathway.lower() in ['priority review', 'conditional noc'] or \
       any(keyword in indication_text.lower() for keyword in rare_keywords):
        return "Rare Disease"

    # IN THE WORST CASE, USE THE ATC PREFIX TO MAP TO A DRUG TYPE
    atc_prefix = atc_code[0].upper() if atc_code else ''
    atc_map = {
        'A': 'Alimentary/Metabolism',
        'B': 'Blood',
        'C': 'Cardiovascular',
        'D': 'Dermatological',
        'G': 'Genito-urinary',
        'H': 'Systemic Hormonal',
        'J': 'Anti-infective',
        'L': 'Oncology/Immunomodulating',
        'M': 'Musculoskeletal',
        'N': 'Nervous System',
        'P': 'Antiparasitic',
        'R': 'Respiratory',
        'S': 'Sensory Organs',
        'V': 'Various'
    }
    return atc_map.get(atc_prefix, 'Other')


