import contextlib
import io
import unittest
from unittest.mock import patch

import current_calculation as cc


def roof(**extra):
    r = {
        "id": "R", "rooftype": "Shingle", "membertype": "Rafter", "memberspacing": 16, "roofheight": 15,
        "etor": 14, "pitch": 20, "framing_breadth": 1.5, "framing_depth": 7.25,
        "snow_pre_pv": 0, "snow_post_pv": 0, "wind_pressure_down": 16, "wind_pressure_up": -16,
        "dead_load_roofing": 10, "dead_load_pv": 3, "live_load_pre_pv": 20, "live_load_post_pv": 0,
        "mod_locations": [1, 10], "span_locations": [0, 13, 0, 0],
    }
    r.update(extra)
    return r


def run(r):
    real = cc.calculate_capacity
    seen = {}

    def spy(*args, **kwargs):
        seen["args"] = args
        return real(*args, **kwargs)

    with patch.object(cc, "calculate_capacity", spy), contextlib.redirect_stdout(io.StringIO()):
        result = cc.analyze_roof(r, {"roofs": [r]})
    return result, seen["args"]


class TestSpeciesTable(unittest.TestCase):
    def test_lookup_and_aliases(self):
        self.assertEqual(cc.sawn_lumber_values("Spruce-Pine-Fir", "No. 2"),
                         ("SPF", "#2", (875, 1400000, 510000, 135, 0.42)))
        self.assertEqual(cc.sawn_lumber_values("Southern Pine", "SS")[2], (2350, 1800000, 660000, 175, 0.55))
        self.assertIsNone(cc.sawn_lumber_values("DFL", "Utility"))
        self.assertIsNone(cc.sawn_lumber_values(None, "#2"))

    def test_species_grade_override_numeric_values(self):
        result, args = run(roof(framing_species="SPF", framing_grade="#2", bending_stress_Fb=900,
                                shear_stress_Fv=180, modulus_E=1600000, material_source="state default (MA)"))
        # calculate_capacity(spans, spacing, depth, breadth, pitch, overhang, E, Emin, Fb, Fv, G, ...)
        self.assertEqual(args[6:11], (1400000.0, 510000.0, 875.0, 135.0, 0.42))
        m = result["material"]
        self.assertEqual((m["species"], m["grade"], m["values_from"], m["selection"]),
                         ("SPF", "#2", "species/grade table", "state default (MA)"))
        self.assertEqual((m["Fb"], m["Fv"], m["E"]), (875.0, 135.0, 1400000.0))

    def test_without_species_uses_payload_values(self):
        result, args = run(roof(bending_stress_Fb=1100, shear_stress_Fv=175))
        self.assertEqual(args[8:10], (1100.0, 175.0))
        self.assertEqual(result["material"]["values_from"], "payload values")

    def test_weaker_species_raises_dcr(self):
        dfl, _ = run(roof(framing_species="DFL", framing_grade="#2"))
        spf, _ = run(roof(framing_species="SPF", framing_grade="#2"))
        self.assertAlmostEqual(spf["Max_DCR_D"] / dfl["Max_DCR_D"], 900 / 875, places=3)


if __name__ == "__main__":
    unittest.main()
