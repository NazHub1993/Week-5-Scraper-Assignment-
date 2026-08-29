# Books Scraper — Week 5 Assignment

A Python web scraper for **Books to Scrape** that discovers books from catalogue pages, extracts book details, normalizes prices, validates records with Pydantic, handles failures gracefully, and saves structured JSON output.

---

## 1. Stage 0 — Target Classification

**Target:** Books to Scrape

**Target classification:** Public website / publicly accessible HTML data.

The scraper collects only the book information required by the assignment from publicly accessible catalogue and product pages.

---

## 2. Project Structure

```text
scraper/
│
├── src/
│   ├── main.py
│   ├── normalize.py
│   ├── schema.py
│   ├── save_books.py
│   ├── save_errors.py
│   └── save_run_report.py
│
├── output/
│   ├── books.json
│   ├── errors.json
│   └── run-report.json
│
├── requirements.txt
├── README.md
└── .gitignore
```

The `cache/` directory is intentionally excluded from Git because cached HTML files can become large and are not required in the repository.

---

## 3. Features

The scraper currently supports:

* Catalogue page discovery
* Book URL extraction
* Pagination
* Duplicate URL removal
* HTML response caching
* Book detail extraction
* Price normalization
* Pydantic validation
* Validation error handling
* Page-level failure handling
* Retry for timeouts and server errors
* No retry for `403` and `404`
* Run statistics
* JSON output
* Run report generation

---

## 4. Clone the Repository

Clone the repository:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git
```

Move into the project:

```bash
cd YOUR_REPO_NAME
```

---

## 5. Installation

Make sure Python 3.10+ is installed.

Create a virtual environment:

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## 6. Run the Scraper

Run the scraper with:

```bash
python src/main.py
```

The scraper will discover the configured catalogue pages, fetch and process the books, validate the records, and generate the output files.

The main output files are:

```text
output/
├── books.json
├── errors.json
└── run-report.json
```

---

## 7. Record Schema

Every valid book record follows the Pydantic `Book` schema:

```text
Book
├── title               → string
├── product_url         → valid URL
├── price_text          → string
├── price_gbp           → float
├── availability_text   → string
├── rating_text         → string or null
├── description         → string or null
├── source_page         → valid URL
└── fetched_at          → string
```

The raw extracted record is normalized before validation.

For example:

```text
"£51.77"
```

is normalized into:

```text
51.77
```

for the `price_gbp` field.

Invalid records are not added to `books.json`. They are recorded in `errors.json`.

---

## 8. Data Processing Pipeline

The scraper follows this pipeline:

```text
Catalogue pages
      ↓
Discover book URLs
      ↓
Remove duplicates
      ↓
Fetch book pages
      ↓
Extract raw data
      ↓
Normalize data
      ↓
Validate with Pydantic
      ↓
Separate valid / invalid records
      ↓
Write JSON output
      ↓
Write run report
```

---

## 9. Failure Handling

One failed page must not stop the entire run.

Each book page is processed independently.

If a page fails:

```text
Failed page
    ↓
Log failure
    ↓
Skip page
    ↓
Continue processing
```

The successful records remain available.

### Retry rules

The scraper retries a request **once** when:

* A request times out
* The server returns a `5xx` error

The scraper does **not** retry:

* `403 Forbidden`
* `404 Not Found`

A `403` means the server has denied the request, while a `404` means the requested page does not exist.

---

## 10. Politeness Rules

The scraper follows several basic politeness rules:

### User-Agent

The scraper identifies itself using:

```text
FlyRankInternshipA9/1.0
```

### Request delay

A short delay is used between requests:

```text
0.5 seconds
```

### Timeout

Requests use a:

```text
10 second timeout
```

### Cache

Previously downloaded pages are stored locally in the `cache/` directory.

If a cached page exists, it is reused instead of making another request.

The cache directory is excluded from Git using `.gitignore`.

### Retry

Only temporary failures are retried:

```text
Timeout → retry once
5xx     → retry once
403     → no retry
404     → no retry
```

---

## 11. Run Report

Every scraper execution produces:

```text
output/run-report.json
```

The report records:

* Start time
* Run duration
* Pages fetched
* Cache hits
* Valid records
* Invalid records
* Failed pages

### Sample Run Report

The following is an example of an actual run report:

```json
{
  "start_time": "2026-08-29T10:30:00+00:00",
  "duration_seconds": 15.42,
  "pages_fetched": 3,
  "cache_hits": 60,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1
}
```

> Replace the values above with the contents of your actual `output/run-report.json` before submitting the repository.

The purpose of the report is to make the scraper's result observable instead of allowing failures to happen silently.

---

## 12. Why No Browser Is Needed

This assignment does not require a browser because the required book data is already present in the HTML sent by the server.

A browser would only add unnecessary cost and complexity.

The scraper can directly request and parse the HTML using Python.

---

## 13. Limitation

One limitation of this implementation is that it currently processes only the first **three catalogue pages** rather than the entire Books to Scrape catalogue.

This keeps the assignment run small and predictable.

---

## 14. Ethics

This scraper is designed to collect only the data needed for the assignment from publicly accessible pages.

When scraping websites:

* Use an official API when one exists.
* Never bypass logins, paywalls, access controls, or website blocks.
* Collect only the data that is actually needed.
* Identify the scraper with an appropriate User-Agent.
* Use reasonable delays between requests.
* Avoid unnecessary repeated requests by using caching.

Scraping should respect the website, its resources, and its access policies.

---

## 15. Output

After running:

```bash
python src/main.py
```

the scraper produces:

### `books.json`

Contains successfully validated book records.

### `errors.json`

Contains records that could not be validated or processed successfully.

### `run-report.json`

Contains statistics describing the execution.

Example:

```text
output/
├── books.json
├── errors.json
└── run-report.json
```

---

## 16. Reproducibility

A new user should be able to reproduce the result with:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

The scraper then generates:

```text
output/books.json
output/errors.json
output/run-report.json
```

The repository intentionally does not include the cached HTML pages.

---

## 17. Stage 6 Checkpoint

The project is considered complete when a new user can:

1. Clone the repository.
2. Install the dependencies.
3. Run the documented command.
4. Obtain `books.json`.
5. Obtain `run-report.json`.
6. Understand how the scraper works from the README.

The project also contains meaningful Git commits for the different assignment stages.

---

## Author

**Nasrin Anwar**

Week 5 — Scraper Assignment
