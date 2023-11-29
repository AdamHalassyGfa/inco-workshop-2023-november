
import os
import requests
import re

from lxml import html, etree

BASE_URL = 'https://www.edsm.net'
STATIONS_URL = 'en/search/stations/index'
FILTER_URL = 'en/search/stations/index/service/1/sortBy/distanceSol/type/1/type/2/type/3/type/4/type/5/type/6'
CARRIER_REGEX = "^[A-Z0-9]{3}-[A-Z0-9]{3}$"


def query_page(url):
    response = requests.request('GET', url, allow_redirects=True)
    if response.status_code != 200:
        raise IOError(f"Request failed with {response.status_code} response.")

    return response.text


def scrape_stations(page):
    url = f'{BASE_URL}/{FILTER_URL}/p/{page}'
    content = query_page(url)
    tree = html.fromstring(content)
    rows = tree.xpath('//table/tbody/tr')

    result = []
    for row in rows:
        rtree = etree.ElementTree(row)
        has_market = rtree.xpath('//i[@class="fas fa-shopping-cart"]')
        if not has_market:
            continue

        url = rtree.xpath('//td[6]/a')[0].attrib.get('href')
        name = rtree.xpath('//td[2]/a/*/text()')[0]
        if re.match(CARRIER_REGEX, name):
            continue

        dst_sol = fetch_dst(rtree.xpath('//td[7]/text()')[0])
        dst_star = fetch_dst(rtree.xpath('//td[7]/em/text()')[0])
        result.append((name, f'{BASE_URL}/{url}', dst_sol, dst_star))

    next_pages = fetch_next_page(tree)

    return result, next_pages


def fetch_dst(str):
    if str is None:
        return None

    return float(str.strip()[:-3].replace(',', ''))


def fetch_next_page(tree):
    pages = tree.xpath('//li[@class="page-item"]/a[@class="page-link"]/text()')
    result = None
    for n in pages:
        if not re.match("\\s*[\\d,]+\\s*", n):
            continue

        n = int(n.replace(',', ''))
        result = n if not result or result < n else max

    return result


def parse_price(price_text):
    if not price_text:
        return None

    price_text = price_text.strip()
    if '--' == price_text:
        return None

    return int(price_text[:-3].replace(',', ''))


def scrape_market(url):
    content = query_page(url)
    market_rows = html.fromstring(content).xpath('//table/tbody/tr')

    result = {}
    for data_row in market_rows:
        row = etree.ElementTree(data_row)
        commodity = row.xpath('//td[1]/text()')[0].strip()
        price_buy = parse_price(row.xpath('//td[2]/text()')[0])
        price_sell = parse_price(row.xpath('//td[4]/text()')[0].strip())

        result[commodity] = (price_buy, price_sell)

    return result


def scrape_simple(page_callback):
    page = 242
    count = 242

    while page <= count:
        print(f'Fetching stations {page}/{count}...')
        stations, last = scrape_stations(page)
        if last > count:
            print(f"Found {last-count} more pages.")
            count = last

        page += 1

        limit = 0
        data = {}
        idx = 1
        for name, url, dst_sol, dst_star in stations:
            print(f'Fetching market from {name} ({idx}/{len(stations)})...')

            commodities = scrape_market(url)
            data[name] = (dst_sol, dst_star), commodities

            limit -= 1
            if limit == 0:
                break

            idx += 1

        page_callback(data)

# eof
