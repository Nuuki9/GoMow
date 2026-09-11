"""Tests for Netatmo rolling-hour rain ingestion."""

from datetime import datetime, timedelta, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).parents[1] / "src" / "pyscript" / "modules" / "rain_accumulation.py"
SPEC = spec_from_file_location("rain_accumulation", MODULE_PATH)
assert SPEC and SPEC.loader
rain_accumulation = module_from_spec(SPEC)
SPEC.loader.exec_module(rain_accumulation)


UTC = timezone.utc
OBSERVED_AT = datetime(2026, 8, 29, 12, 13, 15, tzinfo=UTC)


class RollingHourRainIngestionTests(unittest.TestCase):
    def test_fresh_positive_rolling_hour_observation_saturates_surface_wetness(self):
        outcome = rain_accumulation.ingest_rolling_hour_observation(
            observation_mm=0.303,
            observed_at=OBSERVED_AT,
            prior_checkpoint=None,
            evaluated_at=OBSERVED_AT + timedelta(minutes=1),
            maximum_age=timedelta(minutes=15),
        )

        self.assertEqual(outcome.action, "saturate")
        self.assertEqual(outcome.reason, "fresh_positive_rolling_hour_rain")
        self.assertTrue(outcome.source_healthy)
        self.assertEqual(outcome.next_checkpoint, OBSERVED_AT)

    def test_replayed_observation_timestamp_is_ignored_without_resaturating(self):
        outcome = rain_accumulation.ingest_rolling_hour_observation(
            observation_mm=0.303,
            observed_at=OBSERVED_AT,
            prior_checkpoint=OBSERVED_AT,
            evaluated_at=OBSERVED_AT + timedelta(minutes=1),
            maximum_age=timedelta(minutes=15),
        )

        self.assertEqual(outcome.action, "none")
        self.assertEqual(outcome.reason, "rain_observation_duplicate")
        self.assertTrue(outcome.source_healthy)
        self.assertEqual(outcome.next_checkpoint, OBSERVED_AT)

    def test_stale_observation_fails_closed_without_advancing_checkpoint(self):
        old_checkpoint = OBSERVED_AT - timedelta(minutes=30)
        outcome = rain_accumulation.ingest_rolling_hour_observation(
            observation_mm=0.303,
            observed_at=OBSERVED_AT,
            prior_checkpoint=old_checkpoint,
            evaluated_at=OBSERVED_AT + timedelta(minutes=16),
            maximum_age=timedelta(minutes=15),
        )

        self.assertEqual(outcome.action, "none")
        self.assertEqual(outcome.reason, "rain_source_stale")
        self.assertFalse(outcome.source_healthy)
        self.assertEqual(outcome.next_checkpoint, old_checkpoint)

    def test_fresh_zero_records_window_expiry_without_adding_wetness(self):
        outcome = rain_accumulation.ingest_rolling_hour_observation(
            observation_mm=0.0,
            observed_at=OBSERVED_AT,
            prior_checkpoint=None,
            evaluated_at=OBSERVED_AT + timedelta(minutes=1),
            maximum_age=timedelta(minutes=15),
        )

        self.assertEqual(outcome.action, "none")
        self.assertEqual(outcome.reason, "rolling_hour_window_expired")
        self.assertTrue(outcome.source_healthy)
        self.assertEqual(outcome.next_checkpoint, OBSERVED_AT)

    def test_invalid_or_negative_value_fails_closed_without_advancing_checkpoint(self):
        checkpoint = OBSERVED_AT - timedelta(minutes=2)
        outcome = rain_accumulation.ingest_rolling_hour_observation(
            observation_mm=-0.1,
            observed_at=OBSERVED_AT,
            prior_checkpoint=checkpoint,
            evaluated_at=OBSERVED_AT + timedelta(minutes=1),
            maximum_age=timedelta(minutes=15),
        )

        self.assertEqual(outcome.action, "none")
        self.assertEqual(outcome.reason, "rain_value_invalid")
        self.assertFalse(outcome.source_healthy)
        self.assertEqual(outcome.next_checkpoint, checkpoint)


if __name__ == "__main__":
    unittest.main()
