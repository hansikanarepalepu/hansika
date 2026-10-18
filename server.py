"""Open-source dashboard. Run: python server.py  ->  http://127.0.0.1:5000"""
import os
from flask import Flask, jsonify, render_template
from core import scoring

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/api/stats")
def api_stats():
    return jsonify(scoring.stats())


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", 5000)))
