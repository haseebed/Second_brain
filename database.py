import sqlite3

DB_PATH = "second_brain.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id          INTEGER  PRIMARY KEY AUTOINCREMENT,
            content     TEXT     NOT NULL,
            type        TEXT     NOT NULL DEFAULT 'idea',
            status      TEXT     NOT NULL DEFAULT 'inbox',
            due_date    DATE,
            subject     TEXT,
            url         TEXT,
            source      TEXT     DEFAULT 'other',
            is_favorite INTEGER  NOT NULL DEFAULT 0,
            created_at  DATETIME NOT NULL DEFAULT (datetime('now'))
        )
    """)
    db.commit()
    db.close()
    print("✅ Database ready.")