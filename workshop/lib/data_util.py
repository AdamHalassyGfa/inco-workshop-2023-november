import os
import sqlite3


SQL_CREATE_STATIONS = """
    CREATE TABLE Stations (
        id INTEGER PRIMARY KEY,
        name TEXT,
        distance DECIMAL(10,5)
    );
    """


def build_schema(db_file):
    if os.path.exists(db_file):
        os.remove(db_file)

    conn = sqlite3.connect(db_file)
    cr = conn.cursor()
    cr.execute(SQL_CREATE_STATIONS)

    return conn


def open_schema(db_file):
    return sqlite3.connect(db_file)


def query_data(conn, sql, arg=None):
    arg = arg or []

    cr = conn.cursor()
    cr.execute(sql, arg)
    return cr.fetchall()


def import_stations(conn, data):
    placeholders = ', '.join(map(lambda _: '(?, ?)', range(0, len(data))))

    sql = f"INSERT INTO Stations (name, distance) VALUES {placeholders};"
    args = []
    for name, url, dist in data:
        args.extend([name, dist])

    cr = conn.cursor()
    cr.execute(sql, args)
    conn.commit()

# eof
