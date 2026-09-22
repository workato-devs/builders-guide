#!/usr/bin/env python3
"""
update-sessions.py — patch sessions.json from a CSV export of the Google Sheet.

Usage:
    python3 scripts/update-sessions.py <path-to-csv>

    python3 scripts/update-sessions.py sessions-ssot.csv
    python3 scripts/update-sessions.py ~/Downloads/sessions-export.csv

How it works:
    Each CSV row is matched to a JSON session by Date + Time Slot (12h or 24h).
    The following fields are patched from the CSV when present and non-blank:

        title, desc, url, timeLabel (Time Label), topic (from Label),
        end (End Time), speakers (Speaker N Name/Role/Company/Photo)

    Date, day, dayShort, start are used for matching only and never overwritten.
    day and dayShort are computed from Date automatically — no columns needed.
    Owner is informational only and not written to the JSON.
    Blank CSV cells defer to the existing JSON value.
"""

import csv
import json
import re
import sys
from datetime import date as Date
from pathlib import Path

SESSIONS_JSON = Path(__file__).parent.parent / "_data" / "sessions.json"

# CSV column → JSON field for simple scalar fields (case-insensitive col match)
SCALAR_MAP = {
    "title (max 60 characters)": "title",
    "title":                      "title",
    "abstract (max 180 characters)": "desc",
    "abstract":                   "desc",
    "url":                        "url",
    "time label":                 "timeLabel",
    # Label is the source of truth for both label and topic — see below
}


def normalise_time(t: str) -> str:
    """Convert any reasonable time string to 24h HH:MM for matching/storage."""
    t = t.strip()
    if re.match(r"^\d{1,2}:\d{2}$", t):
        h, m = map(int, t.split(":"))
        return f"{h:02d}:{m:02d}"
    m12 = re.match(r"^(\d{1,2}):(\d{2})\s*(AM|PM)$", t, re.IGNORECASE)
    if m12:
        h, m, period = int(m12.group(1)), int(m12.group(2)), m12.group(3).upper()
        if period == "AM":
            h = 0 if h == 12 else h
        else:
            h = 12 if h == 12 else h + 12
        return f"{h:02d}:{m:02d}"
    raise ValueError(f"Unrecognised time format: {t!r}")


def build_index(sessions: list) -> dict:
    return {(s["date"], s["start"]): s for s in sessions}


def parse_speakers(cols: dict, row: list) -> list | None:
    """
    Extract Speaker N Name/Role/Company/Photo columns.
    Returns a list of speaker dicts, or None if no speaker columns exist.
    Only returns speakers where at least a name is present.
    """
    speakers = []
    i = 1
    while True:
        name_col = f"speaker {i} name"
        if name_col not in cols:
            break
        name = row[cols[name_col]].strip()
        role = row[cols.get(f"speaker {i} role", -1)].strip() if f"speaker {i} role" in cols else ""
        company = row[cols.get(f"speaker {i} company", -1)].strip() if f"speaker {i} company" in cols else ""
        photo = row[cols.get(f"speaker {i} photo", -1)].strip() if f"speaker {i} photo" in cols else ""
        if name:
            speakers.append({"name": name, "role": role, "company": company, "photo": photo})
        i += 1
    return speakers if i > 1 else None  # None = no speaker columns at all


def main(csv_path: str):
    csv_file = Path(csv_path)
    if not csv_file.exists():
        print(f"ERROR: CSV not found: {csv_file}")
        sys.exit(1)

    with open(SESSIONS_JSON) as f:
        sessions = json.load(f)

    index = build_index(sessions)
    matched = set()
    changes = []
    line_num = 1

    with open(csv_file, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        cols = {h.strip().lower(): i for i, h in enumerate(header)}

        # Require Date and Time Slot for matching
        for required in ("date", "time slot"):
            if required not in cols:
                print(f"ERROR: CSV is missing required column: '{required}'")
                sys.exit(1)

        for line_num, row in enumerate(reader, start=2):
            if not any(c.strip() for c in row):
                continue

            date = row[cols["date"]].strip()
            start_raw = row[cols["time slot"]].strip()

            try:
                start_24h = normalise_time(start_raw)
            except ValueError as e:
                print(f"  WARNING line {line_num}: {e} — skipping row")
                continue

            key = (date, start_24h)
            session = index.get(key)

            if session is None:
                print(f"  WARNING line {line_num}: no session for {date} {start_24h} — skipping")
                continue

            matched.add(key)
            row_changes = []

            # --- Compute day / dayShort from date ---
            try:
                d = Date.fromisoformat(date)
                computed_day = d.strftime("%A %b %-d")   # "Wednesday Sep 23"
                computed_day_short = d.strftime("%a")    # "Wed"
                for field, val in (("day", computed_day), ("dayShort", computed_day_short)):
                    if session.get(field) != val:
                        row_changes.append((field, session.get(field, ""), val))
                        session[field] = val
            except ValueError:
                pass  # malformed date — leave existing values

            # --- Scalar fields ---
            for csv_col, json_field in SCALAR_MAP.items():
                if csv_col not in cols:
                    continue
                new_val = row[cols[csv_col]].strip()
                if not new_val:
                    continue
                old_val = session.get(json_field, "")
                if new_val != old_val:
                    row_changes.append((json_field, old_val, new_val))
                    session[json_field] = new_val

            # --- Label → writes to topic (Label is the source of truth for topic) ---
            if "label" in cols:
                new_label = row[cols["label"]].strip()
                if new_label:
                    old_val = session.get("topic", "")
                    if old_val != new_label:
                        row_changes.append(("topic", old_val, new_label))
                        session["topic"] = new_label

            # --- End time ---
            if "end time" in cols:
                end_raw = row[cols["end time"]].strip()
                if end_raw:
                    try:
                        end_24h = normalise_time(end_raw)
                        if end_24h != session.get("end", ""):
                            row_changes.append(("end", session.get("end", ""), end_24h))
                            session["end"] = end_24h
                    except ValueError as e:
                        print(f"  WARNING line {line_num}: bad End Time — {e}")

            # --- Speakers ---
            new_speakers = parse_speakers(cols, row)
            if new_speakers is not None and new_speakers:
                old_speakers = session.get("speakers", [])
                if new_speakers != old_speakers:
                    row_changes.append(("speakers", old_speakers, new_speakers))
                    session["speakers"] = new_speakers

            if row_changes:
                changes.append((date, start_24h, session.get("title", ""), row_changes))

    # Report
    print(f"\n{'─' * 60}")
    print(f"CSV rows processed : {line_num - 1}")
    print(f"Sessions matched   : {len(matched)}")
    print(f"Sessions changed   : {len(changes)}")

    unmatched = [s for s in sessions if (s["date"], s["start"]) not in matched]
    if unmatched:
        print(f"\nJSON sessions with no CSV row (unchanged):")
        for s in unmatched:
            print(f"  - {s['date']} {s['start']}  {s['title']}")

    if changes:
        print(f"\nChanges applied:")
        for date, start, title, field_changes in changes:
            print(f"\n  {date} {start}  {title}")
            for field, old, new in field_changes:
                print(f"    {field}:")
                if isinstance(old, list):
                    print(f"      old: {json.dumps(old)}")
                    print(f"      new: {json.dumps(new)}")
                else:
                    print(f"      old: {old!r}")
                    print(f"      new: {new!r}")

        with open(SESSIONS_JSON, "w") as f:
            json.dump(sessions, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"\n✓ Written to {SESSIONS_JSON}")
    else:
        print("\nNo changes — sessions.json is already up to date.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/update-sessions.py <path-to-csv>")
        sys.exit(1)
    main(sys.argv[1])
