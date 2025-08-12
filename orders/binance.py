import os
import time
import hmac
import hashlib
from decimal import Decimal, ROUND_DOWN
from typing import Any, Dict

import logging
import requests

logger = logging.getLogger(__name__)

API_URL = "https://fapi.binance.com"


def _sign(params: Dict[str, Any], secret: str) -> Dict[str, Any]:
    query = "&".join(f"{k}={v}" for k, v in params.items())
    signature = hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature
    return params


def _get_headers(api_key: str) -> Dict[str, str]:
    return {"X-MBX-APIKEY": api_key}


class BinanceOrderClient:
    """Simple Binance Futures order wrapper with basic validation."""

    def __init__(self, api_key: str, api_secret: str, live: bool | None = None) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        if live is None:
            live_env = os.getenv("LIVE", "0")
            self.live = bool(int(live_env))
        else:
            self.live = live
        self.session = requests.Session()
        self.session.headers.update(_get_headers(api_key))
        self._exchange_cache: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Exchange info helpers
    # ------------------------------------------------------------------
    def _get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        symbol = symbol.upper()
        if symbol not in self._exchange_cache:
            resp = self.session.get(f"{API_URL}/fapi/v1/exchangeInfo", params={"symbol": symbol})
            data = resp.json()
            if "symbols" not in data or not data["symbols"]:
                raise ValueError(f"Symbol {symbol} not found on exchange")
            self._exchange_cache[symbol] = data["symbols"][0]
        return self._exchange_cache[symbol]

    def _validate(self, symbol: str, quantity: Decimal, price: Decimal | None) -> None:
        info = self._get_symbol_info(symbol)
        qty = Decimal(str(quantity))
        prc = Decimal(str(price)) if price is not None else None

        qty_precision = info.get("quantityPrecision", 8)
        price_precision = info.get("pricePrecision", 8)

        for f in info.get("filters", []):
            f_type = f.get("filterType")
            if f_type == "LOT_SIZE":
                min_qty = Decimal(f["minQty"])
                step_size = Decimal(f["stepSize"])
                if qty < min_qty:
                    raise ValueError("Quantity below minQty")
                if (qty - min_qty) % step_size != 0:
                    raise ValueError("Quantity not aligned with stepSize")
            elif f_type == "MIN_NOTIONAL" and prc is not None:
                min_notional = Decimal(f["notional"])
                if prc * qty < min_notional:
                    raise ValueError("Notional too small")
            elif f_type == "PRICE_FILTER" and prc is not None:
                min_price = Decimal(f["minPrice"])
                tick = Decimal(f["tickSize"])
                if prc < min_price:
                    raise ValueError("Price below minPrice")
                if (prc - min_price) % tick != 0:
                    raise ValueError("Price not aligned with tickSize")

        # Precision validation
        q_quant = Decimal("1") / (Decimal("10") ** qty_precision)
        if qty != qty.quantize(q_quant, rounding=ROUND_DOWN):
            raise ValueError("Quantity exceeds allowed precision")
        if prc is not None:
            p_quant = Decimal("1") / (Decimal("10") ** price_precision)
            if prc != prc.quantize(p_quant, rounding=ROUND_DOWN):
                raise ValueError("Price exceeds allowed precision")

    # ------------------------------------------------------------------
    # Order placement
    # ------------------------------------------------------------------
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float | None = None,
        time_in_force: str = "GTC",
        reduce_only: bool = False,
        position_side: str | None = None,
        new_order_resp_type: str = "RESULT",
        extra_params: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        symbol = symbol.upper()
        qty_dec = Decimal(str(quantity))
        price_dec = Decimal(str(price)) if price is not None else None
        self._validate(symbol, qty_dec, price_dec)

        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": float(qty_dec),
            "timestamp": int(time.time() * 1000),
            "newOrderRespType": new_order_resp_type,
        }
        if order_type.upper() != "MARKET":
            if price_dec is None:
                raise ValueError("Price required for non-market orders")
            tif = time_in_force.upper()
            if tif not in {"IOC", "FOK", "GTC", "GTX"}:
                raise ValueError("Unsupported timeInForce")
            params["price"] = float(price_dec)
            params["timeInForce"] = tif
        if reduce_only:
            params["reduceOnly"] = "true"
        if position_side:
            params["positionSide"] = position_side
        if extra_params:
            params.update(extra_params)

        endpoint = "/fapi/v1/order" if self.live else "/fapi/v1/order/test"
        signed = _sign(params, self.api_secret)
        resp = self.session.post(f"{API_URL}{endpoint}", params=signed)
        data = resp.json()

        if resp.status_code != 200 or "code" in data and data.get("code", 0) != 0:
            logger.error("Order rejected: %s", data)
        else:
            logger.info("Order %s: %s", new_order_resp_type, data)
        return data
