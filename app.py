from flask import Flask, render_template, request, redirect, url_for
from database import init_db, get_db

app = Flask(__name__)
init_db()

@app.route("/", methods=["GET", "POST"])
def today():
    return "Today page — coming soon!"

@app.route("/inbox", methods=["GET", "POST"])
def inbox():
    db = get_db()
    # If the form was submitted, save it first
    if request.method == "POST":
        content = request.form.get("content", "").strip()
        if content:
            db.execute("INSERT INTO items (content) VALUES (?)", (content,))
            db.commit()
    # Then fetch everything and show the page
    items = db.execute("SELECT * FROM items ORDER BY created_at DESC").fetchall()
    db.close()
    return render_template("inbox.html", items=items)   


if __name__ == "__main__":
    app.run(debug=True)