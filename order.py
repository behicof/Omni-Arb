"""Simple Binance Futures order wrapper with dry-run support."""

from __future__ import annotations
import os
from typing import Any, Dict
import requests

BASE_URL = "https://fapi.binance.com"
ALLOWED_TIF = {"IOC", "FOK", "GTC", "GTX"}

class BinanceOrderClient:
    """Place orders on Binance Futures with LIVE toggle."""

    def __init__(self, api_key: str = "", live: int | None = None) -> None:
        self.api_key = api_key
        self.live = int(os.getenv("LIVE", "0")) if live is None else int(live)

    def place_order(self, symbol: str, side: str, quantity: float,
                    price: float | None = None, tif: str = "GTC") -> Dict[str, Any]:
        tif = tif.upper()
        if tif not in ALLOWED_TIF:
            raise ValueError("Unsupported timeInForce")
        if tif == "GTX" and price is None:
            raise ValueError("GTX (Post-Only) requires a limit price")

        endpoint = "/fapi/v1/order" if self.live else "/fapi/v1/order/test"
        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": "LIMIT" if price is not None else "MARKET",
            "quantity": quantity,
            "timeInForce": tif,
        }
        if price is not None:
            params["price"] = price
        headers = {"X-MBX-APIKEY": self.api_key} if self.api_key else {}
        response = requests.post(f"{BASE_URL}{endpoint}", params=params, headers=headers)
        try:
            data = response.json()
        except ValueError:
            data = {"error": response.text}
        data.setdefault("status", response.status_code)
        return data

__all__ = ["BinanceOrderClient", "ALLOWED_TIF"]
