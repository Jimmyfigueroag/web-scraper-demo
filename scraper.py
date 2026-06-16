"""
Web scraper demo — product catalog -> clean CSV.

Qué hace:
  - Recorre TODAS las páginas del catálogo (maneja paginación automática).
  - Extrae de cada producto: título, precio, rating, disponibilidad y URL.
  - Reintenta ante errores de red y respeta una pausa entre peticiones (scraping "educado").
  - Guarda todo en un CSV limpio, listo para abrir en Excel/Google Sheets.

Demo apuntada a http://books.toscrape.com (sitio sandbox legal para practicar
scraping). Para un cliente real, solo cambias BASE_URL y la función parse_product().

Uso:
    python scraper.py
    python scraper.py --pages 5 --out mis_datos.csv   # límite de páginas y nombre de salida

Requisitos: pip install -r requirements.txt
Autor: Jimmy Figueroa
"""

import argparse
import csv
import re
import sys
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://books.toscrape.com/catalogue/page-1.html"
REQUEST_DELAY = 0.5          # segundos entre peticiones (no martillar el servidor)
MAX_RETRIES = 3
TIMEOUT = 15
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def fetch(session, url):
    """Descarga una URL con reintentos. Devuelve el HTML o None si falla del todo."""
    for intento in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, headers=HEADERS, timeout=TIMEOUT)
            if resp.status_code == 404:
                return None  # llegamos al final de la paginación
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            espera = intento * 2
            print(f"  ! Error en {url} (intento {intento}/{MAX_RETRIES}): {e}. "
                  f"Reintento en {espera}s...", file=sys.stderr)
            time.sleep(espera)
    print(f"  X Se agotaron los reintentos para {url}", file=sys.stderr)
    return None


def parse_product(article, page_url):
    """Extrae los campos de un producto. Aislado para adaptarlo fácil a otro sitio."""
    titulo = article.h3.a["title"].strip()

    precio_txt = article.select_one("p.price_color").get_text(strip=True)
    m = re.search(r"[\d]+\.?[\d]*", precio_txt)  # toma solo el número, ignora £/$/€
    precio = m.group(0) if m else ""

    rating_clases = article.select_one("p.star-rating")["class"]
    rating = next((RATING_WORDS[c] for c in rating_clases if c in RATING_WORDS), "")

    disponibilidad = article.select_one("p.instock.availability").get_text(strip=True)

    href = article.h3.a["href"]
    url_producto = urljoin(page_url, href)

    return {
        "titulo": titulo,
        "precio": precio,
        "rating_estrellas": rating,
        "disponibilidad": disponibilidad,
        "url": url_producto,
    }


def scrape(max_pages=None):
    """Recorre el catálogo paginado y devuelve la lista de productos."""
    session = requests.Session()
    productos = []
    page_num = 1
    url = BASE_URL

    while url:
        print(f"-> Página {page_num}: {url}")
        html = fetch(session, url)
        if html is None:
            break

        soup = BeautifulSoup(html, "html.parser")
        articles = soup.select("article.product_pod")
        if not articles:
            break

        for article in articles:
            try:
                productos.append(parse_product(article, url))
            except (AttributeError, KeyError, TypeError) as e:
                print(f"  ! Producto omitido (estructura inesperada): {e}",
                      file=sys.stderr)

        if max_pages and page_num >= max_pages:
            break

        # Paginación: buscar el botón "next"
        next_link = soup.select_one("li.next a")
        if next_link:
            url = urljoin(url, next_link["href"])
            page_num += 1
            time.sleep(REQUEST_DELAY)
        else:
            url = None

    return productos


def guardar_csv(productos, ruta):
    """Guarda en CSV con BOM utf-8 para que Excel muestre bien los acentos."""
    if not productos:
        print("No se extrajo ningún producto; no se escribe CSV.", file=sys.stderr)
        return
    campos = ["titulo", "precio", "rating_estrellas", "disponibilidad", "url"]
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(productos)


def main():
    parser = argparse.ArgumentParser(description="Scraper de catálogo -> CSV")
    parser.add_argument("--pages", type=int, default=None,
                        help="Máximo de páginas a recorrer (por defecto: todas)")
    parser.add_argument("--out", default="productos.csv",
                        help="Nombre del archivo CSV de salida")
    args = parser.parse_args()

    inicio = time.time()
    productos = scrape(max_pages=args.pages)
    guardar_csv(productos, args.out)
    dur = time.time() - inicio

    print("\n" + "=" * 50)
    print(f"  Productos extraídos : {len(productos)}")
    if productos:
        precios = [float(p["precio"]) for p in productos if p["precio"]]
        if precios:
            print(f"  Precio mín / máx    : {min(precios):.2f} / {max(precios):.2f}")
            print(f"  Precio promedio     : {sum(precios)/len(precios):.2f}")
    print(f"  Guardado en         : {args.out}")
    print(f"  Tiempo              : {dur:.1f}s")
    print("=" * 50)


if __name__ == "__main__":
    main()
