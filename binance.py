import logging
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests
import rsa


class BinanceFuturesClient:
    """Simple Binance Futures REST client with hedge mode support."""

    def __init__(self, api_key: str, private_key_pem: str,
                 base_url: str = "https://fapi.binance.com") -> None:
        self.api_key = api_key
        self._private_key = rsa.PrivateKey.load_pkcs1(private_key_pem.encode())
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": api_key})
        self.hedge_mode: Optional[bool] = None
        self.rate_limits: Dict[str, str] = {}

    # --- signing and request helpers -------------------------------------------------
    def _sign(self, params: Dict[str, Any]) -> str:
        query = urlencode(params)
        signature = rsa.sign(query.encode(), self._private_key, "SHA-256")
        return signature.hex()

    def _request(self, method: str, path: str,
                 params: Optional[Dict[str, Any]] = None,
                 signed: bool = False) -> requests.Response:
        params = params or {}
        if signed:
            params["timestamp"] = int(time.time() * 1000)
            params["signature"] = self._sign(params)
        url = self.base_url + path
        response = self.session.request(method, url, params=params)
        # capture rate limit headers
        self.rate_limits = {k: v for k, v in response.headers.items() if k.startswith("X-MBX-")}
        return response

    # --- position mode ---------------------------------------------------------------
    def get_position_mode(self) -> bool:
        """Retrieve current position mode (hedge or one-way)."""
        r = self._request("GET", "/fapi/v1/positionSide/dual", signed=True)
        data = r.json()
        self.hedge_mode = data.get("dualSidePosition", False)
        return bool(self.hedge_mode)

    def set_position_mode(self, hedge: bool) -> Dict[str, Any]:
        """Enable or disable hedge mode."""
        params = {"dualSidePosition": str(hedge).lower()}
        r = self._request("POST", "/fapi/v1/positionSide/dual", params=params, signed=True)
        if r.status_code == 200:
            self.hedge_mode = hedge
        return r.json()

    # --- order placement -------------------------------------------------------------
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        time_in_force: Optional[str] = None,
        reduce_only: bool = False,
        position_side: Optional[str] = None,
        live: bool = True,
        **extra: Any,
    ) -> Dict[str, Any]:
        """Place an order or test order depending on ``live`` flag."""

        if self.hedge_mode:
            # auto set positionSide if not provided
            if position_side is None:
                position_side = "LONG" if side.upper() == "BUY" else "SHORT"
            if reduce_only and position_side is None:
                raise ValueError("reduceOnly orders must specify positionSide in hedge mode")
        elif position_side is not None:
            raise ValueError("positionSide is only valid in hedge mode")

        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }
        if price is not None:
            params["price"] = price
        if time_in_force is not None:
            params["timeInForce"] = time_in_force
        if reduce_only:
            params["reduceOnly"] = "true"
        if position_side is not None:
            params["positionSide"] = position_side
        params.update(extra)

        path = "/fapi/v1/order" if live else "/fapi/v1/order/test"
        r = self._request("POST", path, params=params, signed=True)
        data = r.json()
        if params.get("timeInForce") == "GTX" and data.get("code") == -5022:
            logging.warning("GTX order rejected: %s", data.get("msg", ""))
        return data
