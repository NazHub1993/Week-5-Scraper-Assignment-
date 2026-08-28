import requests
from pathlib import Path

URL = "https://books.toscrape.com/catalogue/page-1.html"

PROJECT_DIR = Path(__file__).resolve().parent.parent

CACHE_DIR = PROJECT_DIR / "cache"
CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"

USER_AGENT = "FlyRankInternshipA9/1.0"
TIMEOUT = 60

def fetch_page():

    #checking if cache exists
    if CACHE_FILE.exists():

        print("CACHE HIT")
        html=CACHE_FILE.read_text(encoding="utf-8")
        print(f"Response size = {len(html)} bytes")
        return html


    print("FETCH")

    headers={
        "User-Agent":USER_AGENT
    }

    response=requests.get(
        URL,
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

    CACHE_FILE.write_text(
        html,
        encoding="utf-8"
    )

    print(f"Response size: {len(html)} bytes")

    return html









def main():
    print("Books to scrape-Week:5 Assignment")
    fetch_page()

if __name__=="__main__":
    main()