#!/usr/bin/env python3
"""Fetch Statbotics EPA for every event in data/events.txt and save it as JSON that index.html reads."""
import datetime, json, pathlib, sys, time

import statbotics

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "statbotics"
OUT.mkdir(parents=True, exist_ok=True)

keys = [l.strip() for l in (ROOT / "data" / "events.txt").read_text().splitlines()
        if l.strip() and not l.startswith("#")]
sb = statbotics.Statbotics()


def fetch(key):
    """Retry with backoff, since the Statbotics API sometimes returns 5xx."""
    for attempt in range(4):
        try:
            return sb.get_team_events(event=key, limit=1000)
        except Exception as e:
            print(f"{key}: attempt {attempt + 1} failed: {e}", file=sys.stderr)
            time.sleep(3 * 2 ** attempt)
    return None


failed = 0
for key in keys:
    rows = fetch(key)
    if not rows:
        failed += 1  # keep the previous file, if any
        continue
    path = OUT / f"{key}.json"
    if path.exists() and json.loads(path.read_text()).get("rows") == rows:
        print(key, "unchanged")
        continue
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    path.write_text(json.dumps({"event": key, "updated": stamp, "rows": rows}, separators=(",", ":")))
    print(key, len(rows), "teams")

sys.exit(1 if keys and failed == len(keys) else 0)
