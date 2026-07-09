import csv, os, time
from flask import Flask, jsonify, render_template

app = Flask(__name__)
def getCSVpath():
    return os.path.join(os.path.dirname(__file__), "données", time.strftime("mesures%b%d.csv"))

def readCSV():
    try:
        with open (getCSVpath(), "r", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        return rows
    
    except FileNotFoundError:
        return []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/sensors/latest")
def latest():
    rows = readCSV()
    if not rows:
        return jsonify({"error": "Aucune donnée disponible!"})
    
    return jsonify(rows[-1])

@app.route("/api/sensors/history/<int:count>")
def historque(count):
    rows = readCSV()
    return jsonify(rows[-count:])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)