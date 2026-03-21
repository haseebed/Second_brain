from flask import Flask, render_template, request, redirect, url_for
from database import init_db, get_db
from datetime import date 

app = Flask(__name__)
init_db()

@app.route("/", methods=["GET", "POST"])
def today():
    db = get_db()

    if request.method == "POST":
        content = request.form.get("content", "").strip()
        if content:
            db.execute("INSERT INTO items (content) VALUES (?)", (content,))
            db.commit()

    # 3 most urgent deadlines
    deadlines = db.execute("""
        SELECT * FROM items
        WHERE type = 'deadline' AND status != 'done'
        ORDER BY due_date ASC
        LIMIT 3
    """).fetchall()

    # 5 most recent captures
    recents = db.execute("""
        SELECT * FROM items
        ORDER BY created_at DESC
        LIMIT 5
    """).fetchall()

    db.close()

    # Calculate urgency for deadlines
    today_date = date.today()
    tagged = []
    for item in deadlines:
        due = date.fromisoformat(item['due_date'])
        days_left = (due - today_date).days
        if days_left < 0:
            urgency = "danger"
        elif days_left <= 3:
            urgency = "warning"
        else:
            urgency = "success"
        tagged.append((item, urgency, days_left))

    return render_template("today.html", tagged=tagged, recents=recents)

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

@app.route("/deadlines", methods=["GET", "POST"])
def deadlines():
    db = get_db()

    if request.method == "POST":
        content = request.form.get("content", "").strip()
        due_date = request.form.get("due_date", "").strip()
        subject  = request.form.get("subject", "").strip()
        if content and due_date:
            db.execute(
                "INSERT INTO items (content, type, status, due_date, subject) VALUES (?, 'deadline', 'active', ?, ?)",
                (content, due_date, subject or None)
            )
            db.commit()

    items = db.execute("""
        SELECT * FROM items
        WHERE type = 'deadline' AND status != 'done'
        ORDER BY due_date ASC
    """).fetchall()
    db.close()

    # Calculate urgency for each item
    today = date.today()
    tagged = []
    for item in items:
        due = date.fromisoformat(item['due_date'])
        days_left = (due - today).days
        if days_left < 0:
            urgency = "danger"    # red — overdue
        elif days_left <= 3:
            urgency = "warning"   # amber — due soon
        else:
            urgency = "success"   # green — upcoming
        tagged.append((item, urgency, days_left))

    return render_template("deadlines.html", tagged=tagged)


@app.route("/watchlist", methods=["GET", "POST"])
def watchlist():
    db = get_db()

    if request.method == "POST":
        content = request.form.get("content", "").strip()
        url     = request.form.get("url", "").strip()
        kind    = request.form.get("kind", "show")
        if content:
            db.execute(
                "INSERT INTO items (content, type, status, url, subject) VALUES (?, 'watchlist', 'active', ?, ?)",
                (content, url or None, kind)
            )
            db.commit()

    items = db.execute("""
        SELECT * FROM items
        WHERE type = 'watchlist'
        ORDER BY created_at DESC
    """).fetchall()
    db.close()
    return render_template("watchlist.html", items=items)

@app.route("/delete/<int:item_id>", methods=["POST"])
def delete(item_id):
    db = get_db()
    db.execute("DELETE FROM items WHERE id = ?", (item_id,))
    db.commit()
    db.close()
    return redirect(request.referrer or url_for("today"))

if __name__ == "__main__":
    app.run(debug=True)