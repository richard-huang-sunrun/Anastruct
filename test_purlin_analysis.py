import unittest

from purlin_analysis import (
    build_purlin_roof_overlay,
    parse_length_ft,
    purlin_configuration,
    run_purlin_subanalysis,
)


class TestPurlinAnalysis(unittest.TestCase):
    def test_parse_length_ft(self):
        self.assertAlmostEqual(parse_length_ft("4' 6\""), 4.5)
        self.assertAlmostEqual(parse_length_ft(8), 8.0)

    def test_configuration_missing_spans_fails_gate(self):
        roof = {
            "attachToPurlins": True,
            "purlin_spacing": 45,
            "purlin_size": "2x4",
            "purlin_axis": "Strong",
            "purlin_span_1": "0' 0\"",
            "purlin_span_2": "0' 0\"",
            "CF_B": 1.1,
        }
        cfg = purlin_configuration(roof)
        self.assertTrue(cfg["configured"])
        self.assertFalse(cfg["has_spans"])

    def test_flat_axis_swaps_depth_breadth(self):
        roof = {
            "attachToPurlins": True,
            "purlin_spacing": 48,
            "purlin_breadth": 1.5,
            "purlin_depth": 3.5,
            "purlin_axis": "Flat",
            "purlin_span_1": 6,
            "CF_B": 1.0,
        }
        cfg = purlin_configuration(roof)
        overlay = build_purlin_roof_overlay(roof, cfg)
        self.assertEqual(overlay["framing_breadth"], 3.5)
        self.assertEqual(overlay["framing_depth"], 1.5)
        self.assertEqual(overlay["CF_B"], 1.0)

    def test_no_attach_returns_none(self):
        roof = {"purlin_spacing": 45, "purlin_size": "2x4"}
        self.assertIsNone(run_purlin_subanalysis(roof, {}, lambda r, t: {}))

    def test_missing_spans_returns_error_block(self):
        roof = {
            "attachToPurlins": True,
            "purlin_spacing": 45,
            "purlin_size": "2x4",
            "purlin_axis": "Strong",
        }

        block = run_purlin_subanalysis(roof, {}, lambda r, t: {"ok": True})
        self.assertIsNotNone(block)
        self.assertFalse(block["performed"])
        self.assertIn("error", block)


if __name__ == "__main__":
    unittest.main()
