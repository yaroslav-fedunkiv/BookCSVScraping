# Static Scraper & Clean CSV

A demo Python scraper for [books.toscrape.com](https://books.toscrape.com/) that walks through 5 pages of pagination, visits each book's detail page, and saves the collected data to a clean UTF-8 CSV file.

## What it demonstrates

| Topic | Details |
|-------|---------|
| **CSS selectors** | `select()`, `select_one()`, sibling selector `~` |
| **Pagination** | URL template `page-{n}.html`, loop over N pages |
| **Detail page scraping** | Follows each book link to extract the full description |
| **Error handling** | `Try-Except` for `HTTPError`, `ConnectionError`, `Timeout`; broken cards are skipped without crashing |
| **Text cleaning** | `re.sub(r"\s+", " ", text).strip()` collapses all whitespace |
| **Clean CSV output** | `pandas` + `encoding="utf-8-sig"` (UTF-8 with BOM, opens correctly in Excel) |

## Stack

- Python 3.10+
- `requests` — HTTP client
- `beautifulsoup4` — HTML parsing
- `pandas` — DataFrame & CSV export
- `lxml` — fast HTML parser (optional fallback)

## Project structure

```
CleanCSVScraping/
├── scraper.py          # main script
├── requirements.txt    # pinned dependencies
├── books_scraped.csv   # output (generated on run)
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python scraper.py
```

The script prints progress to the console and writes `books_scraped.csv` in the same directory when done.

## Output columns

| Column | Example |
|--------|---------|
| `title` | A Light in the Attic |
| `price` | £51.77 |
| `availability` | In stock |
| `rating` | Three |
| `description` | It's hard to imagine a world without... |

## Configuration

Edit the constants at the top of `scraper.py`:

| Constant | Default | Description |
|----------|---------|-------------|
| `PAGES_TO_SCRAPE` | `5` | Number of catalogue pages to scrape |
| `REQUEST_DELAY` | `0.3` | Seconds to wait between requests |
| `OUTPUT_FILE` | `books_scraped.csv` | Output file path |

## How pagination works

The catalogue URL follows a predictable pattern:

```
https://books.toscrape.com/catalogue/page-1.html
https://books.toscrape.com/catalogue/page-2.html
...
```

The script iterates `range(1, PAGES_TO_SCRAPE + 1)` and formats the URL for each page. On real-world sites, look for a "Next" button and follow its `href` instead.

## Error handling strategy

```
get_soup()              ← catches network/HTTP errors, returns None
parse_listing_page()    ← wraps each card in try/except, skips broken ones
parse_detail_page()     ← calls get_soup(), returns "" if page is unavailable
```

If a single page or card fails, the rest of the run continues unaffected.
