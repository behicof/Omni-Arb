"""Binance Futures order placement wrapper."""
from typing import Any, Dict, Optional
import os
import requests

BASE_URL = "https://fapi.binance.com"


def place_order(
    symbol: str,
    side: str,
    quantity: float,
    price: Optional[float] = None,
    timeInForce: str = "GTC",
    positionSide: Optional[str] = None,
    reduceOnly: Optional[bool] = None,
    newClientOrderId: Optional[str] = None,
    live: Optional[int] = None,
) -> Dict[str, Any]:
    """Place an order on Binance Futures.

    If ``live`` is 0 (default) the test endpoint is used which does not hit the
    matching engine. When ``live`` is 1 the real order endpoint is called.
    Supported ``timeInForce`` values include IOC, GTC, GTD and GTX (post only).
    Additional fields such as ``positionSide``, ``reduceOnly`` and
    ``newClientOrderId`` are forwarded to the exchange.
    """

    live = int(live if live is not None else os.getenv("LIVE", "0"))
    endpoint = "/fapi/v1/order" if live else "/fapi/v1/order/test"

    params: Dict[str, Any] = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT" if price is not None else "MARKET",
        "quantity": quantity,
        "timeInForce": timeInForce,
    }
    if price is not None:
        params["price"] = price
    if positionSide is not None:
        params["positionSide"] = positionSide
    if reduceOnly is not None:
        params["reduceOnly"] = str(reduceOnly).lower()
    if newClientOrderId is not None:
        params["newClientOrderId"] = newClientOrderId

    url = BASE_URL + endpoint
    response = requests.post(url, data=params)
    return response.json()
