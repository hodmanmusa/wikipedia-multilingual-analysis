import os
import sys
import json

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from config import COMPUTER_SCIENCE_CATEGORIES
from wikipedia_client import WikipediaClient


LANGUAGE_CODE = "en"

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

raw_data_dir = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    LANGUAGE_CODE
)

os.makedirs(raw_data_dir, exist_ok=True)

json_path = os.path.join(
    raw_data_dir,
    "computer_science_articles.json"
)

client = WikipediaClient(LANGUAGE_CODE)

all_articles = []

for category in COMPUTER_SCIENCE_CATEGORIES:
    print(f"\nProcessing {category}")

    articles = client.get_recursive_category_articles(
        category,
        max_depth=1,
        max_categories=20
    )

    all_articles.extend(articles)

unique_articles = {
    article["pageid"]: article
    for article in all_articles
}

all_articles = list(unique_articles.values())

with open(json_path, "w", encoding="utf-8") as file:
    json.dump(
        all_articles,
        file,
        ensure_ascii=False,
        indent=2
    )

print(f"\nTotal Unique Articles: {len(all_articles)}")
print(f"Saved dataset to: {json_path}")

for article in all_articles[:20]:
    print(article["title"])