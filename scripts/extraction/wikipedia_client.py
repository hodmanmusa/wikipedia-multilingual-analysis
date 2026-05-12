import requests
import time


class WikipediaClient:

    def __init__(self, language_code):
        self.language_code = language_code
        self.base_url = f"https://{language_code}.wikipedia.org/w/api.php"

    def make_request(self, params, retries=3):

        for attempt in range(retries):

            try:
                headers = {
                    "User-Agent": "WikipediaResearchBot/1.0 (Academic Research Project)"
                }

                response = requests.get(
                    self.base_url,
                    params=params,
                    headers=headers,
                    timeout=30
                )

                response.raise_for_status()
                
                time.sleep(1)

                return response.json()

            except Exception as e:

                print(f"Request failed: {e}")

                if "429" in str(e):
                    print("Rate limited. Sleeping for 10 seconds...")
                    time.sleep(10)

                if attempt < retries - 1:
                    time.sleep(2)

        return None
    
    def is_relevant_subcategory(self, category_title):
        excluded_keywords = [
            "by country",
            "by nationality",
            "magazines",
            "people",
            "organizations",
            "institutes",
            "universities",
            "companies",
            "awards",
            "history",
            "stub",
            "templates"
        ]

        title_lower = category_title.lower()

        for keyword in excluded_keywords:
            if keyword in title_lower:
                return False

        return True
    

    def is_relevant_article(self, article_title):

        excluded_keywords = [
            "list of",
            "outline of",
            "glossary of",
            "index of",
            "template:",
            "portal:",
            "stub",
            "(disambiguation)",
            "awards",
            "magazine",
            "conference",
            "journal",
            "organization",
            "society",
            "museum",
            "history of",
            "timeline of"
        ]

        excluded_exact_patterns = [
            "algorithmic puzzles",
            "the algorithm auction"
        ]

        title_lower = article_title.lower()

        for keyword in excluded_keywords:
            if keyword in title_lower:
                return False

        for pattern in excluded_exact_patterns:
            if pattern == title_lower:
                return False

        return True
    
    def get_category_articles(self, category_name, limit=500):

        articles = []

        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": category_name,
            "cmlimit": limit,
            "format": "json"
        }

        while True:

            data = self.make_request(params)

            if not data:
                break

            members = data.get("query", {}).get("categorymembers", [])

            articles.extend(members)

            if "continue" in data:
                params.update(data["continue"])
            else:
                break

        return articles
    
    def get_recursive_category_articles(
            self,
        category_name,
        max_depth=2,
        visited_categories=None,
        category_counter=None,
        max_categories=50
    ):
        if category_counter is None:
            category_counter = {"count": 0}

        if visited_categories is None:
            visited_categories = set()

        if category_name in visited_categories:
            return []

        visited_categories.add(category_name)

        if category_counter["count"] >= max_categories:
            return []
        category_counter["count"] += 1

        print(f"Crawling: {category_name}")

        articles = []

        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": category_name,
            "cmlimit": 500,
            "format": "json"
        }

        while True:

            data = self.make_request(params)

            if not data:
                break

            members = data.get("query", {}).get(
                "categorymembers",
                []
            )

            for member in members:

                namespace = member.get("ns")

                # ARTICLE
                if namespace == 0 and self.is_relevant_article(member["title"]):
                    articles.append(member)

                # SUBCATEGORY
                elif (
                    namespace == 14
                    and max_depth > 0
                    and self.is_relevant_subcategory(member["title"])
                ):
                    sub_articles = self.get_recursive_category_articles(
                        member["title"],
                        max_depth=max_depth - 1,
                        visited_categories=visited_categories,
                        category_counter=category_counter,
                        max_categories=max_categories
                    )

                    articles.extend(sub_articles)

            if "continue" in data:
                params.update(data["continue"])
            else:
                break

        return articles
        
    def get_articles_metadata(self, page_ids):

        page_ids_string = "|".join(
            str(page_id)
            for page_id in page_ids
        )

        params = {
            "action": "query",

            "prop": "info|revisions|categories|extlinks",

            "inprop": "url",

            "rvprop": "timestamp",

            "cllimit": "max",

            "pageids": page_ids_string,

            "format": "json"
        }

        data = self.make_request(params)

        return data
