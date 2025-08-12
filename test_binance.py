import logging
from unittest import TestCase, mock

import rsa

from binance import BinanceFuturesClient

# generate a small RSA key for tests
_pub, _priv = rsa.newkeys(512)
PRIVATE_KEY_PEM = _priv.save_pkcs1().decode()


class BinanceClientTest(TestCase):
    def setUp(self):
        self.client = BinanceFuturesClient("key", PRIVATE_KEY_PEM)

    def _mock_response(self, json_data, headers=None, status=200):
        response = mock.Mock()
        response.status_code = status
        response.json.return_value = json_data
        response.headers = headers or {}
        return response

    @mock.patch("requests.Session.request")
    def test_get_position_mode_updates_state_and_rate_limits(self, mock_req):
        headers = {"X-MBX-USED-WEIGHT-1M": "5"}
        mock_req.return_value = self._mock_response({"dualSidePosition": True}, headers)
        mode = self.client.get_position_mode()
        self.assertTrue(mode)
        self.assertEqual(self.client.rate_limits["X-MBX-USED-WEIGHT-1M"], "5")
        mock_req.assert_called_with(
            "GET", "https://fapi.binance.com/fapi/v1/positionSide/dual", params=mock.ANY
        )

    @mock.patch("requests.Session.request")
    def test_set_position_mode(self, mock_req):
        mock_req.return_value = self._mock_response({"code": 200})
        self.client.set_position_mode(True)
        self.assertTrue(self.client.hedge_mode)
        mock_req.assert_called()

    @mock.patch("requests.Session.request")
    def test_place_order_test_endpoint(self, mock_req):
        mock_req.return_value = self._mock_response({"code": 200})
        self.client.place_order(
            symbol="BTCUSDT",
            side="BUY",
            order_type="LIMIT",
            quantity=1,
            price=10,
            live=False,
        )
        args, kwargs = mock_req.call_args
        self.assertIn("/fapi/v1/order/test", args[1])

    @mock.patch("requests.Session.request")
    def test_gtx_rejection_logging(self, mock_req):
        mock_req.return_value = self._mock_response({"code": -5022, "msg": "Post only"})
        with self.assertLogs(level="WARNING") as log:
            self.client.place_order(
                symbol="BTCUSDT",
                side="BUY",
                order_type="LIMIT",
                quantity=1,
                price=10,
                time_in_force="GTX",
            )
        self.assertIn("GTX order rejected", "".join(log.output))

    @mock.patch("requests.Session.request")
    def test_position_side_auto_in_hedge_mode(self, mock_req):
        mock_req.return_value = self._mock_response({"code": 200})
        self.client.hedge_mode = True
        self.client.place_order(
            symbol="ETHUSDT",
            side="SELL",
            order_type="MARKET",
            quantity=1,
        )
        called_params = mock_req.call_args.kwargs["params"]
        self.assertEqual(called_params["positionSide"], "SHORT")
