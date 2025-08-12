"""Binance Futures exchange order utilities."""
from __future__ import annotations
import httpx
from typing import Optional

BASE_URL = "https://fapi.binance.com"

VALID_TIFS = {"IOC", "GTC", "GTX"}


def place_order(
    client: httpx.Client,
    *,
    symbol: str,
    side: str,
    quantity: float,
    price: Optional[float] = None,
    time_in_force: str = "GTC",
    reduce_only: bool = False,
    position_side: Optional[str] = None,
    live: bool = False,
) -> httpx.Response:
    """Place an order on Binance Futures.

    The function validates time-in-force to allow IOC, GTC and GTX (post-only).
    When ``live`` is ``False`` the order is sent to the test endpoint which is
    guaranteed not to hit the matching engine.
    """
    tif = time_in_force.upper()
    if tif not in VALID_TIFS:
        raise ValueError("time_in_force must be one of IOC, GTC or GTX")
    if tif == "GTX" and price is None:
        raise ValueError("Post-only (GTX) orders require a price")

    endpoint = "/fapi/v1/order" if live else "/fapi/v1/order/test"
    url = BASE_URL + endpoint

    payload = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT" if price is not None else "MARKET",
        "quantity": quantity,
        "timeInForce": tif,
    }
    if price is not None:
        payload["price"] = price
    if reduce_only:
        payload["reduceOnly"] = True
    if position_side:
        payload["positionSide"] = position_side

    return client.post(url, data=payload)


def place_test_order(**kwargs) -> httpx.Response:
    """Convenience wrapper using a temporary client."""
    live = kwargs.pop("live", False)
    with httpx.Client() as client:
        return place_order(client, live=live, **kwargs)
