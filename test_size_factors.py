import contextlib
import io
import unittest
from unittest.mock import patch

import current_calculation as cc


class TestNdsSizeFactors(unittest.TestCase):
    def test_table_4a(self):
        cases = [
            (1.5, 3.5, (1.5, 1.5, 1.15)),
            (1.5, 5.5, (1.3, 1.3, 1.1)),
            (1.5, 7.25, (1.2, 1.2, 1.05)),
            (1.5, 9.25, (1.1, 1.1, 1.0)),
            (1.5, 11.25, (1.0, 1.0, 1.0)),
            (1.5, 13.25, (0.9, 0.9, 0.9)),
            (3.5, 7.25, (1.3, 1.2, 1.05)),
            (3.5, 11.25, (1.1, 1.0, 1.0)),
            (5.5, 7.5, (1.0, 1.0, 1.0)),
        ]
        for breadth, depth, expected in cases:
            with self.subTest(breadth=breadth, depth=depth):
                for got, want in zip(cc.nds_size_factors(breadth, depth), expected):
                    self.assertAlmostEqual(got, want)

    def test_timber_deeper_than_12_uses_formula(self):
        fb, ft, fc = cc.nds_size_factors(5.5, 13.5)
        self.assertAlmostEqual(fb, (12 / 13.5) ** (1 / 9))
        self.assertEqual((ft, fc), (1.0, 1.0))

    def test_capacity_receives_tension_factor_from_depth_when_not_sent(self):
        roof = {
            "id": "R", "rooftype": "Shingle", "membertype": "Rafter", "memberspacing": 16, "roofheight": 15,
            "etor": 14, "pitch": 20, "framing_breadth": 1.5, "framing_depth": 7.25,
            "snow_pre_pv": 0, "snow_post_pv": 0, "wind_pressure_down": 16, "wind_pressure_up": -16,
            "dead_load_roofing": 10, "dead_load_pv": 3, "live_load_pre_pv": 20, "live_load_post_pv": 0,
            "mod_locations": [1, 10], "span_locations": [0, 13, 0, 0],
        }
        real = cc.calculate_capacity
        seen = {}

        def spy(*args, **kwargs):
            seen["args"], seen["kwargs"] = args, kwargs
            return real(*args, **kwargs)

        with patch.object(cc, "calculate_capacity", spy), contextlib.redirect_stdout(io.StringIO()):
            cc.analyze_roof(roof, {"roofs": [roof]})
        self.assertAlmostEqual(seen["kwargs"]["CF_T"], 1.2)
        self.assertAlmostEqual(seen["args"][11], 1.2)   # CF_B
        self.assertAlmostEqual(seen["args"][12], 1.05)  # CF_C


if __name__ == "__main__":
    unittest.main()
