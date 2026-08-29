from pydantic import ValidationError
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pathlib import Path
import requests
import time
from save_run_report import save_run_report
from save_errors import save_errors
from save_books import save_books
from normalize import normalize_book
from schema import Book



# ==============================================
# Project paths
# ==============================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

CACHE_DIR = PROJECT_DIR / "cache"
OUTPUT_DIR = PROJECT_DIR / "output"


# ==============================================
# Run statistics
# ==============================================

RUN_STATS = {
    "pages_fetched": 0,
    "cache_hits": 0,
    "failed_pages": 0
}


# ==============================================
# Configuration
# ==============================================

USER_AGENT = "FlyRankInternshipA9/1.0"
TIMEOUT = 10


# ==============================================
# Fetch page
# ==============================================

def fetch_page(current_url, cache_file):

    # ------------------------------------------
    # Check cache
    # ------------------------------------------

    if cache_file.exists():

        print("CACHE HIT")

        RUN_STATS["cache_hits"] += 1

        html = cache_file.read_text(
            encoding="utf-8"
        )

        print(
            f"Response size = {len(html)} bytes"
        )

        return html

    # ------------------------------------------
    # Fetch from website
    # ------------------------------------------

    print("FETCH")

    headers = {
        "User-Agent": USER_AGENT
    }

    for attempt in range(2):

        try:

            time.sleep(0.5)

            response = requests.get(
                current_url,
                headers=headers,
                timeout=TIMEOUT
            )

            # ----------------------------------
            # Successful response
            # ----------------------------------

            if response.status_code == 200:

                RUN_STATS["pages_fetched"] += 1

                html = response.content.decode(
                    "utf-8"
                )

                CACHE_DIR.mkdir(
                    parents=True,
                    exist_ok=True
                )

                cache_file.write_text(
                    html,
                    encoding="utf-8"
                )

                print(
                    f"Response size: {len(html)} bytes"
                )

                return html

            # ----------------------------------
            # Retry server errors
            # ----------------------------------

            if 500 <= response.status_code <= 599:

                if attempt == 0:

                    print(
                        f"HTTP {response.status_code}. "
                        "Retrying once..."
                    )

                    time.sleep(1)

                    continue

                raise Exception(
                    f"Fetch failed HTTP "
                    f"{response.status_code}"
                )

            # ----------------------------------
            # Do NOT retry 403 or 404
            # ----------------------------------

            if response.status_code in (403, 404):

                raise Exception(
                    f"Fetch failed HTTP "
                    f"{response.status_code}"
                )

            # ----------------------------------
            # Other HTTP errors
            # ----------------------------------

            raise Exception(
                f"Fetch failed HTTP "
                f"{response.status_code}"
            )

        except requests.Timeout:

            if attempt == 0:

                print(
                    "Request timed out. "
                    "Retrying once..."
                )

                time.sleep(1)

                continue

            raise Exception(
                "Fetch failed: timeout after retry"
            )

    raise Exception("Fetch failed")


# ==============================================
# Extract book links
# ==============================================

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


# ==============================================
# Find next catalogue page
# ==============================================

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

    return None


# ==============================================
# Extract book details
# ==============================================

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

    # ------------------------------------------
    # Title
    # ------------------------------------------

    title = product_main.select_one(
        "h1"
    ).get_text(
        strip=True
    )

    # ------------------------------------------
    # Price
    # ------------------------------------------

    price_text = product_main.select_one(
        ".price_color"
    ).get_text(
        strip=True
    )

    # ------------------------------------------
    # Availability
    # ------------------------------------------

    availability_text = product_main.select_one(
        ".availability"
    ).get_text(
        " ",
        strip=True
    )

    # ------------------------------------------
    # Rating
    # ------------------------------------------

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

    # ------------------------------------------
    # Description
    # ------------------------------------------

    description = None

    description_element = soup.select_one(
        "#product_description + p"
    )

    if description_element:

        description = description_element.get_text(
            " ",
            strip=True
        )

    # ------------------------------------------
    # Timestamp
    # ------------------------------------------

    fetched_at = datetime.now(
        timezone.utc
    ).isoformat()

    # ------------------------------------------
    # Raw record
    # ------------------------------------------

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


# ==============================================
# Main
# ==============================================

def main():

    print(
        "Books to scrape-Week:5 Assignment"
    )

    # ------------------------------------------
    # Start run timer
    # ------------------------------------------

    run_start = datetime.now(
        timezone.utc
    )

    start_counter = time.perf_counter()

    # ------------------------------------------
    # Starting catalogue page
    # ------------------------------------------

    current_url = (
        "https://books.toscrape.com/"
        "catalogue/page-1.html"
    )

    catalogue_pages = 0

    # ==========================================
    # Catalogue discovery
    # ==========================================

    discovered_books = []

    while (
        current_url
        and catalogue_pages < 3
    ):

        catalogue_pages += 1

        cache_file = (
            CACHE_DIR
            / f"catalogue-page-{catalogue_pages}.html"
        )

        try:

            html = fetch_page(
                current_url,
                cache_file
            )

            book_urls = extract_book_links(
                html,
                current_url
            )

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

        except Exception as error:

            RUN_STATS["failed_pages"] += 1

            print(
                f"Catalogue page failed: {error}"
            )

            print(
                "Skipping catalogue page..."
            )

            current_url = None

    # ==========================================
    # Discovery results
    # ==========================================

    print()

    print(
        f"catalogue_pages={catalogue_pages}"
    )

    print(
        f"discovered={len(discovered_books)}"
    )

    # ==========================================
    # Deduplicate books
    # ==========================================

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

    # ==========================================
    # Stage 5 failure test
    # ==========================================

    # One fake URL is intentionally added
    # to prove that one bad page does not
    # kill the entire scraper.

    unique_books.append({
        "product_url":
            "https://books.toscrape.com/"
            "catalogue/fake-book-for-stage-5.html",

        "source_page": "stage-5-test"
    })

    # ==========================================
    # Process books
    # ==========================================

    records = []
    errors = []

    for index, book in enumerate(
        unique_books,
        start=1
    ):

        print()

        print(
            f"Processing book "
            f"{index}/{len(unique_books)}"
        )

        book_cache_file = (
            CACHE_DIR
            / f"book-{index}.html"
        )

        try:

            # ----------------------------------
            # Fetch
            # ----------------------------------

            book_html = fetch_page(
                book["product_url"],
                book_cache_file
            )

            # ----------------------------------
            # Extract
            # ----------------------------------

            book_record = extract_book_details(
                book_html,
                book["product_url"],
                book["source_page"]
            )

            # ----------------------------------
            # Normalize
            # ----------------------------------

            book_record = normalize_book(
                book_record
            )

            # ----------------------------------
            # Validate
            # ----------------------------------

            validated_book = Book(
                **book_record
            )

            records.append(
                validated_book
            )

            print(
                f"Book {index} processed successfully."
            )

        except ValidationError as error:

            errors.append({
                "record": book_record,
                "error": str(error)
            })

            print(
                f"Validation failed for book {index}"
            )

        except Exception as error:

            RUN_STATS["failed_pages"] += 1

            print(
                f"Page failed for book {index}: "
                f"{error}"
            )

            print(
                "Skipping page and continuing..."
            )

    # ==========================================
    # Save books
    # ==========================================

    save_books(
        records,
        OUTPUT_DIR
    )

    # ==========================================
    # Save errors
    # ==========================================

    save_errors(
        errors,
        OUTPUT_DIR
    )

    # ==========================================
    # Run report
    # ==========================================

    duration = (
        time.perf_counter()
        - start_counter
    )

    run_report = {
        "start_time":
            run_start.isoformat(),

        "duration_seconds":
            round(duration, 2),

        "pages_fetched":
            RUN_STATS["pages_fetched"],

        "cache_hits":
            RUN_STATS["cache_hits"],

        "valid_records":
            len(records),

        "invalid_records":
            len(errors),

        "failed_pages":
            RUN_STATS["failed_pages"]
    }

    save_run_report(
        run_report,
        OUTPUT_DIR
    )

    # ==========================================
    # Final results
    # ==========================================

    print()

    print(
        "======================================"
    )

    print(
        "RUN COMPLETE"
    )

    print(
        "======================================"
    )

    print(
        f"Valid records   : {len(records)}"
    )

    print(
        f"Invalid records : {len(errors)}"
    )

    print(
        f"Failed pages    : "
        f"{RUN_STATS['failed_pages']}"
    )

    print(
        f"Cache hits      : "
        f"{RUN_STATS['cache_hits']}"
    )

    print(
        f"Pages fetched   : "
        f"{RUN_STATS['pages_fetched']}"
    )

    print(
        f"Duration        : "
        f"{round(duration, 2)} seconds"
    )

    print(
        "======================================"
    )


# ==============================================
# Run program
# ==============================================

if __name__ == "__main__":
    main()

