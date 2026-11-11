import unittest

from current_calculation import _lateral_stability_cl_neg, calculate_capacity


class TestTjiCapacityFactors(unittest.TestCase):
    def test_cl_neg_forced_one_for_tji(self):
        cl = _lateral_stability_cl_neg(14.0, 1.5, 5000.0, 1000.0, is_tji=True)
        self.assertEqual(cl, 1.0)

    def test_calculate_capacity_tji_overrides_cf_b_and_cr(self):
        cap = calculate_capacity(
            spans=[20, 0, 0, 0],
            spacing=24,
            depth=14.0,
            breadth=1.5,
            pitch=18,
            overhang=0,
            E=1600000,
            Emin=580000,
            Fb=900,
            Fv=180,
            G=0.5,
            CF_B=1.3,
            CF_C=1.1,
            Cr=1.15,
            CD_D=0.9,
            CD_L=1.25,
            CD_S=1.15,
            CD_W=1.6,
            is_tji=True,
        )
        # Fb_prime_neg_D uses CF_B and Cr; with is_tji both are 1.0 and CL_neg is 1.0
        expected_neg_d = 900 * 0.9 * 1.0 * 1.0 * 1.0
        self.assertAlmostEqual(cap["Fb_prime_neg_D"], expected_neg_d, places=4)


if __name__ == "__main__":
    unittest.main()
