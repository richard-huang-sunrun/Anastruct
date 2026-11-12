import unittest

from current_calculation import accumulate_sliding_snow_pairs, analyze_roof
from purlin_analysis import purlin_configuration


def _roof(**overrides):
    roof = {
        "id": "Roof 01A", "index": 0, "rooftype": "Shingle", "membertype": "Rafter", "memberspacing": 24,
        "roofheight": 15, "etor": 14, "pitch": 22, "ASCE": "7-16", "patio": False, "vaulted": False,
        "bending_stress_Fb": 900, "modulus_E": 1600000, "member_A": 8.25, "member_I": 20.8,
        "modulus_E_minimum": 580000, "shear_stress_Fv": 180, "specific_gravity_G": 0.5,
        "framing_breadth": 1.5, "framing_depth": 5.5, "snow_pre_pv": 20, "snow_post_pv": 20,
        "wind_pressure_down": 16, "wind_pressure_up": -16, "dead_load_roofing": 10, "dead_load_pv": 3,
        "live_load_pre_pv": 20, "live_load_post_pv": 0, "CF_B": 1.3, "CF_T": 1.3, "CF_C": 1.1, "Cr": 1.15,
        "CD_D": 0.9, "CD_L": 1.25, "CD_S": 1.15, "CD_W": 1.6, "overhang": 0,
        "mod_locations": [1, 10], "span_locations": [1.5, 12.5, 0, 0],
    }
    roof.update(overrides)
    return roof


class TestSlidingSnowFrom(unittest.TestCase):
    def test_receiving_roof_spec_applies_surcharge(self):
        ry = _roof(sliding_snow_from={"id": "Roof 02A", "etor": 20, "pitch": 30, "snow_pre_pv": 25, "snow_post_pv": 25})
        accumulate_sliding_snow_pairs([ry])
        self.assertGreater(ry["_sliding_snow_surcharge_psf"], 0)
        self.assertEqual(ry["_sliding_snow_received"][0]["rx_id"], "Roof 02A")

    def test_not_double_counted_with_source_side_pair(self):
        rx = _roof(id="Roof 02A", index=0, etor=20, pitch=30, sliding_snow=True,
                   sliding_snow_pairs=[{"rx": "Roof 02A", "ry": "Roof 01A"}])
        ry = _roof(index=1, sliding_snow_from={"id": "Roof 02A", "etor": 20, "pitch": 30})
        accumulate_sliding_snow_pairs([rx, ry])
        self.assertEqual(len(ry["_sliding_snow_received"]), 1)

    def test_bad_spec_is_ignored(self):
        ry = _roof(sliding_snow_from={"id": "Roof 02A", "etor": "abc"})
        accumulate_sliding_snow_pairs([ry])
        self.assertNotIn("_sliding_snow_surcharge_psf", ry)


class TestSlidingSnowLoad(unittest.TestCase):
    def test_surcharge_adds_to_snow_moment(self):
        base = analyze_roof(_roof(span_locations=[0, 14, 0, 0], mod_locations=[1, 13]), {})
        slid = _roof(span_locations=[0, 14, 0, 0], mod_locations=[1, 13],
                     _sliding_snow_surcharge_psf=15.0, _sliding_snow_strip_horizontal_ft=6.0)
        slid = analyze_roof(slid, {})
        for case in ("D + S", "D + 0.75(S + 0.6W)"):
            self.assertGreater(slid["load_cases"][case]["Max Moment (+)"], base["load_cases"][case]["Max Moment (+)"])
        self.assertGreater(slid["Max_DCR_D_S"], base["Max_DCR_D_S"])


class TestPurlinSpanLocations(unittest.TestCase):
    def test_explicit_span_locations_used_as_is(self):
        cfg = purlin_configuration({
            "attach_to_purlins": True, "purlin_spacing": 48, "purlin_breadth": 1.5, "purlin_depth": 5.5,
            "purlin_axis": "Strong", "purlin_span_locations": [1, 4, 3],
        })
        self.assertEqual(cfg["span_locations_ft"], [1.0, 4.0, 3.0, 0.0])
        self.assertTrue(cfg["configured"])
        self.assertTrue(cfg["has_spans"])

    def test_overhang_only_has_no_spans(self):
        cfg = purlin_configuration({"attach_to_purlins": True, "purlin_span_locations": [2, 0, 0, 0]})
        self.assertFalse(cfg["has_spans"])


class TestTjiFallback(unittest.TestCase):
    def test_unknown_tji_model_analysed_as_rafter(self):
        rafter = analyze_roof(_roof(), {})
        tji = analyze_roof(_roof(membertype="TJI", tji_model=999, tji_depth=11.875), {})
        self.assertIn("error", tji["detdb_flags"]["tji"])
        self.assertAlmostEqual(tji["Max_DCR_D_S"], rafter["Max_DCR_D_S"], places=6)

    def test_known_tji_uses_table(self):
        tji = analyze_roof(_roof(membertype="TJI", tji_model=210, tji_depth=11.875), {})
        self.assertIn("table_row", tji["detdb_flags"]["tji"])


if __name__ == "__main__":
    unittest.main()
