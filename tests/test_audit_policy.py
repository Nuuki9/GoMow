"""Unit tests for noise-controlled GoMow audit-event selection."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).parents[1] / "src" / "pyscript" / "modules" / "audit_policy.py"
SPEC = spec_from_file_location("audit_policy", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load audit-policy module: {MODULE_PATH}")
audit_policy = module_from_spec(SPEC)
SPEC.loader.exec_module(audit_policy)


class AuditPolicyTests(unittest.TestCase):
    def test_unchanged_decision_evaluation_does_not_emit_an_audit_event(self):
        trace = {
            "recommendation": False,
            "state": "BLOCKED",
            "primary_reason_code": "WET_SURFACE",
        }

        event = audit_policy.select_decision_audit_event(trace, trace)

        self.assertIsNone(event)

    def test_primary_reason_change_emits_one_explanatory_event(self):
        previous = {
            "recommendation": False,
            "state": "BLOCKED",
            "primary_reason_code": "WET_SURFACE",
        }
        current = {
            "recommendation": False,
            "state": "NOT_READY",
            "primary_reason_code": "INPUT_STALE",
        }

        event = audit_policy.select_decision_audit_event(previous, current)

        self.assertEqual(event.event_code, "DECISION_REASON_CHANGED")
        self.assertEqual(event.severity, "warning")
        self.assertEqual(event.primary_reason_code, "INPUT_STALE")


if __name__ == "__main__":
    unittest.main()
