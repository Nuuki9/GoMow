"""Tests for post-completion mowing-frequency timing."""

from datetime import datetime, timedelta, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).parents[1] / "src/pyscript/modules/mowing_cadence.py"
SPEC = spec_from_file_location("mowing_cadence", MODULE_PATH)
assert SPEC and SPEC.loader
mowing_cadence = module_from_spec(SPEC)
SPEC.loader.exec_module(mowing_cadence)


class MowingCadenceTests(unittest.TestCase):
    def test_long_gate_interruption_preserves_start_anchored_nominal_due(self):
        accepted_start = datetime(2026, 8, 1, 9, tzinfo=timezone.utc)
        completed = datetime(2026, 8, 4, 12, tzinfo=timezone.utc)

        timing = mowing_cadence.calculate_next_eligible_at(
            accepted_start_at=accepted_start,
            planned_interval=timedelta(days=5),
            verified_completed_at=completed,
            minimum_post_completion_rest=timedelta(days=1),
        )

        self.assertEqual(timing.nominal_due_at, datetime(2026, 8, 6, 9, tzinfo=timezone.utc))
        self.assertEqual(timing.next_eligible_at, datetime(2026, 8, 6, 9, tzinfo=timezone.utc))

    def test_very_long_interruption_preserves_minimum_rest_after_completion(self):
        accepted_start = datetime(2026, 8, 1, 9, tzinfo=timezone.utc)
        completed = datetime(2026, 8, 8, 12, tzinfo=timezone.utc)

        timing = mowing_cadence.calculate_next_eligible_at(
            accepted_start_at=accepted_start,
            planned_interval=timedelta(days=5),
            verified_completed_at=completed,
            minimum_post_completion_rest=timedelta(days=1),
        )

        self.assertEqual(timing.next_eligible_at, datetime(2026, 8, 9, 12, tzinfo=timezone.utc))
