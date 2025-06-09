import nest_asyncio
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
import os

nest_asyncio.apply()

BASE_URL = "https://www.inesss.qc.ca/en/themes/medicaments/drug-products-undergoing-evaluation-and-evaluated.html?tx_solr[page]={}"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# 5 threads at a time
CONCURRENT_REQUESTS = 5
MAX_PAGES = 1

async def fetch_page(session, page_num):
    url = BASE_URL.format(page_num)
    try:
        async with session.get(url, timeout=60) as response:
            if response.status != 200:
                return page_num, None
            text = await response.text()
            return page_num, text
    except Exception as e:
        return page_num, None

def parse_page(html, page_num):
    soup = BeautifulSoup(html, "html.parser")
    evaluated_tab = soup.select_one("#jfmulticontent_c767-6")
    if not evaluated_tab:
        return []

    table = evaluated_tab.find("table")
    if not table or not table.find("tbody"):
        return []

    rows = table.find("tbody").find_all("tr")
    if not rows:
        return []

    page_data = []
    for row in rows:
        cells = row.find_all("td")
        if len(cells) != 6:
            continue
        page_data.append({
            "Date": cells[0].get_text(strip=True),
            "Trademark / Project": cells[1].get_text(strip=True),
            "Common name / Subject": cells[2].get_text(strip=True),
            "Manufacturer": cells[3].get_text(strip=True),
            "INESSS Recommendation": cells[4].get_text(strip=True),
            "Minister's Decision": cells[5].get_text(strip=True),
        })
    return page_data

async def scrape_all_pages():

    # Prevents duplicate pages
    visited_pages = set()

    connector = aiohttp.TCPConnector(limit=CONCURRENT_REQUESTS)
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(headers=HEADERS, connector=connector, timeout=timeout) as session:
        all_data = []
        for batch_start in range(0, MAX_PAGES, CONCURRENT_REQUESTS):
            tasks = [fetch_page(session, i) for i in range(batch_start, batch_start + CONCURRENT_REQUESTS)]
            responses = await asyncio.gather(*tasks)

            # Iterate through pages
            for page_num, html in sorted(responses):
                if html is None:
                    continue
                
                if page_num in visited_pages:
                    continue
                visited_pages.add(page_num)

                page_data = parse_page(html, page_num)
                if not page_data:
                    return all_data
                
                # Add to data
                all_data.extend(page_data)

        return all_data

if __name__ == "__main__":
    scraped_data = asyncio.run(scrape_all_pages())
    df = pd.DataFrame(scraped_data)
    df.to_csv("inesss_data.csv", index=False, encoding="utf-8-sig")

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))

    target_dir = os.path.join(project_root, "Data/Preprocessing/Data/scrapedData/inesssDownloads")
    os.makedirs(target_dir, exist_ok=True)

    output_path = os.path.join(target_dir, "inesss_data.csv")
    df.to_csv(output_path, index=False, encoding="utf-8-sig")