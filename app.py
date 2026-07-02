import csv
from flask import Flask, jsonify, render_template

app = Flask(__name__)
CSV_PATH = "mesures.csv"

def readCSV():
    try:
        with open (CSV_PATH, "r", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        return rows
    
    except FileNotFoundError:
        return []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/sensor/latest")
def latest():
    rows = readCSV()
    if not rows:
        return jsonify({"error": "Aucune donnée disponible!"})
    
    return jsonify(rows[-1:])

@app.route("/api/sensor/historque")
def historque():
    rows = readCSV()
    return jsonify(rows[-100:])