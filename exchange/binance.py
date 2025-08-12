import logging
from typing import Any, Dict, Optional

import requests

BINANCE_BASE_URL = "https://api.binance.com"  # placeholder endpoint

VALID_TIME_IN_FORCE = {"GTC", "IOC", "FOK", "GTX"}


class BinanceOrderWrapper:
    """Simple Binance order wrapper supporting post-only (GTX) orders."""

    def __init__(
        self,
        api_key: str | None = None,
        session: Optional[requests.Session] = None,
        *,
        reprice_tick: bool = False,
        tick_size: float = 0.01,
    ) -> None:
        self.api_key = api_key or ""
        self.session = session or requests.Session()
        self.reprice_tick = reprice_tick
        self.tick_size = tick_size
        self.logger = logging.getLogger(__name__)

    # internal helper to send order
    def _send_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        headers = {"X-MBX-APIKEY": self.api_key} if self.api_key else {}
        response = self.session.post(f"{BINANCE_BASE_URL}/api/v3/order", data=params, headers=headers)
        return response.json()

    def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        time_in_force: str = "GTC",
        post_only: bool = False,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }
        if price is not None:
            params["price"] = price

        if post_only:
            time_in_force = "GTX"
        if time_in_force not in VALID_TIME_IN_FORCE:
            raise ValueError(f"Invalid timeInForce {time_in_force}")
        params["timeInForce"] = time_in_force

        response = self._send_order(params)
        # Detect GTX rejection
        if response.get("code") == -5022 and time_in_force == "GTX":
            self.logger.warning("Binance rejected post-only order (-5022)")
            if self.reprice_tick and price is not None:
                # Adjust price by one tick and retry once
                adjusted_price = price - self.tick_size if side.upper() == "SELL" else price + self.tick_size
                params["price"] = adjusted_price
                response = self._send_order(params)
            return response
        return response
