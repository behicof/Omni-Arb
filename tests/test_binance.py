import httpx
import pytest
from core.exchange import binance


def make_transport(capture):
    def handler(request: httpx.Request) -> httpx.Response:
        capture['method'] = request.method
        capture['url'] = request.url.path
        capture['data'] = request.content.decode()
        return httpx.Response(200, json={"ok": True})
    return httpx.MockTransport(handler)


def test_place_test_order_endpoints():
    capture = {}
    transport = make_transport(capture)
    client = httpx.Client(transport=transport)
    # Dry run
    binance.place_order(
        client,
        symbol="BTCUSDT",
        side="BUY",
        quantity=1,
        price=10,
        time_in_force="GTC",
        live=False,
    )
    assert capture['url'] == "/fapi/v1/order/test"
    # Live
    binance.place_order(
        client,
        symbol="BTCUSDT",
        side="BUY",
        quantity=1,
        price=10,
        time_in_force="GTC",
        live=True,
    )
    assert capture['url'] == "/fapi/v1/order"


def test_post_only_requires_price():
    with pytest.raises(ValueError):
        binance.place_test_order(symbol="BTCUSDT", side="BUY", quantity=1, time_in_force="GTX")


def test_position_side_and_reduce_only():
    capture = {}
    transport = make_transport(capture)
    client = httpx.Client(transport=transport)
    binance.place_order(
        client,
        symbol="BTCUSDT",
        side="SELL",
        quantity=1,
        price=10,
        time_in_force="IOC",
        reduce_only=True,
        position_side="SHORT",
        live=False,
    )
    assert "reduceOnly" in capture['data']
    assert "positionSide=SHORT" in capture['data']
