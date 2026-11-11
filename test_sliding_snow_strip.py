import unittest

from current_calculation import (
    _element_ids_in_horizontal_strip,
    accumulate_sliding_snow_pairs,
    compute_sliding_snow_p_add,
)


class TestSlidingSnowStrip(unittest.TestCase):
    def test_p_add_not_merged_into_roof_snow(self):
        rx = {
            "id": "R1",
            "sliding_snow": True,
            "etor": 20,
            "pitch": 30,
            "snow_pre_pv": 25,
            "snow_post_pv": 25,
        }
        ry = {"id": "R2", "index": 1, "etor": 25, "pitch": 25, "snow_pre_pv": 20, "snow_post_pv": 20}
        roofs = [rx, ry]
        rx["sliding_snow_pairs"] = [{"RX": 0, "RY": 1}]
        roofs[0]["_raw_snow_pre_pv"] = 25
        roofs[0]["_raw_snow_post_pv"] = 25
        accumulate_sliding_snow_pairs(roofs)
        self.assertGreater(float(ry.get("_sliding_snow_surcharge_psf", 0)), 0)
        self.assertEqual(ry["snow_pre_pv"], 20)
        self.assertEqual(ry["snow_post_pv"], 20)

    def test_strip_metadata(self):
        rx = {"sliding_snow": True, "etor": 10, "pitch": 20}
        ry = {"etor": 30, "pitch": 20}
        detail = compute_sliding_snow_p_add(rx, ry, 30.0)
        self.assertIsNotNone(detail)
        self.assertEqual(detail["strip_horizontal_ft"], 15.0)

    def test_elements_only_in_strip(self):
        coords = [[0, 0], [3, 1], [6, 2], [12, 4]]
        strip_ids = _element_ids_in_horizontal_strip(coords, strip_horizontal_m=4.0)
        self.assertEqual(strip_ids, [1])
