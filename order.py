"""Order submission helpers for Binance Futures."""
from __future__ import annotations

from typing import Any, Dict
import requests

BASE_URL = "https://fapi.binance.com"
VALID_TIF = {"IOC", "FOK", "GTC", "GTX"}


class GTXError(Exception):
    """Raised when Binance returns error code -5022 indicating GTX misuse."""


def _validate_order(order: Dict[str, Any], dual_mode: bool) -> None:
    position_side = order.get("positionSide")
    reduce_only = order.get("reduceOnly", False)
    tif = order.get("timeInForce")

    if tif and tif not in VALID_TIF:
        raise ValueError("invalid timeInForce")

    if dual_mode:
        if position_side not in {"LONG", "SHORT"}:
            raise ValueError("dual mode requires positionSide LONG or SHORT")
    else:
        if position_side not in {None, "BOTH"}:
            raise ValueError("one-way mode requires positionSide BOTH or omitted")

    if reduce_only and not position_side:
        raise ValueError("reduceOnly orders must specify positionSide")


def order_test(order: Dict[str, Any], dual_mode: bool, session: Any = requests) -> Dict[str, Any]:
    """Submit a test order to Binance Futures."""
    _validate_order(order, dual_mode)
    resp = session.post(f"{BASE_URL}/fapi/v1/order/test", data=order)
    data = resp.json()
    if data.get("code") == -5022:
        raise GTXError(data.get("msg", "GTX order rejected"))
    return data


def order_live(order: Dict[str, Any], dual_mode: bool, session: Any = requests) -> Dict[str, Any]:
    """Submit a live order to Binance Futures."""
    _validate_order(order, dual_mode)
    resp = session.post(f"{BASE_URL}/fapi/v1/order", data=order)
    data = resp.json()
    if data.get("code") == -5022:
        raise GTXError(data.get("msg", "GTX order rejected"))
    return data
