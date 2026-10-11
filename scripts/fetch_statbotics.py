#!/usr/bin/env python3
"""Fetch Statbotics EPA for every event in data/events.txt and save it as JSON that index.html reads."""
import datetime, json, pathlib, sys, time, urllib.error, urllib.request

import statbotics

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "statbotics"
OUT.mkdir(parents=True, exist_ok=True)

keys = [l.strip() for l in (ROOT / "data" / "events.txt").read_text().splitlines()
        if l.strip() and not l.startswith("#")]
sb = statbotics.Statbotics()


API = "https://api.statbotics.io/v3/team_events"


def raw(query):
    """Direct request that sends only the parameters we choose (no default sort)."""
    req = urllib.request.Request(f"{API}?{query}", headers={"User-Agent": "TitanScout-data-fetch"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


# The package adds metric=year to every query, which the API rejected ("Invalid query"), so try other sorts and plain requests.
STRATEGIES = [
    ("raw, event only", lambda k: raw(f"event={k}")),
    ("raw, with limit", lambda k: raw(f"event={k}&limit=1000")),
    ("package, metric=epa_end", lambda k: sb.get_team_events(event=k, limit=1000, metric="epa_end")),
    ("package, metric=team", lambda k: sb.get_team_events(event=k, limit=1000, metric="team")),
]


def fetch(key):
    for rnd in range(2):
        for name, fn in STRATEGIES:
            try:
                rows = fn(key)
                if rows:
                    print(f"{key}: ok via {name}")
                    return rows
                print(f"{key}: {name} returned no rows", file=sys.stderr)
            except urllib.error.HTTPError as e:
                print(f"{key}: {name} failed: HTTP {e.code} {e.read()[:200]!r}", file=sys.stderr)
            except Exception as e:
                print(f"{key}: {name} failed: {e}", file=sys.stderr)
        time.sleep(5 * (rnd + 1))
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
