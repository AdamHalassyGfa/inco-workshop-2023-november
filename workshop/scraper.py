
import os

from lib.scraper_util import scrape_stations
from lib.data_util import build_schema, import_stations

DB_FILE = os.path.abspath('data.db')

if __name__ == '__main__':
    data = scrape_stations()
    conn = build_schema(DB_FILE)
    import_stations(conn, data)

# eof
