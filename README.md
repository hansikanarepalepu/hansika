# Mistake Tracker

A VS Code extension plus an open-source dashboard that catches common Python mistakes
when you save, shows the fix in the editor, counts how often you repeat each mistake,
and reports your score and improvement trend.

## Run it
```bash
pip install -r requirements.txt
python server.py                  # dashboard at http://127.0.0.1:5000
```
Then in VS Code: open the `extension/` folder and press F5 (Extension Development Host),
open any `.py` file and save it. Problems appear as warnings with the fix; the status bar
shows your score; click it to open the dashboard.

## Score
- Mistakes per 100 lines analysed (each distinct mistake counted once per day).
- Score = 100 - 4 x (mistakes per 100 lines this week), minimum 0.
- Status compares this week with last week: Improving / Steady / Needs attention.

## Add a rule
Add a check in `core/analyzer.py` and a hint in `HINTS`. Pull requests welcome.

## Host it publicly
`HOST=0.0.0.0 PORT=8000 python server.py`, or deploy with gunicorn (`gunicorn server:app`).
Data is stored per machine in `~/.mistake_tracker/data.db` (override with `MISTAKE_TRACKER_DB`).

MIT licensed.
