"""Runtime-contract tests for PyScript wetness scripts using minimal HA doubles."""

import builtins
import datetime
import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).parents[1]
MODULES = ROOT / "src" / "pyscript" / "modules"
SCRIPTS = ROOT / "src" / "pyscript"


class FakeState:
    def __init__(self):
        self.values = {}
        self.attributes = {}

    def get(self, entity_id):
        return self.values.get(entity_id)

    def getattr(self, entity_id):
        return self.attributes.get(entity_id)

    def set(self, entity_id, value, attributes=None):
        self.values[entity_id] = value
        if attributes is not None:
            self.attributes[entity_id] = attributes

    def persist(self, entity_id, default_value=0.0):
        self.values.setdefault(entity_id, default_value)


class FakeLog:
    def warning(self, _message):
        pass


def passthrough_decorator(*_args, **_kwargs):
    return lambda function: function


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class WetnessScriptContractTests(unittest.TestCase):
    def setUp(self):
        self.state = FakeState()
        self.previous = {
            name: getattr(builtins, name, None)
            for name in ("state", "log", "time_trigger", "state_trigger", "service")
        }
        builtins.state = self.state
        builtins.log = FakeLog()
        builtins.time_trigger = passthrough_decorator
        builtins.state_trigger = passthrough_decorator
        builtins.service = passthrough_decorator
        sys.path.insert(0, str(MODULES))
        for name in ("gomow_config", "wetness_math", "wetness_store", "ground_wetness_score", "dew_accumulation"):
            sys.modules.pop(name, None)
        self.config = load_module("gomow_config", MODULES / "gomow_config.py")
        load_module("wetness_math", MODULES / "wetness_math.py")
        load_module("wetness_store", MODULES / "wetness_store.py")
        self.ground = load_module("ground_wetness_score", SCRIPTS / "ground_wetness_score.py")
        self.dew = load_module("dew_accumulation", SCRIPTS / "dew_accumulation.py")

    def tearDown(self):
        sys.path.remove(str(MODULES))
        for name, value in self.previous.items():
            if value is None:
                delattr(builtins, name)
            else:
                setattr(builtins, name, value)

    def test_decay_uses_the_prior_et_rate_not_the_new_reading(self):
        self.state.values[self.config.GROUND_WETNESS_BACKING_ENTITY] = 1.0
        self.ground.restore_ground_wetness_score()
        self.state.values[self.config.REFERENCE_ET_ENTITY] = 0.2
        self.ground.apply_reference_et_decay()  # establish 0.2 mm/h baseline

        attributes = self.state.attributes[self.config.GROUND_WETNESS_SCORE_ENTITY]
        attributes["decay_last_calculated"] = (
            datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)
        ).isoformat()
        self.state.values[self.config.REFERENCE_ET_ENTITY] = 0.4
        self.ground.apply_reference_et_decay()

        self.assertAlmostEqual(
            self.state.values[self.config.GROUND_WETNESS_SCORE_ENTITY], 0.8, places=2
        )
        self.assertEqual(
            self.state.attributes[self.config.GROUND_WETNESS_SCORE_ENTITY]["decay_rate_mm_h"],
            0.4,
        )

    def test_disabled_dew_model_never_adds_wetness(self):
        self.state.values.update(
            {
                self.config.OUTDOOR_TEMPERATURE_ENTITY: 12.0,
                self.config.OUTDOOR_HUMIDITY_ENTITY: 98.0,
                self.config.WIND_SPEED_ENTITY: 0.0,
                self.config.RAINING_ENTITY: "off",
            }
        )
        self.state.attributes[self.config.SUN_ENTITY] = {"elevation": -10.0}
        self.state.values[self.config.GROUND_WETNESS_SCORE_ENTITY] = 0.4
        self.state.attributes[self.config.GROUND_WETNESS_SCORE_ENTITY] = {
            "rain_score_mm": 0.4,
            "dew_score_mm": 0.0,
            "dew_last_calculated": (
                datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=2)
            ).isoformat(),
            "dew_rate_mm_h": 0.2,
        }

        self.dew.apply_dew_accumulation()

        self.assertAlmostEqual(
            self.state.values[self.config.GROUND_WETNESS_SCORE_ENTITY], 0.4, places=2
        )
        self.assertEqual(
            self.state.attributes[self.config.GROUND_WETNESS_SCORE_ENTITY]["dew_gate"],
            "feature_disabled",
        )


if __name__ == "__main__":
    unittest.main()
