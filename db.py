"""SQLite storage for mistakes and analysed lines."""
import os
import sqlite3
from datetime import date

DB_PATH = os.environ.get(
    "MISTAKE_TRACKER_DB",
    os.path.join(os.path.expanduser("~"), ".mistake_tracker", "data.db"),
)


def connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS mistakes(
            id INTEGER PRIMARY KEY,
            day TEXT NOT NULL,
            file TEXT NOT NULL,
            rule TEXT NOT NULL,
            line INTEGER,
            message TEXT,
            signature TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS analyses(
            day TEXT NOT NULL,
            file TEXT NOT NULL,
            lines INTEGER NOT NULL,
            PRIMARY KEY(day, file)
        );
        """
    )
    return conn


def record(file, lines, issues):
    """Store one analysis run. Identical issues on the same day are counted once."""
    today = date.today().isoformat()
    with connect() as conn:
        conn.execute(
            "INSERT INTO analyses(day,file,lines) VALUES(?,?,?) "
            "ON CONFLICT(day,file) DO UPDATE SET lines=MAX(lines, excluded.lines)",
            (today, file, lines),
        )
        for i in issues:
            sig = f"{today}|{file}|{i['rule']}|{i['code']}"
            conn.execute(
                "INSERT OR IGNORE INTO mistakes(day,file,rule,line,message,signature) "
                "VALUES(?,?,?,?,?,?)",
                (today, file, i["rule"], i["line"], i["message"], sig),
            )


def rule_count(rule):
    with connect() as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM mistakes WHERE rule=?", (rule,)
        ).fetchone()[0]
