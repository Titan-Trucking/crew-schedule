#!/usr/bin/env python3
"""Build schedule.json for the public crew schedule page.

Reads JSON exports of the crew board's shifts, employees and equipment
(one file per record, as saved by ArtifactData with out_dir) and writes a
slimmed-down schedule.json holding only: names, dates, start/end times,
day/night, job and truck unit. Notes, quals, restrictions and time-off
reasons are never copied.

Usage: python3 export.py <db_dir> <out_file> [--from YYYY-MM-DD] [--to YYYY-MM-DD]
"""
import json, glob, os, re, sys, datetime as dt

def load(dirpath):
    out = {}
    for f in glob.glob(os.path.join(dirpath, "*.json")):
        with open(f) as fh:
            d = json.load(fh)
        doc_id = d.get("id") or os.path.splitext(os.path.basename(f))[0]
        out[doc_id] = d.get("data", d) if isinstance(d.get("data"), dict) else d
    return out

def norm(n):
    """Same name normalizing as the board: drop leading *, lowercase, 'Last, First' -> 'first last'."""
    s = re.sub(r"^\s*\*+\s*", "", str(n or "")).strip().lower()
    s = re.sub(r"\s+", " ", s)
    m = re.match(r"^([^,]+),\s*(.+)$", s)
    return f"{m.group(2)} {m.group(1)}" if m else s

def main():
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    db, out = args[0], args[1]
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=-9))).date()  # Alaska date (AKST/AKDT within an hour)
    start = today - dt.timedelta(days=today.weekday() + 7)   # Monday of last week
    end = today + dt.timedelta(days=28)
    if "--from" in args: start = dt.date.fromisoformat(args[args.index("--from") + 1])
    if "--to" in args: end = dt.date.fromisoformat(args[args.index("--to") + 1])

    emps = load(os.path.join(db, "employees"))
    trucks = load(os.path.join(db, "equipment"))
    shifts = load(os.path.join(db, "shifts"))

    people = {}
    for eid, e in emps.items():
        if e.get("active") is False:
            continue
        name = (e.get("name") or "").strip()
        if name:
            people[eid] = name

    rows = []
    for s in shifts.values():
        d = s.get("date", "")
        try:
            day = dt.date.fromisoformat(d)
        except ValueError:
            continue
        if not (start <= day <= end):
            continue
        name = people.get(s.get("empId"))
        if not name:
            continue
        if s.get("off"):
            rows.append({"d": d, "n": name, "off": True})
            continue
        if not s.get("start"):
            continue
        t = trucks.get(s.get("truckId") or "", {})
        row = {"d": d, "n": name, "s": s.get("start", ""), "e": s.get("end", ""),
               "j": (s.get("job") or "").strip(), "u": (t.get("unit") or "").strip()}
        if s.get("period") == "night":
            row["night"] = True
        rows.append(row)

    rows.sort(key=lambda r: (r["d"], r.get("off", False), r.get("s", ""), r["n"]))

    # Clocked hours per payroll week, matched the same way as the board's Hours tab.
    # Only weekly totals are copied: no punch times, no per-day detail.
    cfg_main = {}
    cfg_path = os.path.join(db, "config", "main.json")
    if os.path.exists(cfg_path):
        with open(cfg_path) as fh:
            c = json.load(fh)
        cfg_main = c.get("data", c) if isinstance(c.get("data"), dict) else c
    ws = int(cfg_main.get("weekStart", 0))
    def week_of(day):  # first day of the payroll week containing `day`
        py = (day.weekday() + 1) % 7  # Sunday=0 like the board
        return day - dt.timedelta(days=(py - ws) % 7)
    this_wk = week_of(today)
    weeks = [this_wk - dt.timedelta(days=7), this_wk]
    keys = {}
    for eid, e in emps.items():
        if eid in people:
            keys[eid] = {norm(e.get("name")), norm(e.get("btName"))} - {""}
    hours = {}
    for d in load(os.path.join(db, "days")).values():
        try:
            day = dt.date.fromisoformat(d.get("date", ""))
        except ValueError:
            continue
        wk = week_of(day)
        if wk not in weeks:
            continue
        by = d.get("byName") or {}
        for eid, ks in keys.items():
            h = sum(float((by.get(k) or {}).get("h") or 0) for k in ks if by.get(k))
            if h:
                slot = hours.setdefault(people[eid], {})
                slot[wk.isoformat()] = round(slot.get(wk.isoformat(), 0) + h, 2)

    data = {
        "updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "people": sorted(set(people.values())),
        "shifts": rows,
        "weekStart": ws,
        "weeks": [w.isoformat() for w in weeks],
        "hours": hours,
    }
    with open(out, "w") as fh:
        json.dump(data, fh, separators=(",", ":"))
    print(f"wrote {out}: {len(rows)} entries, {start} to {end}")

if __name__ == "__main__":
    main()
