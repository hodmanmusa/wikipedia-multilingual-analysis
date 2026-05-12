import os
import json

from sqlalchemy import create_engine, text


# -----------------------------------
# PATH SETUP
# -----------------------------------

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

PROCESSED_DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "en_processed_articles.json"
)


# -----------------------------------
# DATABASE CONFIG
# -----------------------------------

DB_USER = "postgres"
DB_PASSWORD = "musa"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "wiki-science-analysis"

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)


# -----------------------------------
# LOAD JSON DATA
# -----------------------------------

with open(PROCESSED_DATA_PATH, "r", encoding="utf-8") as file:
    articles = json.load(file)


# -----------------------------------
# SQL QUERIES
# -----------------------------------

get_languages_query = text("""
SELECT id, code
FROM languages
""")

insert_article_query = text("""
INSERT INTO articles (
    wikipedia_page_id,
    language_id,
    language_code,
    title,
    created_at,
    last_updated_at,
    article_length,
    edit_count,
    contributor_count,
    reference_count,
    category_count,
    article_url,
    raw_json_path
)
VALUES (
    :wikipedia_page_id,
    :language_id,
    :language_code,
    :title,
    :created_at,
    :last_updated_at,
    :article_length,
    :edit_count,
    :contributor_count,
    :reference_count,
    :category_count,
    :article_url,
    :raw_json_path
)
ON CONFLICT (
    wikipedia_page_id,
    language_code
)
DO UPDATE SET
    title = EXCLUDED.title,
    created_at = EXCLUDED.created_at,
    last_updated_at = EXCLUDED.last_updated_at,
    article_length = EXCLUDED.article_length,
    edit_count = EXCLUDED.edit_count,
    contributor_count = EXCLUDED.contributor_count,
    reference_count = EXCLUDED.reference_count,
    category_count = EXCLUDED.category_count,
    article_url = EXCLUDED.article_url,
    raw_json_path = EXCLUDED.raw_json_path
RETURNING id
""")

insert_category_query = text("""
INSERT INTO categories (
    canonical_name,
    source_category_name,
    language_code
)
VALUES (
    :canonical_name,
    :source_category_name,
    :language_code
)
ON CONFLICT (
    source_category_name,
    language_code
)
DO UPDATE SET
    canonical_name = EXCLUDED.canonical_name
RETURNING id
""")

insert_article_category_query = text("""
INSERT INTO article_categories (
    article_id,
    category_id
)
VALUES (
    :article_id,
    :category_id
)
ON CONFLICT DO NOTHING
""")


# -----------------------------------
# HELPER FUNCTION
# -----------------------------------

def make_canonical_category_name(category_name):
    return (
        category_name
        .replace("Category:", "")
        .strip()
        .lower()
    )


# -----------------------------------
# LOAD DATA INTO DATABASE
# -----------------------------------

inserted_or_updated_articles = 0
inserted_or_updated_categories = 0
inserted_relationships = 0
skipped_articles = 0

with engine.begin() as connection:

    language_result = connection.execute(get_languages_query)

    language_mapping = {
        row.code: row.id
        for row in language_result
    }

    for article in articles:

        language_code = article.get("language_code")
        language_id = language_mapping.get(language_code)

        if not language_id:
            skipped_articles += 1
            continue

        article_data = {
            "wikipedia_page_id": article.get("wikipedia_page_id"),
            "language_id": language_id,
            "language_code": language_code,
            "title": article.get("title"),
            "created_at": article.get("created_at"),
            "last_updated_at": article.get("last_updated_at"),
            "article_length": article.get("article_length"),
            "edit_count": article.get("edit_count"),
            "contributor_count": article.get("contributor_count"),
            "reference_count": article.get("reference_count"),
            "category_count": article.get("category_count"),
            "article_url": article.get("article_url"),
            "raw_json_path": article.get("raw_json_path")
        }

        article_result = connection.execute(
            insert_article_query,
            article_data
        )

        article_id = article_result.scalar_one()

        inserted_or_updated_articles += 1

        categories = article.get("categories", [])

        for category_name in categories:

            if not category_name:
                continue

            category_data = {
                "canonical_name": make_canonical_category_name(category_name),
                "source_category_name": category_name,
                "language_code": language_code
            }

            category_result = connection.execute(
                insert_category_query,
                category_data
            )

            category_id = category_result.scalar_one()

            inserted_or_updated_categories += 1

            relationship_result = connection.execute(
                insert_article_category_query,
                {
                    "article_id": article_id,
                    "category_id": category_id
                }
            )

            if relationship_result.rowcount == 1:
                inserted_relationships += 1


print("\nLoading completed.")
print(f"Articles inserted/updated: {inserted_or_updated_articles}")
print(f"Categories inserted/updated: {inserted_or_updated_categories}")
print(f"Article-category relationships inserted: {inserted_relationships}")
print(f"Skipped articles: {skipped_articles}")