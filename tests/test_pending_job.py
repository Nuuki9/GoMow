"""Pure completion verification for GoMow's immutable pending-mow jobs."""

from datetime import datetime, timedelta, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).parents[1] / "src" / "pyscript" / "modules" / "pending_job.py"
SPEC = spec_from_file_location("pending_job", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load pending-job module: {MODULE_PATH}")
pending_job = module_from_spec(SPEC)
SPEC.loader.exec_module(pending_job)
PendingMowJob = pending_job.PendingMowJob
verify_terminal_completion = pending_job.verify_terminal_completion


UTC = timezone.utc
STARTED = datetime(2026, 8, 4, 13, 22, 7, tzinfo=UTC)


class PendingJobCompletionTests(unittest.TestCase):
    def test_selected_two_zone_job_completes_without_map_completion(self):
        """Fresh selected-zone evidence, not map completion, is authoritative."""
        job = PendingMowJob(
            job_id="gomow-test-1",
            accepted_start_at=STARTED,
            map_identity="2",
            target_zone_ids=(6, 7),
        )

        result = verify_terminal_completion(
            job,
            mower_state="docked",
            task_progress_pct=100.0,
            zone_completed_at={
                6: STARTED + timedelta(minutes=19),
                7: STARTED + timedelta(hours=2, minutes=46),
                # Main was deliberately not selected and must not be required.
                8: None,
            },
            map_completed_at=None,
            has_interruption=False,
        )

        self.assertTrue(result.completed)
        self.assertEqual(result.completed_zone_ids, (6, 7))
        self.assertEqual(result.reason, "target_zones_verified")

    def test_non_docked_terminal_state_cannot_complete_job(self):
        job = PendingMowJob("gomow-test-2", STARTED, "2", (6, 7))

        result = verify_terminal_completion(
            job,
            mower_state="mowing",
            task_progress_pct=100.0,
            zone_completed_at={
                6: STARTED + timedelta(minutes=19),
                7: STARTED + timedelta(hours=2, minutes=46),
            },
            map_completed_at=None,
            has_interruption=False,
        )

        self.assertFalse(result.completed)
        self.assertEqual(result.reason, "terminal_state_not_docked")

    def test_interrupted_job_cannot_complete_after_docking(self):
        job = PendingMowJob("gomow-test-3", STARTED, "2", (6, 7))

        result = verify_terminal_completion(
            job,
            mower_state="docked",
            task_progress_pct=100.0,
            zone_completed_at={
                6: STARTED + timedelta(minutes=19),
                7: STARTED + timedelta(hours=2, minutes=46),
            },
            map_completed_at=None,
            has_interruption=True,
        )

        self.assertFalse(result.completed)
        self.assertEqual(result.reason, "interrupted")

    def test_missing_fresh_target_zone_evidence_blocks_completion(self):
        job = PendingMowJob("gomow-test-4", STARTED, "2", (6, 7))

        result = verify_terminal_completion(
            job,
            mower_state="docked",
            task_progress_pct=100.0,
            zone_completed_at={
                6: STARTED + timedelta(minutes=19),
                7: None,
            },
            map_completed_at=None,
            has_interruption=False,
        )

        self.assertFalse(result.completed)
        self.assertEqual(result.completed_zone_ids, (6,))
        self.assertEqual(result.reason, "target_zone_evidence_incomplete")

    def test_subthreshold_task_progress_blocks_completion(self):
        job = PendingMowJob("gomow-test-5", STARTED, "2", (6, 7))

        result = verify_terminal_completion(
            job,
            mower_state="docked",
            task_progress_pct=94.9,
            zone_completed_at={
                6: STARTED + timedelta(minutes=19),
                7: STARTED + timedelta(hours=2, minutes=46),
            },
            map_completed_at=None,
            has_interruption=False,
        )

        self.assertFalse(result.completed)
        self.assertEqual(result.reason, "task_progress_incomplete")

    def test_recovery_never_retries_an_unconfirmed_start_request(self):
        job = PendingMowJob("gomow-test-recovery", STARTED, "2", (6, 7))

        recovery = pending_job.reconcile_recovery(
            job,
            prior_state="START_REQUESTED",
            mower_state="docked",
        )

        self.assertEqual(recovery.state, "RECOVERY_UNCONFIRMED")
        self.assertFalse(recovery.dispatch_allowed)
        self.assertEqual(recovery.reason, "start_unconfirmed_no_retry")

    def test_recovery_resumes_monitoring_confirmed_active_mower(self):
        job = PendingMowJob("gomow-test-active-recovery", STARTED, "2", (6, 7))

        recovery = pending_job.reconcile_recovery(
            job,
            prior_state="MOWING",
            mower_state="mowing",
        )

        self.assertEqual(recovery.state, "MOWING")
        self.assertFalse(recovery.dispatch_allowed)
        self.assertEqual(recovery.reason, "active_mower_confirmed")

    def test_pending_job_round_trips_as_an_immutable_persisted_record(self):
        job = PendingMowJob("gomow-test-persist", STARTED, "2", (6, 7))

        restored = PendingMowJob.from_record(job.to_record())

        self.assertEqual(restored, job)
        self.assertEqual(restored.target_zone_ids, (6, 7))


if __name__ == "__main__":
    unittest.main()
