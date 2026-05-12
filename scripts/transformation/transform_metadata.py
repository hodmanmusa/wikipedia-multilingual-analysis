import os
import sys
import json

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from extraction.wikipedia_client import WikipediaClient


LANGUAGE_CODE = "en"

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

RAW_JSON_PATH = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    LANGUAGE_CODE,
    "computer_science_articles.json"
)

PROCESSED_DIR = os.path.join(
    BASE_DIR,
    "data",
    "processed"
)

os.makedirs(PROCESSED_DIR, exist_ok=True)

OUTPUT_PATH = os.path.join(
    PROCESSED_DIR,
    f"{LANGUAGE_CODE}_processed_articles.json"
)

with open(RAW_JSON_PATH, "r", encoding="utf-8") as file:
    raw_articles = json.load(file)

client = WikipediaClient(LANGUAGE_CODE)

page_ids = [
    article["pageid"]
    for article in raw_articles
]

BATCH_SIZE = 50
processed_articles = []

for i in range(0, len(page_ids), BATCH_SIZE):
    batch_ids = page_ids[i:i + BATCH_SIZE]

    print(f"Processing batch {i // BATCH_SIZE + 1}")

    data = client.get_articles_metadata(batch_ids)

    if not data:
        continue

    pages = data.get("query", {}).get("pages", {})

    for page_id, page_data in pages.items():
        categories = page_data.get("categories", [])
        external_links = page_data.get("extlinks", [])
        revisions = page_data.get("revisions", [])

        last_revision_timestamp = None

        if revisions:
            last_revision_timestamp = revisions[0].get("timestamp")

        article_record = {
            "wikipedia_page_id": page_data.get("pageid"),
            "language_code": LANGUAGE_CODE,
            "title": page_data.get("title"),
            "article_length": page_data.get("length"),
            "category_count": len(categories),
            "reference_count": len(external_links),
            "last_updated_at": last_revision_timestamp,
            "article_url": page_data.get("fullurl"),
            "raw_json_path": RAW_JSON_PATH,
            "categories": [
                category.get("title")
                for category in categories
                if category.get("title")
            ]
        }

        processed_articles.append(article_record)

with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
    json.dump(
        processed_articles,
        file,
        ensure_ascii=False,
        indent=2
    )

print("\nProcessing completed.")
print(f"Processed Articles: {len(processed_articles)}")
print(f"Saved to: {OUTPUT_PATH}")