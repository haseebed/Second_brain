# Second Brain
### CS50X Final Project — 2026

A clean, fast personal productivity web app to capture thoughts, track deadlines, and manage your watch/read list — all in one place.

## Description

Second Brain is a web application built with Python and Flask that helps you stay on top of your thoughts, assignments, and things you want to watch or read. The core idea is simple: open the app, capture whatever is on your mind instantly, then triage it into the right place.

The app has five main sections:

**Today** is the home page. It shows your three most urgent upcoming deadlines with color-coded urgency (red for overdue, amber for due within 3 days, green for upcoming), your five most recent captures, and any items you have starred. This page gives you a snapshot of what actually matters right now without any configuration.

**Inbox** is where everything lands first. When you capture something, it goes here. Each item has triage buttons — you can move it to Deadlines (which reveals an inline form asking for a due date and subject), move it to the Watch List, mark it as Done, or delete it. This separation between capturing and sorting keeps the capture step fast and friction-free.

**Deadlines** is a board of all your active assignments sorted by urgency. Each deadline shows how many days are left, color coded the same way as the Today page. You can add new deadlines directly from this page with a title, subject, and due date.

**Watch / Read List** stores shows, movies, books, articles, and YouTube links you want to get back to. Items can have an optional URL so you can open them directly from the app.

**Recents** shows the last 10 things you captured across the entire app, regardless of type or status. It acts as a live feed so the app always feels active.

**Search** lets you search across all your captures by keyword. Results show the item type and source so you have full context.

---

## Design Decisions

**Single table architecture** — everything lives in one `items` table with a `type` column (`idea`, `deadline`, `watchlist`) and a `status` column (`inbox`, `active`, `done`). This keeps the database simple and means one delete or done route works for every item across every page.

**Triage over instant categorization** — rather than forcing you to categorize something at capture time, you dump it to inbox first and sort it later. This is intentional. The capture step needs to be as fast as possible so you don't lose the thought. Sorting happens separately when you have a moment.

**Done vs Delete** — deleting is permanent. Marking as done hides the item from active views but keeps it in the database. This means your history is preserved and accidental deletions are avoided. Delete requires a browser confirmation dialog as an extra safeguard.

**Soft mobile navigation** — on desktop, navigation lives in a fixed left sidebar. On mobile, the sidebar is replaced by a hamburger button that triggers a smooth dropdown nav. This was implemented with pure CSS `max-height` transition rather than JavaScript animation, keeping the code simple.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3 / Flask |
| Database | SQLite3 |
| Frontend | HTML, CSS, Bootstrap 5 via AdminKit |
| Icons | Feather Icons |
| Fonts | System default (AdminKit) |

---

## Project Structure

```
second-brain/
├── app.py              # All Flask routes
├── database.py         # DB connection and init
├── second_brain.db     # SQLite database (auto-created)
├── requirements.txt    # Python dependencies
├── templates/
│   ├── layout.html     # Base template with sidebar and nav
│   ├── today.html      # Home page
│   ├── inbox.html      # Inbox with triage
│   ├── deadlines.html  # Deadlines board
│   ├── watchlist.html  # Watch / Read list
│   ├── recents.html    # Last 10 captures
│   └── search.html     # Search results
└── static/
    └── style.css       # Custom overrides
```

---

## Database Schema

One table powers the entire app:

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key, auto-increment |
| `content` | TEXT | The captured text |
| `type` | TEXT | `idea`, `deadline`, `watchlist` |
| `status` | TEXT | `inbox`, `active`, `done` |
| `due_date` | DATE | Deadlines only |
| `subject` | TEXT | e.g. `Maths`, `OOP` |
| `url` | TEXT | Watch list links |
| `source` | TEXT | `class`, `youtube`, `article`, `friend`, `other` |
| `is_favorite` | INTEGER | `0` or `1` — the star flag |
| `created_at` | DATETIME | Auto-set on insert |

---

## How to Run

**Requirements:** Python 3.8 or higher

```bash
# 1. Clone or download the project
cd second-brain

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip3 install flask

# 4. Run the app
python3 app.py
```

Open `http://127.0.0.1:5000` in your browser. The database is created automatically on first run.

---

## Features

- ⚡ Quick capture from the Today page — type and hit Save
- 📥 Inbox with triage — move items to Deadlines or Watch List inline
- 🕐 Deadlines board with red/amber/green urgency color coding
- 🔖 Watch / Read List with optional URLs
- ⭐ Star any item — starred items surface on the Today page
- ✓ Mark items as done — soft delete that preserves history
- 🔍 Search across all captures
- 🕓 Recents feed — last 10 captures at a glance
- 📱 Responsive — works on mobile with a slide-down nav