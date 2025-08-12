import unittest
from unittest.mock import Mock

from exchange.binance import BinanceOrderWrapper


class TestBinanceGTX(unittest.TestCase):
    def test_gtx_rejection_no_retry(self):
        session = Mock()
        session.post.return_value.json.return_value = {"code": -5022, "msg": "Rejected"}
        wrapper = BinanceOrderWrapper(session=session, reprice_tick=False)
        with self.assertLogs('exchange.binance', level='WARNING') as cm:
            result = wrapper.create_order(
                symbol="BTCUSDT",
                side="BUY",
                order_type="LIMIT",
                quantity=1,
                price=10.0,
                post_only=True,
            )
        self.assertEqual(result["code"], -5022)
        self.assertEqual(session.post.call_count, 1)
        self.assertTrue(any("-5022" in m for m in cm.output))

    def test_gtx_rejection_reprice(self):
        session = Mock()
        # first call rejects, second call succeeds
        session.post.return_value.json.side_effect = [
            {"code": -5022, "msg": "Rejected"},
            {"orderId": 1},
        ]
        wrapper = BinanceOrderWrapper(session=session, reprice_tick=True)
        result = wrapper.create_order(
            symbol="BTCUSDT",
            side="BUY",
            order_type="LIMIT",
            quantity=1,
            price=10.0,
            post_only=True,
        )
        self.assertEqual(result["orderId"], 1)
        self.assertEqual(session.post.call_count, 2)

