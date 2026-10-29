"""Browser -> Flask -> Postgres.

Local:   python app.py   then open http://localhost:8000
Railway: started by the Dockerfile (gunicorn on 0.0.0.0:$PORT)
"""
import os

import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template

load_dotenv()  # locally reads .env; on Railway there is no .env, the Variables tab provides it

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    # Fail loudly at startup so the Deploy Logs say exactly why (Stage 4)
    raise RuntimeError("DATABASE_URL not set")

app = Flask(__name__)


def query(sql):
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    finally:
        conn.close()


@app.route("/")
def index():
    # Stage 1a: the names
    names = [r[0] for r in query("SELECT name FROM students ORDER BY name")]

    # Stage 3: the "model" - averages computed in SQL with AVG()
    avg = query(
        """SELECT ROUND(AVG(skill_programming), 2),
                  ROUND(AVG(skill_data_stats), 2),
                  ROUND(AVG(skill_frontend_design), 2),
                  ROUND(AVG(skill_business_pitch), 2)
           FROM students"""
    )[0]
    averages = [
        ("Programming", avg[0]),
        ("Data / stats", avg[1]),
        ("Frontend / design", avg[2]),
        ("Business / pitch", avg[3]),
    ]
    # Server-rendered: Python puts the data into the HTML before sending it
    return render_template("index.html", names=names, averages=averages)


if __name__ == "__main__":
    # 0.0.0.0 + PORT so it also works inside a container; 8000 avoids macOS AirPlay on 5000
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
