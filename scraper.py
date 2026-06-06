"""
scraper.py — Demo scraper for https://books.toscrape.com/

What this file demonstrates:
  ✔ CSS selectors (select / select_one)
  ✔ Pagination (5 catalogue pages)
  ✔ Following detail page links for each book
  ✔ Error handling via Try-Except
  ✔ Text cleaning (re.sub)
  ✔ Saving to UTF-8 CSV with pandas

Stack: requests · BeautifulSoup4 · pandas
"""

import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
import pandas as pd


CATALOGUE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
PAGES_TO_SCRAPE = 5      
REQUEST_DELAY   = 0.3   
OUTPUT_FILE     = "books_scraped.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; BooksScraperDemo/1.0)"
}

def get_soup(url: str) -> BeautifulSoup | None:
    """
    Downloads a page by URL and returns a BeautifulSoup object.
    Returns None on any network or HTTP error.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()          
        response.encoding = "utf-8"          
        return BeautifulSoup(response.text, "html.parser")

    except requests.HTTPError as exc:
        print(f"  [HTTP ERROR]  {url}  →  {exc}")
    except requests.ConnectionError:
        print(f"  [CONN ERROR]  Cannot connect: {url}")
    except requests.Timeout:
        print(f"  [TIMEOUT]     Server did not respond: {url}")

    return None

def clean_text(raw: str | None) -> str:
    if not raw:
        return ""
    return re.sub(r"\s+", " ", raw).strip()

def parse_listing_page(soup: BeautifulSoup, page_url: str) -> list[dict]:
    """
    Extracts the list of books from a single catalogue page.
    """
    books: list[dict] = []

    for article in soup.select("article.product_pod"):
        try:
            title_tag  = article.select_one("h3 > a")
            title      = title_tag["title"] if title_tag else ""

            detail_url = (
                urljoin(page_url, title_tag["href"]) if title_tag else ""
            )

            price_tag = article.select_one("p.price_color")
            price     = clean_text(price_tag.text) if price_tag else ""

            avail_tag    = article.select_one("p.availability")
            availability = clean_text(avail_tag.text) if avail_tag else ""

            rating_tag = article.select_one("p.star-rating")
            rating = rating_tag["class"][1] if rating_tag else ""

            books.append({
                "title":        title,
                "price":        price,
                "availability": availability,
                "rating":       rating,
                "_detail_url":  detail_url, 
            })

        except Exception as exc:
            print(f"  [PARSE WARN] Skipped card: {exc}")

    return books

def parse_detail_page(url: str) -> str:
    soup = get_soup(url)
    if soup is None:
        return ""

    try:
        desc_tag = soup.select_one("#product_description ~ p")
        return clean_text(desc_tag.text) if desc_tag else ""
    except Exception as exc:
        print(f"  [DETAIL WARN] {url}: {exc}")
        return ""

def scrape(num_pages: int = PAGES_TO_SCRAPE) -> list[dict]:
    """
    Iterates over num_pages catalogue pages, fetches the detail page
    for each book, and collects all fields into a single list.
    """
    all_books: list[dict] = []

    for page_num in range(1, num_pages + 1):
        page_url = CATALOGUE_URL.format(page_num)

        print(f"\n{'─'*60}")
        print(f"  Page {page_num}/{num_pages}  →  {page_url}")
        print(f"{'─'*60}")

        soup = get_soup(page_url)
        if soup is None:
            print(f"  [SKIP] Page {page_num} unavailable, skipping.")
            continue

        books = parse_listing_page(soup, page_url)
        print(f"  Found {len(books)} books. Fetching details...\n")

        for idx, book in enumerate(books, start=1):
            label = book["title"][:52] + ("…" if len(book["title"]) > 52 else "")
            print(f"    [{idx:>2}/{len(books)}] {label}")
            book["description"] = parse_detail_page(book["_detail_url"])
            time.sleep(REQUEST_DELAY)   # pause between requests to the server

        all_books.extend(books)
        print(f"\n  Total collected: {len(all_books)} books")
        time.sleep(REQUEST_DELAY)

    return all_books

def save_csv(books: list[dict], path: str = OUTPUT_FILE) -> None:
    """
    Saves the list of books to a CSV file.
    """
    if not books:
        print("[ERROR] List is empty — nothing to save.")
        return

    df = pd.DataFrame(books)

    # Remove the internal detail URL column
    df.drop(columns=["_detail_url"], inplace=True, errors="ignore")

    # Final column order
    df = df[["title", "price", "availability", "rating", "description"]]

    df.to_csv(path, index=False, encoding="utf-8-sig")

    print(f"\n{'='*60}")
    print(f"  DONE! Saved {len(df)} rows to '{path}'")
    print(f"{'='*60}")
    print(f"\nDataframe shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst 3 records:")
    print(df.head(3).to_string(index=False))

if __name__ == "__main__":
    books = scrape(num_pages=PAGES_TO_SCRAPE)
    save_csv(books, path=OUTPUT_FILE)
