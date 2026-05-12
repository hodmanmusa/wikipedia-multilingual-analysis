import os
import json

from wikipedia_client import WikipediaClient

client = WikipediaClient("en")

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

json_path = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "en",
    "computer_science_articles.json"
)

with open(json_path, "r", encoding="utf-8") as file:
    articles = json.load(file)

sample_page_ids = [
    article["pageid"]
    for article in articles[:10]
]

data = client.get_articles_metadata(sample_page_ids)

if not data:
    print("No data returned from API")
    exit()

pages = data["query"]["pages"]

for page_id, page_data in pages.items():

    print("\n-------------------")

    print("Title:", page_data.get("title"))
    print("Page ID:", page_data.get("pageid"))
    print("URL:", page_data.get("fullurl"))
    print("Length:", page_data.get("length"))

    categories = page_data.get("categories", [])
    print("Category Count:", len(categories))

    external_links = page_data.get("extlinks", [])
    print("External Links:", len(external_links))

    revisions = page_data.get("revisions", [])

    if revisions:
        print(
            "Last Revision Timestamp:",
            revisions[0].get("timestamp")
        )