import os
import json
import sys

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

with open(
    PROCESSED_DATA_PATH,
    "r",
    encoding="utf-8"
) as file:

    articles = json.load(file)


# -----------------------------------
# LOAD LANGUAGE IDS
# -----------------------------------

with engine.connect() as connection:

    language_result = connection.execute(
        text(
            "SELECT id, code FROM languages"
        )
    )

    language_mapping = {
        row.code: row.id
        for row in language_result
    }


# -----------------------------------
# INSERT ARTICLES
# -----------------------------------

insert_query = text("""
INSERT INTO articles (

    wikipedia_page_id,
    language_id,
    language_code,
    title,
    article_length,
    category_count,
    reference_count,
    last_updated_at,
    article_url

)

VALUES (

    :wikipedia_page_id,
    :language_id,
    :language_code,
    :title,
    :article_length,
    :category_count,
    :reference_count,
    :last_updated_at,
    :article_url

)

ON CONFLICT (
    wikipedia_page_id,
    language_code
)

DO NOTHING
""")


inserted_count = 0


with engine.begin() as connection:

    for article in articles:

        language_code = article["language_code"]

        language_id = language_mapping.get(
            language_code
        )

        if not language_id:
            continue

        article["language_id"] = language_id

        connection.execute(
            insert_query,
            article
        )

        inserted_count += 1


print(f"\nInserted Articles: {inserted_count}")