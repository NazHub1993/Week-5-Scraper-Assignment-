import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# URL = "https://books.toscrape.com/catalogue/page-1.html"

PROJECT_DIR = Path(__file__).resolve().parent.parent

CACHE_DIR = PROJECT_DIR / "cache"
# CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"

USER_AGENT = "FlyRankInternshipA9/1.0"
TIMEOUT = 60

def fetch_page(current_url,cache_file):

    #checking if cache exists
    if cache_file.exists():

        print("CACHE HIT")
        html=cache_file.read_text(encoding="utf-8")
        print(f"Response size = {len(html)} bytes")
        return html


    print("FETCH")

    headers={
        "User-Agent":USER_AGENT
    }

    response=requests.get(
        current_url,
        headers=headers,
        timeout=TIMEOUT
    )

    if response.status_code!=200:
        raise Exception(
            f"Fetch Failed HTTP {response.status_code}"
        )

    html=response.text

    CACHE_DIR.mkdir(parents=True,exist_ok=True)
    #save html to cache

    cache_file.write_text(
        html,
        encoding="utf-8"
    )

    print(f"Response size: {len(html)} bytes")

    return html


def extract_book_links(html,page_url):

    soup=BeautifulSoup(html,"html.parser")
    book_urls=[]

    for article in soup.select("article.product_pod"):

        link=article.select_one("h3 a")
        if link:
            href=link.get("href")

            if href:
                absolute_url=urljoin(page_url,href)
                book_urls.append(absolute_url)
    return book_urls


def get_next_page(html,page_url):

    soup=BeautifulSoup(html,"html.parser")
    next_link=soup.select_one("li.next a")

    if next_link:
        href=next_link.get("href")

        if href:
            return urljoin(page_url,href)







def main():
    print("Books to scrape-Week:5 Assignment")
    current_url = "https://books.toscrape.com/catalogue/page-1.html"

    catalogue_pages=0
    all_book_url=[]

    while current_url and catalogue_pages<3:

        catalogue_pages+=1

        # Create cache filename
        cache_file = (
            CACHE_DIR /
            f"catalogue-page-{catalogue_pages}.html"
        )


        html=fetch_page(current_url,cache_file)

        book_urls=extract_book_links(html,current_url)

        all_book_url.extend(book_urls)

        print(f"page-{catalogue_pages}={len(book_urls)} number books")

        if catalogue_pages<3:

            current_url=get_next_page(html,current_url)

    print()
    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(all_book_url)}")
        

if __name__=="__main__":
    main()