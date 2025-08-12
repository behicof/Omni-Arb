import unittest
from unittest.mock import patch

from order import BinanceOrderClient

class OrderWrapperTest(unittest.TestCase):
    @patch('order.requests.post')
    def test_dry_run_endpoint(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"result": "ok"}
        client = BinanceOrderClient(live=0)
        client.place_order('BTCUSDT', 'BUY', 1, price=100, tif='GTC')
        called_url = mock_post.call_args[0][0]
        self.assertIn('/fapi/v1/order/test', called_url)

    @patch('order.requests.post')
    def test_live_endpoint(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"result": "ok"}
        client = BinanceOrderClient(live=1)
        client.place_order('BTCUSDT', 'BUY', 1, price=100, tif='GTC')
        called_url = mock_post.call_args[0][0]
        self.assertEqual(called_url, 'https://fapi.binance.com/fapi/v1/order')

    def test_invalid_tif(self):
        client = BinanceOrderClient()
        with self.assertRaises(ValueError):
            client.place_order('BTCUSDT', 'BUY', 1, tif='DAY')

    def test_gtx_requires_price(self):
        client = BinanceOrderClient()
        with self.assertRaises(ValueError):
            client.place_order('BTCUSDT', 'BUY', 1, tif='GTX')

if __name__ == '__main__':
    unittest.main()
