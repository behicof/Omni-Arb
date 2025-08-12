import unittest
from unittest.mock import patch

from exchange.binance import BinanceExchange


class TestBinanceHedgeRules(unittest.TestCase):
    def setUp(self):
        self.client = BinanceExchange()

    def test_build_order_hedge_mode(self):
        order = self.client.build_order("BUY", 1, hedge_mode=True)
        self.assertEqual(order["positionSide"], "LONG")

        order = self.client.build_order("SELL", 1, hedge_mode=True)
        self.assertEqual(order["positionSide"], "SHORT")

        order = self.client.build_order("BUY", 1, reduce_only=True, hedge_mode=True)
        self.assertEqual(order["positionSide"], "SHORT")

        order = self.client.build_order("SELL", 1, reduce_only=True, hedge_mode=True)
        self.assertEqual(order["positionSide"], "LONG")

        with self.assertRaises(ValueError):
            self.client.build_order("BUY", 1, hedge_mode=True, position_side="SHORT")

    def test_build_order_one_way(self):
        order = self.client.build_order("BUY", 1, hedge_mode=False)
        self.assertNotIn("positionSide", order)

        with self.assertRaises(ValueError):
            self.client.build_order("BUY", 1, hedge_mode=False, position_side="LONG")

    def test_reduce_only_gtx(self):
        with self.assertRaises(ValueError):
            self.client.build_order("SELL", 1, reduce_only=True, hedge_mode=False, time_in_force="GTX")

    @patch("exchange.binance.requests.get")
    def test_get_position_mode(self, mock_get):
        mock_get.return_value.json.return_value = {"dualSidePosition": True}
        mock_get.return_value.raise_for_status.return_value = None
        mode = self.client.get_position_mode()
        self.assertTrue(mode)
        mock_get.assert_called_once()

    @patch("exchange.binance.requests.post")
    def test_set_position_mode(self, mock_post):
        mock_post.return_value.json.return_value = {"code": 200}
        mock_post.return_value.raise_for_status.return_value = None
        resp = self.client.set_position_mode(True)
        self.assertEqual(resp, {"code": 200})
        mock_post.assert_called_once()


if __name__ == "__main__":
    unittest.main()
