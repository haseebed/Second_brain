from flask import Flask, render_template, request, redirect, url_for
from database import init_db, get_db
from datetime import date

app = Flask(__name__)
init_db()


# ─────────────────────────────────────────
#  TODAY
# ─────────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
def today():
    db = get_db()

    if request.method == "POST":
        content = request.form.get("content", "").strip()
        if content:
            db.execute("INSERT INTO items (content) VALUES (?)", (content,))
            db.commit()

    deadlines = db.execute("""
        SELECT * FROM items
        WHERE type = 'deadline' AND status != 'done'
        ORDER BY due_date ASC LIMIT 3
    """).fetchall()

    recents = db.execute("""
        SELECT * FROM items
        WHERE status != 'done'
        ORDER BY created_at DESC LIMIT 5
    """).fetchall()

    starred = db.execute("""
        SELECT * FROM items
        WHERE is_favorite = 1 AND status != 'done'
        ORDER BY created_at DESC
    """).fetchall()

    db.close()

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

    return render_template("today.html", tagged=tagged, recents=recents, starred=starred)


# ─────────────────────────────────────────
#  INBOX
# ─────────────────────────────────────────
@app.route("/inbox", methods=["GET", "POST"])
def inbox():
    db = get_db()

    if request.method == "POST":
        content = request.form.get("content", "").strip()
        if content:
            db.execute("INSERT INTO items (content) VALUES (?)", (content,))
            db.commit()

    items = db.execute("""
        SELECT * FROM items
        WHERE status = 'inbox'
        ORDER BY created_at DESC
    """).fetchall()
    db.close()
    return render_template("inbox.html", items=items)

# ─────────────────────────────────────────
#  DEADLINES
# ─────────────────────────────────────────
@app.route("/deadlines", methods=["GET", "POST"])
def deadlines():
    db = get_db()

    if request.method == "POST":
        content  = request.form.get("content", "").strip()
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

    today_date = date.today()
    tagged = []
    for item in items:
        due = date.fromisoformat(item['due_date'])
        days_left = (due - today_date).days
        if days_left < 0:
            urgency = "danger"
        elif days_left <= 3:
            urgency = "warning"
        else:
            urgency = "success"
        tagged.append((item, urgency, days_left))

    return render_template("deadlines.html", tagged=tagged)


# ─────────────────────────────────────────
#  WATCHLIST
# ─────────────────────────────────────────
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
        WHERE type = 'watchlist' AND status != 'done'
        ORDER BY created_at DESC
    """).fetchall()
    db.close()
    return render_template("watchlist.html", items=items)


# ─────────────────────────────────────────
#  RECENTS
# ─────────────────────────────────────────
@app.route("/recents")
def recents():
    db = get_db()
    items = db.execute("""
        SELECT * FROM items
        ORDER BY created_at DESC
        LIMIT 10
    """).fetchall()
    db.close()
    return render_template("recents.html", items=items)

# ─────────────────────────────────────────
#  DELETE
# ─────────────────────────────────────────
@app.route("/delete/<int:item_id>", methods=["POST"])
def delete(item_id):
    db = get_db()
    db.execute("DELETE FROM items WHERE id = ?", (item_id,))
    db.commit()
    db.close()
    return redirect(request.referrer or url_for("today"))


# ─────────────────────────────────────────
#  MARK AS DONE
# ─────────────────────────────────────────
@app.route("/done/<int:item_id>", methods=["POST"])
def mark_done(item_id):
    db = get_db()
    db.execute("UPDATE items SET status = 'done' WHERE id = ?", (item_id,))
    db.commit()
    db.close()
    return redirect(request.referrer or url_for("today"))

# ─────────────────────────────────────────
#  FAVORITES
# ─────────────────────────────────────────
@app.route("/star/<int:item_id>", methods=["POST"])
def toggle_star(item_id):
    db = get_db()
    db.execute("""
        UPDATE items
        SET is_favorite = CASE WHEN is_favorite = 1 THEN 0 ELSE 1 END
        WHERE id = ?
    """, (item_id,))
    db.commit()
    db.close()
    return redirect(request.referrer or url_for("today"))


# ─────────────────────────────────────────
#  SEARCH OPTION
# ─────────────────────────────────────────

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    items = []
    if q:
        db = get_db()
        items = db.execute("""
            SELECT * FROM items
            WHERE content LIKE ?
            ORDER BY created_at DESC
        """, (f"%{q}%",)).fetchall()
        db.close()
    return render_template("search.html", items=items, q=q)

# ─────────────────────────────────────────
#  MOVE (triage inbox item)
# ─────────────────────────────────────────
@app.route("/move/<int:item_id>", methods=["POST"])
def move(item_id):
    destination = request.form.get("destination")
    due_date    = request.form.get("due_date", "").strip() or None
    subject     = request.form.get("subject", "").strip() or None

    db = get_db()

    if destination == "deadline" and due_date:
        db.execute("""
            UPDATE items
            SET type = 'deadline', status = 'active', due_date = ?, subject = ?
            WHERE id = ?
        """, (due_date, subject, item_id))

    elif destination == "watchlist":
        db.execute("""
            UPDATE items
            SET type = 'watchlist', status = 'active'
            WHERE id = ?
        """, (item_id,))

    db.commit()
    db.close()
    return redirect(request.referrer or url_for("inbox"))


if __name__ == "__main__":
    app.run(debug=True)