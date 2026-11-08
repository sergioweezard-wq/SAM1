import os

import psycopg2
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

DB_CONFIG = {
    "host": "34.14.140.240",
    "port": 5431,
    "dbname": "guestbook",
    "user": "postgres",
    "password": "adm1in1",
    "sslmode": "require",
}


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    conn = get_conn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    text VARCHAR(500) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
    finally:
        conn.close()


@app.route("/")
def index():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, text, created_at FROM messages ORDER BY id DESC"
            )
            rows = cur.fetchall()
    finally:
        conn.close()
    return render_template("index.html", messages=rows)


@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()
    text = request.form.get("text", "").strip()

    if not name or not text:
        flash("Заповніть ім'я та повідомлення.")
        return redirect(url_for("index"))
    if len(name) > 50 or len(text) > 500:
        flash("Занадто довгий текст.")
        return redirect(url_for("index"))

    conn = get_conn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO messages (name, text) VALUES (%s, %s)",
                (name, text),
            )
    finally:
        conn.close()
    flash("Повідомлення збережено!")
    return redirect(url_for("index"))


@app.route("/delete/<int:msg_id>", methods=["POST"])
def delete(msg_id):
    conn = get_conn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("DELETE FROM messages WHERE id = %s", (msg_id,))
    finally:
        conn.close()
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)