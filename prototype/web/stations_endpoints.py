from flask import request
from lib.storage_util import open_schema, query_first, query_data
from lib.app_util import str_to_int

from __main__ import app

import os

DB_PATH = os.path.abspath("data/elite-market-p1.db")


@app.route("/api/station")
def find_stations():
    name = request.args.get('name')
    name = f'%{name}%' if name else None
    dst_min = str_to_int(request.args.get('min'))
    dst_max = str_to_int(request.args.get('max'))
    page = (str_to_int(request.args.get('p')) or 1) - 1
    limit = 20
    offset = page * limit

    conn = open_schema(DB_PATH)
    where = """
        WHERE (? IS NULL OR name like ?)
            AND (? IS NULL OR ? <= dst_sol)
            AND (? IS NULL OR ? >= dst_sol)
    """

    query_records = 'SELECT id, name, dst_sol, dst_star FROM Stations ' + where + f' LIMIT {limit} OFFSET {offset}'
    query_count = 'SELECT count(*) FROM Stations ' + where
    args = [name, name, dst_min, dst_min, dst_max, dst_max]

    count = query_first(conn, query_count, args)[0]
    data = query_data(conn, query_records, args)
    response = map(lambda d: {
        "id": d[0],
        "name": d[1],
        'dst_sol': d[2],
        "dst_star": d[3]
    }, data)
    response = list(response)

    return {
        "bounds": {
            "page": page,
            "limit": limit,
            "total": count,
            "found": len(response)
        },
        "data": response
    }, 200


@app.route("/api/station/<station_id>")
def get_station(station_id):
    conn = open_schema(DB_PATH)
    id, name, dst_sol, dst_star = query_first(
        conn,
        "SELECT id, name, dst_sol, dst_star FROM Stations WHERE id = ?",
        [station_id]
    )

    query_market = """
        SELECT c.name, buy_price, sell_price
        FROM Prices p
        INNER JOIN Commodities c ON c.id = p.commodity_id
        WHERE p.station_id = ?
        ORDER BY c.name
    """
    market = query_data(
        conn,
        query_market,
        [station_id]
    )
    market = map(lambda d: {
        'commodity': d[0],
        'sell_price': d[1],
        'buy_price': d[2]
    }, market)

    return {
        "data": {
            "id": id,
            "name": name,
            "dst_sol": dst_sol,
            "dst_star": dst_star
        },
        "market": list(market)
    }, 200
