"""Contract tests for GoMow's central installation configuration module."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).parents[1] / "src" / "pyscript" / "modules" / "gomow_config.py"
SPEC = spec_from_file_location("gomow_config", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load GoMow configuration module: {MODULE_PATH}")
gomow_config = module_from_spec(SPEC)
SPEC.loader.exec_module(gomow_config)


class CentralConfigurationContractTests(unittest.TestCase):
    def test_wetness_scripts_have_one_shared_definition_for_common_entity_ids(self):
        required = (
            "OUTDOOR_TEMPERATURE_ENTITY",
            "OUTDOOR_HUMIDITY_ENTITY",
            "WIND_SPEED_ENTITY",
            "SOLAR_RADIATION_ENTITY",
            "PRESSURE_ENTITY",
            "RAINING_ENTITY",
            "SUN_ENTITY",
            "REFERENCE_ET_ENTITY",
            "GROUND_WETNESS_BACKING_ENTITY",
            "GROUND_WETNESS_SCORE_ENTITY",
        )
        for name in required:
            with self.subTest(name=name):
                self.assertIsInstance(getattr(gomow_config, name), str)
                self.assertTrue(getattr(gomow_config, name))

    def test_wetness_model_uses_the_agreed_1_point_5_mm_maximum(self):
        self.assertEqual(gomow_config.WETNESS_MAX_SCORE_MM, 1.5)

    def test_hysteresis_thresholds_remain_unset_until_empirical_calibration(self):
        self.assertIsNone(gomow_config.DRY_ENTER_THRESHOLD_MM)
        self.assertIsNone(gomow_config.WET_ENTER_THRESHOLD_MM)

    def test_reference_et_has_an_explicit_hourly_recalculation_cadence(self):
        self.assertEqual(gomow_config.REFERENCE_ET_RECALCULATION_TRIGGER, "period(1h)")


if __name__ == "__main__":
    unittest.main()
