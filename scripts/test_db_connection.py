from sqlalchemy import create_engine

DB_USER = "postgres"
DB_PASSWORD = "musa"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "wiki-science-analysis"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        print("Database connection successful!")
except Exception as e:
    print("Connection failed:")
    print(e)