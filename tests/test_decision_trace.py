"""Unit tests for GoMow's canonical decision-explainability trace."""

from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).parents[1] / "src" / "pyscript" / "modules" / "decision_trace.py"
SPEC = spec_from_file_location("decision_trace", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load decision-trace module: {MODULE_PATH}")
decision_trace = module_from_spec(SPEC)
SPEC.loader.exec_module(decision_trace)


class DecisionTraceTests(unittest.TestCase):
    def test_trace_retains_all_failed_gates_while_prioritising_stale_input(self):
        evaluated_at = datetime(2026, 8, 4, 16, 9, 11, tzinfo=timezone.utc)

        trace = decision_trace.build_decision_trace(
            gates={"inputs_healthy": False, "ground_dry": False, "mow_due": True},
            blocking_reason_codes=("WET_SURFACE", "INPUT_STALE"),
            factors={
                "wetness": {"value": 1.2, "unit": "mm", "valid": True},
                "reference_et": {"value": None, "unit": "mm/h", "valid": False},
            },
            model_version="0.1.0-shadow",
            evaluated_at=evaluated_at,
        )

        self.assertEqual(trace["state"], "NOT_READY")
        self.assertFalse(trace["recommendation"])
        self.assertEqual(trace["primary_reason_code"], "INPUT_STALE")
        self.assertEqual(trace["blocking_reason_codes"], ("INPUT_STALE", "WET_SURFACE"))
        self.assertEqual(trace["gates"]["mow_due"], True)
        self.assertEqual(trace["factors"]["reference_et"]["valid"], False)
        self.assertEqual(trace["evaluated_at"], "2026-08-04T16:09:11+00:00")
        self.assertEqual(trace["trace_schema_version"], "1")


if __name__ == "__main__":
    unittest.main()
