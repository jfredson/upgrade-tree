#!/usr/bin/env python3
"""Checks on data/headline.json, the small file other sites read (added 2026-10-17).

Plain Python, standard library only:

    python3 scripts/test_headline.py

The file is written by scripts/export.py from the same records as the site's data, and the
export's `--check` refuses to pass while the committed copy is missing or stale. These tests
say the same thing from the outside, in the shape of The Belt Equation's scripts/test_headline.py:
the committed file exists and is current; it carries what the family's Projects page reads; a
missing file is named; writing it twice changes nothing; a newer reading or a moved stage makes
it stale; and doctored numbers are caught even when the dates agree. That is the failure to
catch: a reading that moved a stage, or a session that edited the record, and forgot to run the
export before committing.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CHANGELOG = ROOT / "CHANGELOG.md"
HEADLINE = DATA / export.HEADLINE_NAME


def expected_from(data: Path) -> dict:
    return export.load_everything(data, data / "readings", CHANGELOG)["headline"]


class CommittedHeadlineFile(unittest.TestCase):
    def test_exists_and_is_current(self):
        problems = export.headline_file_problems(HEADLINE, expected_from(DATA))
        self.assertEqual(problems, [], "\n".join(problems))

    def test_carries_what_the_projects_page_reads(self):
        h = json.loads(HEADLINE.read_text())
        for key in ("computed_on", "commit", "last_reading", "method", "headline", "by_stage",
                    "second_number", "counts", "site"):
            self.assertIn(key, h)
        self.assertEqual(h["headline"]["stage"], export.HEADLINE_STAGE)
        self.assertEqual(h["headline"]["words"], export.headline_words(h["headline"]["count"], h["headline"]["total"]))
        self.assertEqual(sum(s["count"] for s in h["by_stage"]), h["headline"]["total"])
        self.assertTrue(h["method"]["status"])
        self.assertEqual(h["site"]["file"], export.HEADLINE_SITE_PATH)

    def test_agrees_with_the_site_data_the_projects_page_used_to_read(self):
        """The parent read the whole tree.json before the headline file existed; the two must agree."""
        tree = json.loads((ROOT / "site" / "src" / "data" / "tree.json").read_text())
        h = json.loads(HEADLINE.read_text())
        self.assertEqual(h["headline"]["count"], tree["counts"]["first_human_or_beyond"])
        self.assertEqual(h["headline"]["total"], tree["counts"]["upgrades"])
        self.assertEqual({s["key"]: s["count"] for s in h["by_stage"]}, tree["counts"]["by_stage"])


class StaleOrMissingIsRefused(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.data = Path(self._tmp.name) / "data"
        shutil.copytree(DATA, self.data)
        self.path = self.data / export.HEADLINE_NAME

    def problems(self) -> list[str]:
        return export.headline_file_problems(self.path, expected_from(self.data))

    def write(self) -> None:
        export.write_headline(self.path, expected_from(self.data), None)

    def test_a_missing_file_is_named(self):
        self.path.unlink()
        problems = self.problems()
        self.assertTrue(any("missing" in p for p in problems), problems)

    def test_writing_it_twice_changes_nothing(self):
        self.write()
        first = self.path.read_bytes()
        self.write()
        self.assertEqual(first, self.path.read_bytes())
        self.assertEqual(self.problems(), [])

    def test_a_newer_reading_makes_the_file_stale(self):
        readings = self.data / "readings"
        newest = sorted(readings.glob("*.toml"))[-1]
        text = newest.read_text().replace(f"date = {newest.stem[:10]}", "date = 2099-01-04", 1)
        # a record dated after 2026-10-19 also carries what the reading rules ask of it
        # (docs/weekly-reading.md, decision 13): the register-aimed search's sites, and the pages opened
        text = re.sub(r"^(verdict = .*)$", r'\1\nregister = ["example.org"]', text, flags=re.M)
        text = re.sub(r"^sources = (\[.*\])$", r"sources = \1\nopened = \1", text, flags=re.M)
        (readings / "2099-01-04.toml").write_text(text)
        problems = self.problems()
        self.assertTrue(any("last_reading" in p for p in problems), problems)
        self.write()
        self.assertEqual(self.problems(), [])

    def test_a_moved_stage_makes_the_file_stale(self):
        """Move one idea-only upgrade to shown in animals: the rung totals change, the count does not."""
        path = self.data / "mind.toml"
        text = path.read_text()
        self.assertIn('stage = "idea-only"', text)
        text = text.replace('stage = "idea-only"',
                            'stage = "shown-in-animals"\nstage_reached_on = 2099-01-04\n'
                            'stage_record = "https://example.org/record"', 1)
        path.write_text(text)
        problems = self.problems()
        self.assertTrue(any("by_stage" in p for p in problems), problems)

    def test_doctored_numbers_are_caught_even_when_the_dates_agree(self):
        h = json.loads(self.path.read_text())
        h["headline"]["count"] += 1
        self.path.write_text(json.dumps(h))
        problems = self.problems()
        self.assertTrue(any("'headline' is stale" in p for p in problems), problems)

    def test_the_day_and_the_commit_may_differ(self):
        h = json.loads(self.path.read_text())
        h["computed_on"], h["commit"] = "2000-01-01", "0000000"
        self.path.write_text(json.dumps(h))
        self.assertEqual(self.problems(), [])


if __name__ == "__main__":
    unittest.main()
