import os
import sys
sys.path.append(os.path.dirname(__file__))
import json
import unittest
import datetime
import asyncio
from unittest.mock import patch, Mock

from binance_ws import process_message, funding_rates
from binance_rest import (
    place_order,
    BinanceAPIError,
    funding_pnl_report,
    set_position_mode,
    get_position_mode,
)

class TestBinanceWS(unittest.TestCase):
    def test_process_message_logs_and_caches(self):
        tmpdir = "data/ticks/test"
        os.makedirs(tmpdir, exist_ok=True)
        msg = json.dumps({"stream": "!markPrice@arr@1s", "data": [{"s": "BTCUSDT", "r": "0.0001"}]})
        asyncio.run(process_message(msg, log_dir=tmpdir))
        date_str = datetime.datetime.utcnow().strftime("%Y%m%d")
        log_path = os.path.join(tmpdir, f"{date_str}.log")
        self.assertTrue(os.path.exists(log_path))
        with open(log_path, encoding="utf-8") as fh:
            content = fh.read()
            self.assertIn("BTCUSDT", content)
        self.assertAlmostEqual(funding_rates["BTCUSDT"], 0.0001)

class TestBinanceREST(unittest.TestCase):
    @patch("binance_rest.requests.post")
    def test_order_test_called_when_not_live(self, mock_post):
        mock_post.return_value = Mock(json=lambda: {})
        place_order({"symbol": "BTCUSDT"}, live=False)
        url = mock_post.call_args[0][0]
        self.assertIn("/order/test", url)

    @patch("binance_rest.requests.post")
    def test_ioc_parameter(self, mock_post):
        mock_post.return_value = Mock(json=lambda: {})
        place_order({"symbol": "BTCUSDT", "timeInForce": "IOC"})
        params = mock_post.call_args.kwargs["params"]
        self.assertEqual(params["timeInForce"], "IOC")

    @patch("binance_rest.requests.post")
    def test_gtx_reject_raises_error(self, mock_post):
        mock_post.return_value = Mock(json=lambda: {"code": -5022, "msg": "error"})
        with self.assertRaises(BinanceAPIError) as ctx:
            place_order({"symbol": "BTCUSDT", "timeInForce": "GTX"})
        self.assertEqual(ctx.exception.code, -5022)

    @patch("binance_rest.requests.post")
    def test_reduce_only_not_allowed(self, mock_post):
        mock_post.return_value = Mock(json=lambda: {"code": -2022, "msg": "error"})
        with self.assertRaises(BinanceAPIError) as ctx:
            place_order({"symbol": "BTCUSDT", "reduceOnly": True})
        self.assertEqual(ctx.exception.code, -2022)

    @patch("binance_rest.requests.post")
    @patch("binance_rest.requests.get")
    def test_position_mode(self, mock_get, mock_post):
        mock_post.return_value = Mock(json=lambda: {"code": 200})
        mock_get.return_value = Mock(json=lambda: {"dualSidePosition": True})
        set_position_mode(True)
        post_data = mock_post.call_args.kwargs["data"]
        self.assertEqual(post_data["dualSidePosition"], "true")
        self.assertTrue(get_position_mode())

    @patch("binance_rest.requests.get")
    def test_funding_pnl_report(self, mock_get):
        now = int(datetime.datetime(2023, 1, 1).timestamp() * 1000)
        mock_get.return_value = Mock(json=lambda: [
            {"time": now, "income": "0.5"},
            {"time": now + 3600 * 1000, "income": "-0.1"},
            {"time": now + 86400 * 1000, "income": "0.2"},
        ])
        report = funding_pnl_report(now, now + 2 * 86400 * 1000)
        day1 = datetime.datetime.utcfromtimestamp(now / 1000).strftime("%Y-%m-%d")
        day2 = datetime.datetime.utcfromtimestamp((now + 86400 * 1000) / 1000).strftime("%Y-%m-%d")
        self.assertAlmostEqual(report[day1]["total"], 0.4)
        self.assertAlmostEqual(report[day2]["total"], 0.2)
        self.assertEqual(len(report[day1]["settlements"]), 2)
