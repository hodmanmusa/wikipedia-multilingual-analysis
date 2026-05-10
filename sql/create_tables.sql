CREATE TABLE IF NOT EXISTS languages (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,

    canonical_name VARCHAR(255) NOT NULL,
    source_category_name VARCHAR(255) NOT NULL,
    language_code VARCHAR(10),

    UNIQUE(source_category_name, language_code)
);

CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,

    wikipedia_page_id BIGINT NOT NULL,

    language_id INTEGER REFERENCES languages(id),
    language_code VARCHAR(10),

    title TEXT NOT NULL,

    created_at TIMESTAMP,
    last_updated_at TIMESTAMP,

    article_length INTEGER,
    edit_count INTEGER,
    contributor_count INTEGER,

    reference_count INTEGER,
    category_count INTEGER,

    article_url TEXT,

    raw_json_path TEXT,

    UNIQUE(wikipedia_page_id, language_code)
);

CREATE TABLE IF NOT EXISTS article_categories (
    article_id INTEGER REFERENCES articles(id),
    category_id INTEGER REFERENCES categories(id),

    PRIMARY KEY(article_id, category_id)
);

INSERT INTO languages (code, name)
VALUES
('en', 'English'),
('de', 'German'),
('tr', 'Turkish'),
('ar', 'Arabic'),
('fa', 'Persian'),
('ps', 'Pashto')
ON CONFLICT (code) DO NOTHING;