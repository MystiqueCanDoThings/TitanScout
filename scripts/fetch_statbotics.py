#!/usr/bin/env python3
"""Fetch Statbotics EPA for every event in data/events.txt and save it as JSON that index.html reads."""
import datetime, json, os, pathlib, sys, time, urllib.error, urllib.request

import statbotics

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "statbotics"
OUT.mkdir(parents=True, exist_ok=True)

keys = [l.strip() for l in (ROOT / "data" / "events.txt").read_text().splitlines()
        if l.strip() and not l.startswith("#")]
sb = statbotics.Statbotics()


BASE = "https://api.statbotics.io/v3"


def get_json(url, headers=None):
    h = {"User-Agent": "TitanScout-data-fetch"}
    h.update(headers or {})
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=60) as r:
        return json.load(r)


def describe(e):
    if isinstance(e, urllib.error.HTTPError):
        return f"HTTP {e.code} {e.read()[:120]!r}"
    return str(e)


# The package adds metric=year to every query ("Invalid query"), so try plain requests and other sorts first.
STRATEGIES = [
    ("raw, event only", lambda k: get_json(f"{BASE}/team_events?event={k}")),
    ("raw, with limit", lambda k: get_json(f"{BASE}/team_events?event={k}&limit=1000")),
    ("package, metric=epa_end", lambda k: sb.get_team_events(event=k, limit=1000, metric="epa_end")),
]


def teams_for(key):
    """Team numbers at an event: from Statbotics matches, else from TBA (needs a TBA_KEY secret)."""
    teams = set()
    try:
        for m in get_json(f"{BASE}/matches?event={key}&limit=1000"):
            for side in ("red", "blue"):
                for t in ((m.get("alliances") or {}).get(side) or {}).get("team_keys", []):
                    teams.add(int(str(t).replace("frc", "")))
    except Exception as e:
        print(f"{key}: Statbotics match list failed: {describe(e)}", file=sys.stderr)
    if not teams and os.environ.get("TBA_KEY"):
        try:
            tba = get_json(f"https://www.thebluealliance.com/api/v3/event/{key}/teams/keys",
                           {"X-TBA-Auth-Key": os.environ["TBA_KEY"]})
            teams = {int(t[3:]) for t in tba}
        except Exception as e:
            print(f"{key}: TBA team list failed: {describe(e)}", file=sys.stderr)
    elif not teams:
        print(f"{key}: no TBA_KEY secret set, so no team list fallback", file=sys.stderr)
    return sorted(teams)


def fetch(key):
    try:
        get_json(f"{BASE}/event/{key}")
        print(f"{key}: Statbotics knows this event")
    except Exception as e:
        print(f"{key}: Statbotics event lookup failed: {describe(e)}", file=sys.stderr)
    for name, fn in STRATEGIES:
        try:
            rows = fn(key)
            if rows:
                print(f"{key}: ok via {name}")
                return rows
            print(f"{key}: {name} returned no rows", file=sys.stderr)
        except Exception as e:
            print(f"{key}: {name} failed: {describe(e)}", file=sys.stderr)
    # Last resort: one request per team.
    rows = []
    for team in teams_for(key):
        for attempt in range(2):
            try:
                rows.append(get_json(f"{BASE}/team_event/{team}/{key}"))
                break
            except Exception as e:
                if attempt:
                    print(f"{key}: team {team} failed: {describe(e)}", file=sys.stderr)
                time.sleep(1)
    if rows:
        print(f"{key}: ok via per-team requests ({len(rows)} teams)")
    return rows or None


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
