#!/usr/bin/env python3
"""Checks for scripts/check_news.py (the news posts; tracker pattern, rule 4.16).

    python3 scripts/test_news.py
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


class NewsPosts(unittest.TestCase):
    """scripts/check_news.py refuses a post that cannot be trusted (tracker pattern, rule 4.16)."""

    RECORDS = {"upgrades": [{"id": "a-leaf", "revisions": [{"date": "2026-10-17"}], "stage_reached_on": "1977-05-01"}], "claims": [], "readings": []}
    GOOD = ("---\ntitle: A leaf moves\ndate: 2026-10-18\nkind: rung-reached\nsummary: It moved.\nrecords: [a-leaf]\n"
            "sources:\n  - label: The paper\n    url: https://example.org/paper\n---\n\n## What happened\n\n"
            "On 27 April 2026 the centre [published it](https://example.org/paper).\n")

    def run_check(self, text, name="2026-10-18-a-leaf-moves.md"):
        import check_news
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp); (d / name).write_text(text, encoding="utf-8")
            problems, n = check_news.check(d, self.RECORDS)
        return problems

    def test_a_good_post_passes(self):
        self.assertEqual(self.run_check(self.GOOD), [])

    def test_a_figure_without_a_link_is_refused(self):
        bad = self.GOOD.replace("[published it](https://example.org/paper)", "published it")
        self.assertTrue(any("states a figure with no link" in p for p in self.run_check(bad)))

    def test_a_missing_record_is_refused(self):
        self.assertTrue(any("does not exist" in p for p in self.run_check(self.GOOD.replace("[a-leaf]", "[no-such-leaf]"))))

    def test_a_date_mismatch_is_refused(self):
        self.assertTrue(any("differs from the file name" in p for p in self.run_check(self.GOOD, name="2026-10-01-a-leaf-moves.md")))

    def test_a_record_with_no_change_near_the_date_is_refused(self):
        far = self.GOOD.replace("date: 2026-10-18", "date: 2026-12-30")
        self.assertTrue(any("shows no dated change" in p for p in self.run_check(far, name="2026-12-30-a-leaf-moves.md")))

    def test_no_source_is_refused(self):
        bad = self.GOOD.replace("sources:\n  - label: The paper\n    url: https://example.org/paper\n", "")
        self.assertTrue(any("cites no source" in p for p in self.run_check(bad)))

    def test_a_claim_made_in_the_window_counts_as_its_own_dated_change(self):
        records = {"upgrades": [], "claims": [{"id": "a-claim", "when": "2026-10-17"}], "readings": []}
        import check_news
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp); (d / "2026-10-18-a-leaf-moves.md").write_text(self.GOOD.replace("[a-leaf]", "[a-claim]").replace("rung-reached", "claim"), encoding="utf-8")
            self.assertEqual(check_news.check(d, records)[0], [])
            records["claims"][0]["when"] = "2026-09-01"
            self.assertTrue(any("no dated change" in p for p in check_news.check(d, records)[0]))

    def test_the_opener_need_not_name_a_record(self):
        opener = self.GOOD.replace("kind: rung-reached", "kind: start-here").replace("records: [a-leaf]\n", "")
        self.assertEqual(self.run_check(opener, name="2026-10-18-start-here.md"), [])




if __name__ == "__main__":
    unittest.main()
