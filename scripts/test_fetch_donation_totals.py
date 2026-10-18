#!/usr/bin/env python3
"""Parser tests for scripts/fetch_donation_totals.py. No network."""
from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fetch_donation_totals import (
    build_record,
    cents_to_dollars,
    kofi_raised_cents,
    parse_kofi_goal,
    sum_sponsor_cents,
)

FIXTURE = """
<div class="progress-bar" style="width: 0%"></div>
<span class="kfds-font-bold">2% </span><span class="goal-label" id="profileGoalTotal">of $10000 goal</span>
"""


class DonationTotalsTest(unittest.TestCase):
    def test_parse_public_goal(self) -> None:
        percent, goal = parse_kofi_goal(FIXTURE)
        self.assertEqual(percent, Decimal("2"))
        self.assertEqual(goal, Decimal("10000"))

    def test_kofi_percent_times_goal(self) -> None:
        self.assertEqual(kofi_raised_cents(Decimal("2"), Decimal("10000")), 20000)

    def test_comma_in_goal(self) -> None:
        html = (
            '<span class="kfds-font-bold">10%</span>'
            '<span class="goal-label" id="profileGoalTotal">of $10,000 goal</span>'
        )
        percent, goal = parse_kofi_goal(html)
        self.assertEqual(percent, Decimal("10"))
        self.assertEqual(goal, Decimal("10000"))
        self.assertEqual(kofi_raised_cents(percent, goal), 100000)

    def test_missing_goal_fails(self) -> None:
        with self.assertRaises(ValueError):
            parse_kofi_goal("<html>Just a moment...</html>")

    def test_sum_lifetime_cents(self) -> None:
        pages = [[{"amountInCents": 500}, {"amountInCents": 250}], [{"amountInCents": 0}]]
        self.assertEqual(sum_sponsor_cents(pages), 750)
        self.assertEqual(cents_to_dollars(750), 8)

    def test_combined_record(self) -> None:
        record = build_record(FIXTURE, 150)
        self.assertEqual(record["kofi_usd"], 200)
        self.assertEqual(record["github_sponsors_usd"], 2)
        self.assertEqual(record["raised_usd"], 202)
        self.assertEqual(record["github_sponsors_user"], "aspauldingcode")


if __name__ == "__main__":
    unittest.main()
