"""Unit tests for pure GoMow wetness-model maths.

These tests deliberately avoid Home Assistant and PyScript runtime APIs so the
model invariants can be checked before a change is deployed to a real mower.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).parents[1] / "src" / "pyscript" / "modules" / "wetness_math.py"
SPEC = spec_from_file_location("wetness_math", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load wetness maths module: {MODULE_PATH}")
wetness_math = module_from_spec(SPEC)
SPEC.loader.exec_module(wetness_math)


class ApportionDecayTests(unittest.TestCase):
    def test_decay_is_apportioned_to_existing_rain_and_dew_shares(self):
        rain, dew = wetness_math.apportion_decay(
            rain_score=1.2,
            dew_score=0.3,
            decay_amount=0.6,
        )

        self.assertAlmostEqual(rain, 0.72)
        self.assertAlmostEqual(dew, 0.18)
        self.assertAlmostEqual(rain + dew, 0.9)

    def test_decay_cannot_make_a_component_or_total_negative(self):
        rain, dew = wetness_math.apportion_decay(
            rain_score=0.2,
            dew_score=0.1,
            decay_amount=9.0,
        )

        self.assertEqual((rain, dew), (0.0, 0.0))

    def test_zero_total_remains_zero(self):
        self.assertEqual(
            wetness_math.apportion_decay(0.0, 0.0, 0.4),
            (0.0, 0.0),
        )

    def test_decay_preserves_unattributed_restored_wetness(self):
        components = wetness_math.apportion_decay_components(
            (0.2, 0.1, 0.7), decay_amount=0.2
        )
        self.assertEqual(len(components), 3)
        self.assertAlmostEqual(components[0], 0.16)
        self.assertAlmostEqual(components[1], 0.08)
        self.assertAlmostEqual(components[2], 0.56)


class DewMathTests(unittest.TestCase):
    def test_dew_intensity_is_full_below_full_spread_and_zero_above_zero_spread(self):
        self.assertEqual(wetness_math.dew_intensity(0.5, 1.0, 3.5), 1.0)
        self.assertEqual(wetness_math.dew_intensity(4.0, 1.0, 3.5), 0.0)

    def test_dew_intensity_interpolates_linearly_between_spread_limits(self):
        self.assertAlmostEqual(wetness_math.dew_intensity(2.25, 1.0, 3.5), 0.5)

    def test_dew_point_is_not_above_air_temperature_for_valid_relative_humidity(self):
        dew_point = wetness_math.dew_point_celsius(15.0, 80.0)
        self.assertLessEqual(dew_point, 15.0)
        self.assertGreater(dew_point, 0.0)


if __name__ == "__main__":
    unittest.main()
