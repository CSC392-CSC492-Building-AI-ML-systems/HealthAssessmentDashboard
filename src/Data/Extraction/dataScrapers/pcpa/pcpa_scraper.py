import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL
url = "https://www.pcpacanada.ca/negotiations"
headers = {"User-Agent": "Mozilla/5.0"}

# GET request
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Find the table by ID
table = soup.find("table", {"id": "datatable"})

rows = table.tbody.find_all("tr")
data = []

# Iterate through each drug in the table
for row in rows:
    cells = row.find_all("td")
    if len(cells) == 4:
        product = cells[0].get_text(strip=True)
        manufacturer = cells[1].get_text(strip=True)
        status = cells[2].get_text(strip=True)
        indication = cells[3].get_text(strip=True)

        data.append(
            {
                "Product": product,
                "Manufacturer": manufacturer,
                "Status": status,
                "Indication": indication,
            }
        )

# Convert to a pandas DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("pcpa_data.csv", index=False, encoding="utf-8")
