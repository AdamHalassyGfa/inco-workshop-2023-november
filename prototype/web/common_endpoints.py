from flask import Flask, jsonify, request

from __main__ import app


@app.route("/api/echo")
def echo():
    msg = request.args.get('msg')

    return jsonify({
        "message": msg
    }), 200
