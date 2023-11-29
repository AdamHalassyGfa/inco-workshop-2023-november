
import requests

from lxml import html, etree

BASE_URL = "https://www.edsm.net"
SCRAPE_URL = "en/search/stations/index/sortBy/distanceSol/type/1/type/2/type/3/type/4/type/5/type/6"


def scrape_stations():
    url = f"{BASE_URL}/{SCRAPE_URL}"
    response = requests.request('GET', url, allow_redirects=True)

    html_content = response.text
    tree = html.fromstring(html_content)
    row_elements = tree.xpath('//table/tbody/tr')

    result = []
    for row_element in row_elements:
        rtree = etree.ElementTree(row_element)
        has_market = rtree.xpath('//i[@class="fas fa-shopping-cart"]')

        # "truthy" check:
        if not has_market:
            continue

        name = rtree.xpath('//td[2]/a/*/text()')[0]
        url = rtree.xpath('//td[6]/a')[0].attrib.get('href')
        dst_star = float(rtree.xpath('//td[7]/em/text()')[0].strip()[:-3].replace(',', ''))

        result.append((name, url, dst_star))

    return result

# eof
