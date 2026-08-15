"""Pure next-mow timing for completed GoMow-owned jobs."""

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class NextMowTiming:
    """Auditable nominal and constrained next-job eligibility timestamps."""

    nominal_due_at: datetime
    completion_rest_until: datetime
    next_eligible_at: datetime


def calculate_next_eligible_at(
    *,
    accepted_start_at: datetime,
    planned_interval: timedelta,
    verified_completed_at: datetime,
    minimum_post_completion_rest: timedelta,
) -> NextMowTiming:
    """Preserve the job-start cadence while protecting the last-cut zone."""
    if planned_interval < timedelta(0):
        raise ValueError("planned_interval must not be negative")
    if minimum_post_completion_rest < timedelta(0):
        raise ValueError("minimum_post_completion_rest must not be negative")
    nominal_due_at = accepted_start_at + planned_interval
    completion_rest_until = verified_completed_at + minimum_post_completion_rest
    return NextMowTiming(
        nominal_due_at=nominal_due_at,
        completion_rest_until=completion_rest_until,
        next_eligible_at=max(nominal_due_at, completion_rest_until),
    )
