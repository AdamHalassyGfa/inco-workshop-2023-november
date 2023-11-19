#!/usr/bin/python3

import os

from lib.scraper_util import scrape_simple
from lib.storage_util import build_schema, merge_data

DATA_FILE = os.path.abspath("data/elite-market.db")
DB_CONNECTION = None


def merge_results(data):
    merge_data(DB_CONNECTION, data)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    DB_CONNECTION = build_schema(DATA_FILE)

    data = scrape_simple(merge_results)

# eof
