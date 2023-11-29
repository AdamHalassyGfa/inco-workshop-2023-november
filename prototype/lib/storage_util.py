
import sqlite3
import os

SQL_CREATE_STATIONS = """
    CREATE TABLE Stations (
        id INTEGER PRIMARY KEY,
        name TEXT,
        dst_sol DECIMAL(10, 5),
        dst_star DECIMAL(10, 5)
        );
    """

SQL_CREATE_COMMODITIES = """
    CREATE TABLE Commodities (
        id INTEGER PRIMARY KEY,
        name TEXT
        );
    """

SQL_CREATE_PRICES = """
    CREATE TABLE Prices (
        id INTEGER PRIMARY KEY,
        station_id INTEGER,
        commodity_id INTEGER,
        buy_price INTEGER,
        sell_price INTEGER
        );
    """


def build_schema(data_file):
    print("Initializing schema... ")
    if os.path.exists(data_file):
        os.remove(data_file)

    conn = sqlite3.connect(data_file)
    cr = conn.cursor()
    cr.execute(SQL_CREATE_STATIONS)
    cr.execute(SQL_CREATE_COMMODITIES)
    cr.execute(SQL_CREATE_PRICES)

    return conn


def query_data(conn, sql, args):
    cr = conn.cursor()
    cr.execute(sql, args)
    return cr.fetchall()


def query_first(conn, sql, args):
    cr = conn.cursor()
    cr.execute(sql, args)
    data = cr.fetchall()
    return data[0] if len(data) else None


def open_schema(data_file):
    return sqlite3.connect(data_file)


def import_stations(conn, stations):
    print('Importing stations...')
    # stations = map(lambda s: s.replace("\'", "\'\'"), stations)
    # stations = map(lambda s: f"('{s}')", stations)
    # values = ', '.join(stations)
    # sql = f'INSERT INTO Stations (station) VALUES {values};'

    placeholders = ','.join(map(lambda s: '(?, ?, ?)', [key for key in stations]))
    sql = f'INSERT INTO Stations (name, dst_sol, dst_star) VALUES {placeholders};'

    data = []
    for station in stations:
        dst_sol, dst_star = stations[station]
        data.extend([station, dst_sol, dst_star])

    cr = conn.cursor()
    cr.execute(sql, data)
    conn.commit()

    cr = conn.cursor()
    cr.execute('SELECT id, name FROM stations;')

    result = {}
    for id, station in cr.fetchall():
        result[station] = id

    return result


def import_prices(conn, commodities, station_id, station_data):
    names = [key for key in station_data]
    if len(names) == 0:
        return

    placeholders = ','.join(map(lambda s: '(?, ?, ?, ?)', names))
    values = []
    for commodity in names:
        commodity_id = commodities[commodity]
        price_buy, price_sell = station_data[commodity]
        values.extend([station_id, commodity_id, price_buy, price_sell])

    sql = f'INSERT INTO Prices (station_id, commodity_id, buy_price, sell_price) VALUES {placeholders};'

    cr = conn.cursor()
    cr.execute(sql, values)
    conn.commit()


def import_commodities(conn, data):
    print('Importing commodities...')

    commodities = []
    for station in data:
        commodities.extend([key for key in data[station]])

    commodities = list(set(commodities))

    placeholders = ','.join(map(lambda s: '(?)', commodities))
    sql = f'INSERT INTO Commodities (name) VALUES {placeholders};'

    cr = conn.cursor()
    cr.execute(sql, commodities)
    conn.commit()

    cr = conn.cursor()
    cr.execute('SELECT id, name FROM Commodities;')

    result = {}
    for id, station in cr.fetchall():
        result[station] = id

    print('done.')
    return result


def query_commodities(conn):
    cr = conn.cursor()
    cr.execute('SELECT id, name FROM Commodities;')

    result = {}
    for commodity_id, station in cr.fetchall():
        result[station] = commodity_id

    return result


def merge_commodities(conn, data):
    print('Merging commodities...')
    existing = [key for key in query_commodities(conn)]

    commodities = []
    for station in data:
        commodities.extend([key for key in data[station]])

    commodities = list(filter(
        lambda c: c not in existing,
        list(set(commodities))
    ))
    if not len(commodities):
        return query_commodities(conn)

    placeholders = ','.join(map(lambda s: '(?)', commodities))
    sql = f'INSERT INTO Commodities (name) VALUES {placeholders};'

    cr = conn.cursor()
    cr.execute(sql, commodities)
    conn.commit()

    return query_commodities(conn)


def merge_data(conn, data):
    metadata = {}
    marketdata = {}
    for station in data.keys():
        meta, market = data[station]
        metadata[station] = meta
        marketdata[station] = market

    stations = import_stations(conn, metadata)
    commodities = merge_commodities(conn, marketdata)

    print("Importing prices...")
    for station in marketdata.keys():
        import_prices(conn, commodities, stations[station], marketdata[station])


def save_data(data_file, data):
    conn = build_schema(data_file)
    # import_stations(conn, data.keys())
    stations = import_stations(conn, [key for key in data])
    commodities = import_commodities(conn, data)
    for station in data.keys():
        import_prices(conn, commodities, stations[station], data[station])

# eof
