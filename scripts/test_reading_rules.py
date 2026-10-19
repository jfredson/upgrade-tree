#!/usr/bin/env python3
"""Checks on the rules the export script holds a weekly reading to (added 2026-10-18).

Plain Python, standard library only:

    python3 scripts/test_reading_rules.py

They say, from the outside, what John ruled on 2026-10-18 after the audit of the first cloud
reading (docs/readings/audit-2026-10-18.md): the newest real record reads exactly the upgrades its
scope asks for; from the reading of 2026-10-19 a verdict that is not quiet lists the pages it
opened and cites only those, and every item names the sites of its register-aimed search; and the
site's data is stamped with the Pacific date, not the machine's.
"""

from __future__ import annotations

import datetime as dt
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export  # noqa: E402

UTC = dt.timezone.utc
TRACKED = {"a": "leaf", "b": "mid", "c": "top"}
IDS = set(TRACKED)


def item(uid, verdict="quiet", **extra):
    base = {"upgrade": uid, "verdict": verdict, "queries": ["one", "two"], "found": "Nothing turned up.",
            "register": ["fda.gov"]}
    base.update(extra)
    return base


def record(date, scope, items, **head):
    reading = {"date": date, "ran_at": "2026-10-19T01:00:00Z", "scope": scope, "upgrades_read": len(items),
               "searches": 2 * len(items), "commit_before": "abc1234"}
    reading.update(head)
    return {"reading": reading, "item": items, "_where": f"readings/{date}.toml", "_file": f"{date}.toml",
            "_name_date": date}


class TodayPacific(unittest.TestCase):
    def test_a_sunday_evening_run_is_still_sunday(self):
        # 18:07 Pacific on 2026-10-18 is 01:07 universal time on the 19th
        self.assertEqual(export.today_pacific(dt.datetime(2026, 10, 19, 1, 7, tzinfo=UTC)), dt.date(2026, 10, 18))

    def test_winter_time(self):
        self.assertEqual(export.today_pacific(dt.datetime(2026, 12, 7, 7, 30, tzinfo=UTC)), dt.date(2026, 12, 6))
        self.assertEqual(export.today_pacific(dt.datetime(2026, 12, 7, 8, 30, tzinfo=UTC)), dt.date(2026, 12, 7))

    def test_the_fallback_without_a_time_zone_database_agrees(self):
        for when in (dt.datetime(2026, 10, 19, 1, 7, tzinfo=UTC), dt.datetime(2026, 12, 7, 7, 30, tzinfo=UTC),
                     dt.datetime(2026, 12, 7, 8, 30, tzinfo=UTC), dt.datetime(2026, 3, 8, 9, 59, tzinfo=UTC),
                     dt.datetime(2026, 3, 8, 10, 0, tzinfo=UTC), dt.datetime(2026, 7, 1, 6, 59, tzinfo=UTC),
                     dt.datetime(2026, 7, 1, 7, 0, tzinfo=UTC), dt.datetime(2026, 11, 1, 8, 59, tzinfo=UTC),
                     dt.datetime(2026, 11, 1, 9, 0, tzinfo=UTC)):
            expect = export.today_pacific(when)
            with mock.patch.dict(sys.modules, {"zoneinfo": None}):
                self.assertEqual(export.today_pacific(when), expect, when)


class ScopeAndCount(unittest.TestCase):
    def test_weekly_reads_everything_but_the_top(self):
        r = record("2026-10-18", "weekly", [item("a"), item("b")])
        self.assertEqual(export.validate_readings([r], IDS, TRACKED), [])

    def test_weekly_that_reads_the_top_or_skips_one_is_refused(self):
        r = record("2026-10-18", "weekly", [item("a"), item("c")])
        problems = export.validate_readings([r], IDS, TRACKED)
        self.assertTrue(any("missing: b" in p and "not in this scope: c" in p for p in problems), problems)

    def test_monthly_reads_all(self):
        r = record("2026-11-01", "monthly", [item("a"), item("b"), item("c")])
        self.assertEqual(export.validate_readings([r], IDS, TRACKED), [])
        r = record("2026-11-01", "monthly", [item("a"), item("b")])
        self.assertTrue(export.validate_readings([r], IDS, TRACKED))

    def test_only_the_newest_real_record_is_held_to_the_count(self):
        old = record("2026-10-11", "weekly", [item("a")])
        new = record("2026-10-18", "weekly", [item("a"), item("b")])
        self.assertEqual(export.validate_readings([old, new], IDS, TRACKED), [])


class OpenedAndRegister(unittest.TestCase):
    def noted(self, **extra):
        return item("a", "noted", sources=["https://example.org/x"], **extra)

    def test_earlier_records_are_not_held_to_it(self):
        r = record("2026-10-18", "weekly", [item("a", "noted", sources=["https://example.org/x"]), item("b")])
        for it in r["item"]:
            it.pop("register")
        self.assertEqual(export.validate_readings([r], IDS, TRACKED), [])

    def test_a_noted_item_has_to_list_what_it_opened(self):
        r = record("2026-10-19", "weekly", [self.noted(), item("b")])
        self.assertTrue(any("'opened'" in p for p in export.validate_readings([r], IDS, TRACKED)))

    def test_sources_must_have_been_opened(self):
        r = record("2026-10-19", "weekly", [self.noted(opened=["https://example.org/other"]), item("b")])
        self.assertTrue(any("not in 'opened'" in p for p in export.validate_readings([r], IDS, TRACKED)))

    def test_opened_and_cited_passes(self):
        r = record("2026-10-19", "weekly", [self.noted(opened=["https://example.org/x"]), item("b")])
        self.assertEqual(export.validate_readings([r], IDS, TRACKED), [])

    def test_every_item_names_its_register(self):
        bad = item("b")
        bad["register"] = []
        r = record("2026-10-19", "weekly", [item("a"), bad])
        self.assertTrue(any("'register'" in p for p in export.validate_readings([r], IDS, TRACKED)))
        bad["register"] = ["not a site"]
        self.assertTrue(any("'register'" in p for p in export.validate_readings([r], IDS, TRACKED)))


if __name__ == "__main__":
    unittest.main()
