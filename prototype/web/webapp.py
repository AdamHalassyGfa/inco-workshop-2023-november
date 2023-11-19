from bootstrap import app

import common_endpoints
import stations_endpoints

DB_CONNECTION = None


@app.route("/")
def hello_world():
    return "Hello, World!"


if __name__ == '__main__':
    app.run()
