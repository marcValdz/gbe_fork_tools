# top_owners.py
import os
import requests
from lxml import html


def scrape_top_owner_ids():
    url = "https://steamladder.com/ladder/games/"
    response = requests.get(url)
    response.raise_for_status()
    tree = html.fromstring(response.content)
    # Use a relative XPath to target <a> tags in the second table cell
    links = tree.xpath("//table/tbody/tr/td[2]/a/@href")
    user_ids = []
    for link in links:
        parts = [s for s in link.split('/') if s]
        if parts:
            try:
                user_id = int(parts[-1])
                user_ids.append(user_id)
            except ValueError:
                # Skip links where the last part isn't a valid integer
                pass
    # Remove duplicates while preserving order
    return list(dict.fromkeys(user_ids))


# Check if the file exists. If so, load TOP_OWNER_IDS from it.
FILE_PATH = "top_owners_ids.txt"
if os.path.exists(FILE_PATH):
    with open(FILE_PATH, "r") as file:
        TOP_OWNER_IDS = [int(line.strip()) for line in file if line.strip()]
else:
    # If the file doesn't exist, scrape and write the IDs to the file.
    TOP_OWNER_IDS = scrape_top_owner_ids()
    with open(FILE_PATH, "w") as file:
        for uid in TOP_OWNER_IDS:
            file.write(f"{uid}\n")

    print("TOP_OWNER_IDS =", TOP_OWNER_IDS)
