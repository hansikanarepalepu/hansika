"""Turns stored mistakes into a score, trend and improvement status."""
from datetime import date, timedelta
from .db import connect


def _period(conn, start, end):
    m = conn.execute("SELECT COUNT(*) FROM mistakes WHERE day>=? AND day<?", (start, end)).fetchone()[0]
    l = conn.execute("SELECT COALESCE(SUM(lines),0) FROM analyses WHERE day>=? AND day<?", (start, end)).fetchone()[0]
    return m, l, (m / l * 100 if l else 0.0)


def stats():
    today = date.today()
    tomorrow = (today + timedelta(days=1)).isoformat()
    d7 = (today - timedelta(days=6)).isoformat()
    d14 = (today - timedelta(days=13)).isoformat()
    with connect() as conn:
        total = conn.execute("SELECT COUNT(*) FROM mistakes").fetchone()[0]
        _, recent_l, recent_d = _period(conn, d7, tomorrow)
        _, prev_l, prev_d = _period(conn, d14, d7)

        by_rule = [dict(r) for r in conn.execute(
            "SELECT rule, COUNT(*) AS count FROM mistakes GROUP BY rule ORDER BY count DESC")]
        daily = []
        for i in range(13, -1, -1):
            day = today - timedelta(days=i)
            m, _, d = _period(conn, day.isoformat(), (day + timedelta(days=1)).isoformat())
            daily.append({"day": day.isoformat(), "mistakes": m, "per100": round(d, 2)})

    score = max(0, round(100 - recent_d * 4)) if recent_l else None
    if not recent_l:
        status = "No data yet. Save a Python file in VS Code."
    elif not prev_l:
        status = "Getting started. Keep coding to see your trend."
    elif recent_d < prev_d * 0.9:
        status = "Improving"
    elif recent_d > prev_d * 1.1:
        status = "Needs attention"
    else:
        status = "Steady"
    return {
        "total_mistakes": total, "score": score, "status": status,
        "this_week": round(recent_d, 2), "last_week": round(prev_d, 2),
        "by_rule": by_rule, "daily": daily,
    }
