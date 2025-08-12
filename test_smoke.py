"""Basic tests for connectivity utilities."""
import unittest

from binance import compute_net_edge
from okx import OKXClient


class UtilTest(unittest.TestCase):
    def test_compute_net_edge_clamps(self) -> None:
        self.assertEqual(compute_net_edge(0.05, 0.01, -0.01), 0.01)
        self.assertEqual(compute_net_edge(-0.05, 0.01, -0.01), -0.01)
        self.assertEqual(compute_net_edge(0.005, 0.01, -0.01), 0.005)

    def test_okx_demo_header(self) -> None:
        demo = OKXClient(demo=True)
        self.assertEqual(demo.session.headers.get("x-simulated-trading"), "1")
        live = OKXClient(demo=False)
        self.assertIsNone(live.session.headers.get("x-simulated-trading"))


if __name__ == "__main__":
    unittest.main()
