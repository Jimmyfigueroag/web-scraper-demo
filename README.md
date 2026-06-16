# Web Scraper → Clean CSV (Python)

A small, production-style web scraper that crawls a paginated product catalog and
exports clean, structured data to CSV — ready to open in Excel or Google Sheets.

This is a portfolio demo pointed at [books.toscrape.com](http://books.toscrape.com)
(a public sandbox site made for practicing scraping). The exact same code adapts to
a real client site by changing `BASE_URL` and the `parse_product()` function.

## What it does

- **Automatic pagination** — follows "next" links until the last page.
- **Structured extraction** — title, price, star rating, availability, product URL.
- **Resilient** — retries on network errors with backoff; skips malformed items
  instead of crashing.
- **Polite scraping** — sets a real User-Agent and waits between requests.
- **Excel-friendly output** — UTF-8 CSV (with BOM) so accents render correctly.
- **Quick stats** — prints count and min/max/average price after each run.

## Sample output

```
titulo,precio,rating_estrellas,disponibilidad,url
A Light in the Attic,51.77,3,In stock,http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
Tipping the Velvet,53.74,1,In stock,http://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html
```

```
==================================================
  Productos extraídos : 100
  Precio mín / máx    : 10.16 / 58.11
  Precio promedio     : 34.56
  Guardado en         : productos.csv
  Tiempo              : 3.4s
==================================================
```

## Run it

```bash
pip install -r requirements.txt

python scraper.py                          # scrape everything
python scraper.py --pages 5 --out data.csv # limit pages, custom output file
```

## Adapt it to your site

1. Point `BASE_URL` at the catalog you need.
2. Update the CSS selectors inside `parse_product()` for the fields you want.
3. Add an export step if needed (Google Sheets, a database, an API push).

Need a scraper, API integration, or automation built for your use case?
I deliver clean, documented Python you own, with fast turnaround. — **Jimmy Figueroa**
