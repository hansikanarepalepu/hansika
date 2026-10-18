"""Called by the VS Code extension: python cli.py <file>  ->  JSON on stdout."""
import json
import sys
from core import analyzer, db, scoring


def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        source = f.read()
    issues = analyzer.analyze(source)
    db.record(path, len(source.splitlines()), issues)
    for i in issues:
        i["times_made"] = db.rule_count(i["rule"])
        i.pop("code", None)
    print(json.dumps({"issues": issues, "stats": scoring.stats()}))


if __name__ == "__main__":
    main()
