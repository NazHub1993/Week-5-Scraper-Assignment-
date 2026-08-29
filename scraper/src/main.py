from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pathlib import Path
import requests
import time




# Project paths
# --------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent

CACHE_DIR = PROJECT_DIR / "cache"


# --------------------------------
# Configuration
# --------------------------------

USER_AGENT = "FlyRankInternshipA9/1.0"
TIMEOUT = 10


# --------------------------------
# Fetch page
# --------------------------------

def fetch_page(current_url, cache_file):

    # Check if cache exists
    if cache_file.exists():

        print("CACHE HIT")

        html = cache_file.read_text(
            encoding="utf-8"
        )

        print(
            f"Response size = {len(html)} bytes"
        )

        return html

    print("FETCH")

    headers = {
        "User-Agent": USER_AGENT
    }
    time.sleep(0.5)

    response = requests.get(
        current_url,
        headers=headers,
        timeout=TIMEOUT
    )

    if response.status_code != 200:
        raise Exception(
            f"Fetch Failed HTTP {response.status_code}"
        )

    # Explicitly decode the response as UTF-8
    html = response.content.decode("utf-8")

    # Create cache directory if it doesn't exist
    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save HTML to cache
    cache_file.write_text(
        html,
        encoding="utf-8"
    )

    print(
        f"Response size: {len(html)} bytes"
    )

    return html


# --------------------------------
# Extract book links
# --------------------------------

def extract_book_links(html, page_url):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    book_urls = []

    for article in soup.select(
        "article.product_pod"
    ):

        link = article.select_one(
            "h3 a"
        )

        if link:

            href = link.get("href")

            if href:

                absolute_url = urljoin(
                    page_url,
                    href
                )

                book_urls.append(
                    absolute_url
                )

    return book_urls


# --------------------------------
# Find next catalogue page
# --------------------------------

def get_next_page(html, page_url):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    next_link = soup.select_one(
        "li.next a"
    )

    if next_link:

        href = next_link.get("href")

        if href:

            return urljoin(
                page_url,
                href
            )


# --------------------------------
# Extract book details
# --------------------------------

def extract_book_details(
    html,
    product_url,
    source_page
):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    product_main = soup.select_one(
        "article.product_page"
    )

    # Title
    title = product_main.select_one(
        "h1"
    ).get_text(
        strip=True
    )

    # Price
    price_text = product_main.select_one(
        ".price_color"
    ).get_text(
        strip=True
    )

    # Availability
    availability_text = product_main.select_one(
        ".availability"
    ).get_text(
        " ",
        strip=True
    )

    # Rating
    rating_element = product_main.select_one(
        "p.star-rating"
    )

    rating_text = None

    if rating_element:

        rating_classes = rating_element.get(
            "class",
            []
        )

        for rating_class in rating_classes:

            if rating_class != "star-rating":

                rating_text = rating_class

                break

    # Description
    description = None

    description_element = soup.select_one(
        "#product_description + p"
    )

    if description_element:

        description = description_element.get_text(
            " ",
            strip=True
        )

    # Fetch timestamp
    fetched_at = datetime.now(
        timezone.utc
    ).isoformat()

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at
    }


# --------------------------------
# Main
# --------------------------------

def main():

    print(
        "Books to scrape-Week:5 Assignment"
    )

    current_url = (
        "https://books.toscrape.com/"
        "catalogue/page-1.html"
    )

    catalogue_pages = 0

    # Each item will contain:
    # product_url
    # source_page
    discovered_books = []

    # --------------------------------
    # Catalogue discovery
    # --------------------------------

    while (
        current_url
        and catalogue_pages < 3
    ):

        catalogue_pages += 1

        # Create catalogue cache filename
        cache_file = (
            CACHE_DIR /
            f"catalogue-page-{catalogue_pages}.html"
        )

        html = fetch_page(
            current_url,
            cache_file
        )

        book_urls = extract_book_links(
            html,
            current_url
        )

        # Store both book URL and
        # the catalogue page where it was found
        for book_url in book_urls:

            discovered_books.append({
                "product_url": book_url,
                "source_page": current_url
            })

        print(
            f"page-{catalogue_pages}="
            f"{len(book_urls)} number books"
        )

        if catalogue_pages < 3:

            current_url = get_next_page(
                html,
                current_url
            )

    # --------------------------------
    # Discovery results
    # --------------------------------

    print()

    print(
        f"catalogue_pages={catalogue_pages}"
    )

    print(
        f"discovered={len(discovered_books)}"
    )

    # --------------------------------
    # Deduplicate books
    # --------------------------------

    unique_books = []

    seen_urls = set()

    for book in discovered_books:

        product_url = book["product_url"]

        if product_url not in seen_urls:

            seen_urls.add(
                product_url
            )

            unique_books.append(
                book
            )

    print(
        f"unique_books={len(unique_books)}"
    )

    # --------------------------------
    # Fetch and extract all books
    # --------------------------------

    records = []

    for index, book in enumerate(
        unique_books,
        start=1
    ):

        print()

        print(
            f"Processing book {index}/60"
        )

        book_cache_file = (
            CACHE_DIR /
            f"book-{index}.html"
        )

        # Fetch book page
        book_html = fetch_page(
            book["product_url"],
            book_cache_file
        )

        # Extract book details
        book_record = extract_book_details(
            book_html,
            book["product_url"],
            book["source_page"]
        )

        records.append(
            book_record
        )

    # --------------------------------
    # Final results
    # --------------------------------

    print()

    print(
        f"detail_pages={len(records)}"
    )

    # --------------------------------
    # Verify source pages
    # --------------------------------

    print()

    print("Source pages:")

    print(
        records[0]["source_page"]
    )

    print(
        records[20]["source_page"]
    )

    print(
        records[40]["source_page"]
    )

    # --------------------------------
    # First complete raw record
    # --------------------------------

    print()

    print(
        "First complete raw record:"
    )

    print(
        records[0]
    )


# --------------------------------
# Run program
# --------------------------------

if __name__ == "__main__":
    main()

