"""Pure, deterministic pending-job completion verification.

This module deliberately has no Home Assistant or PyScript dependency.  The
runtime layer supplies observed evidence; this module determines whether that
evidence is sufficient to complete the immutable GoMow job.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping


COMPLETION_PROGRESS_PCT = 95.0


@dataclass(frozen=True)
class PendingMowJob:
    """The immutable identity and target set of one requested mowing job."""

    job_id: str
    accepted_start_at: datetime
    map_identity: str
    target_zone_ids: tuple[int, ...]


@dataclass(frozen=True)
class CompletionVerification:
    """Outcome of evaluating one terminal mower observation."""

    completed: bool
    completed_zone_ids: tuple[int, ...]
    reason: str


def verify_terminal_completion(
    job: PendingMowJob,
    *,
    mower_state: str,
    task_progress_pct: float,
    zone_completed_at: Mapping[int, datetime | None],
    map_completed_at: datetime | None,
    has_interruption: bool,
) -> CompletionVerification:
    """Verify target-relative terminal completion without trusting map metadata.

    ``map_completed_at`` is intentionally accepted but not used as authority:
    a selected-zone job can succeed while a whole-map timestamp stays unset.
    """
    del map_completed_at
    if has_interruption:
        return CompletionVerification(False, (), "interrupted")
    if mower_state != "docked":
        return CompletionVerification(False, (), "terminal_state_not_docked")
    if task_progress_pct < COMPLETION_PROGRESS_PCT:
        return CompletionVerification(False, (), "task_progress_incomplete")

    completed = tuple(
        zone_id
        for zone_id in job.target_zone_ids
        if (completed_at := zone_completed_at.get(zone_id)) is not None
        and completed_at > job.accepted_start_at
    )
    if completed != job.target_zone_ids:
        return CompletionVerification(False, completed, "target_zone_evidence_incomplete")
    return CompletionVerification(True, completed, "target_zones_verified")
