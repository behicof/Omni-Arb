import os
import unittest
from unittest.mock import patch, MagicMock

import order

EXCHANGE_INFO = {
    "symbols": [
        {
            "filters": [
                {"filterType": "LOT_SIZE", "stepSize": "0.001", "minQty": "0.001"},
                {"filterType": "MIN_NOTIONAL", "notional": "5"},
            ]
        }
    ]
}


class OrderWrapperTest(unittest.TestCase):
    def setUp(self):
        os.environ["BINANCE_API_KEY"] = "test"

    @patch("order.requests.post")
    @patch("order.requests.get")
    def test_dry_run(self, mock_get, mock_post):
        mock_get.return_value.json.return_value = EXCHANGE_INFO
        mock_get.return_value.raise_for_status.return_value = None
        mock_post.return_value.json.return_value = {"status": "ok"}
        mock_post.return_value.raise_for_status.return_value = None
        os.environ["LIVE"] = "0"
        order.send_order({"symbol": "BTCUSDT", "side": "BUY", "quantity": 0.001, "price": 30000, "timeInForce": "GTC"})
        self.assertIn("/fapi/v1/order/test", mock_post.call_args[0][0])

    @patch("order.requests.post")
    @patch("order.requests.get")
    def test_live(self, mock_get, mock_post):
        mock_get.return_value.json.return_value = EXCHANGE_INFO
        mock_get.return_value.raise_for_status.return_value = None
        mock_post.return_value.json.return_value = {"status": "ok"}
        mock_post.return_value.raise_for_status.return_value = None
        os.environ["LIVE"] = "1"
        order.send_order({"symbol": "BTCUSDT", "side": "BUY", "quantity": 0.001, "price": 30000, "timeInForce": "GTC"})
        self.assertIn("/fapi/v1/order", mock_post.call_args[0][0])


if __name__ == "__main__":
    unittest.main()
