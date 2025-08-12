"""Binance order wrapper with test/live switch and filter validation."""
from __future__ import annotations
import os
import logging
from typing import Dict, Any

import requests

BINANCE_BASE = "https://fapi.binance.com"
logger = logging.getLogger(__name__)


def _get_filters(symbol: str) -> Dict[str, Any]:
    resp = requests.get(f"{BINANCE_BASE}/fapi/v1/exchangeInfo", params={"symbol": symbol})
    resp.raise_for_status()
    info = resp.json()
    filters = {}
    for f in info["symbols"][0]["filters"]:
        filters[f["filterType"]] = f
    return filters


def _validate(symbol: str, qty: float, price: float) -> None:
    filters = _get_filters(symbol)
    lot = float(filters["LOT_SIZE"]["stepSize"])
    min_qty = float(filters["LOT_SIZE"]["minQty"])
    notional = float(filters["MIN_NOTIONAL"]["notional"])
    if qty < min_qty or (qty % lot) != 0:
        raise ValueError("quantity fails LOT_SIZE filter")
    if qty * price < notional:
        raise ValueError("notional below MIN_NOTIONAL")


def send_order(payload: Dict[str, Any], live: int | None = None) -> Dict[str, Any]:
    """Send an order or run dry-run test.

    Parameters
    ----------
    payload: Dict[str, Any]
        Must include symbol, side, quantity, price, timeInForce.
    live: int | None
        Override LIVE flag; 0 uses test endpoint.
    """
    if live is None:
        live = int(os.getenv("LIVE", "0"))

    symbol = payload.get("symbol")
    qty = float(payload.get("quantity", 0))
    price = float(payload.get("price", 0))
    _validate(symbol, qty, price)

    endpoint = "/fapi/v1/order" if live else "/fapi/v1/order/test"
    url = f"{BINANCE_BASE}{endpoint}"
    headers = {"X-MBX-APIKEY": os.getenv("BINANCE_API_KEY", "")}
    resp = requests.post(url, headers=headers, data=payload)
    try:
        resp.raise_for_status()
        logger.info("ACK %s", resp.json())
    except requests.HTTPError as exc:
        logger.error("error %s", resp.text)
        raise exc
    return resp.json()


__all__ = ["send_order"]
