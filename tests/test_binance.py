from unittest.mock import patch
from core.exchange.binance import place_order


def test_place_order_test_endpoint():
    with patch("core.exchange.binance.requests.post") as mock_post:
        mock_post.return_value.json.return_value = {"status": "ok"}
        place_order(
            symbol="BTCUSDT",
            side="BUY",
            quantity=1,
            price=100,
            timeInForce="GTC",
            positionSide="LONG",
            reduceOnly=False,
            newClientOrderId="123",
            live=0,
        )
        url = mock_post.call_args[0][0]
        data = mock_post.call_args[1]["data"]
        assert url.endswith("/fapi/v1/order/test")
        assert data["timeInForce"] == "GTC"
        assert data["positionSide"] == "LONG"
        assert data["reduceOnly"] == "false"
        assert data["newClientOrderId"] == "123"


def test_place_order_live_endpoint():
    with patch("core.exchange.binance.requests.post") as mock_post:
        mock_post.return_value.json.return_value = {"status": "ok"}
        place_order(
            symbol="BTCUSDT", side="BUY", quantity=1, live=1, timeInForce="IOC"
        )
        url = mock_post.call_args[0][0]
        assert url.endswith("/fapi/v1/order")
