import os

from flask import Flask, request, jsonify
from lib.data_util import open_schema, query_data

DB_FILE = os.path.abspath('data.db')


app = Flask(__name__)


@app.route('/api/echo')
def echo():
    msg = request.args.get('msg')
    return jsonify({
        "message": msg
    }), 200


@app.route("/api/station")
def list_stations():
    conn = open_schema(DB_FILE)
    data = query_data(conn, "SELECT id, name FROM Stations ORDER BY name")

    data = map(lambda d: {
        "id": d[0],
        "name": d[1]
    }, data)

    return list(data), 200


@app.route("/api/station/<station_id>")
def get_station(station_id):
    conn = open_schema(DB_FILE)
    data = query_data(conn, "SELECT id, name, distance FROM Stations WHERE id = ?;", [station_id])
    if not len(data):
        return {
            "message": "Station was not found."
        }, 404

    id, name, distance = data[0]
    return {
        "id": id,
        "name": name,
        "distance": distance,
    }, 200


if __name__ == '__main__':
    app.run(host="0.0.0.0")

# eof
