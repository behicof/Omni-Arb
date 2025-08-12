import unittest
from hcope import hcope_gate


class TestHCOPEGate(unittest.TestCase):
    def test_lcb_pass(self):
        result = hcope_gate(1.5, 0.4)  # Expected: pass, since LCB > threshold
        self.assertTrue(result)

    def test_lcb_fail(self):
        result = hcope_gate(0.8, 0.6)  # Expected: fail, since LCB < threshold
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()

