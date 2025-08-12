"""Binance futures exchange utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

BASE_URL = "https://fapi.binance.com"


@dataclass
class BinanceExchange:
    """Minimal Binance futures REST client.

    Parameters
    ----------
    api_key: Optional[str]
        API key used for authenticated endpoints.
    """

    api_key: Optional[str] = None

    # --- Position mode management -------------------------------------------------
    def _headers(self) -> Dict[str, str]:
        return {"X-MBX-APIKEY": self.api_key} if self.api_key else {}

    def get_position_mode(self) -> bool:
        """Return ``True`` if dual-side (hedge) mode is enabled."""
        url = f"{BASE_URL}/fapi/v1/positionSide/dual"
        resp = requests.get(url, headers=self._headers(), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return bool(data.get("dualSidePosition", False))

    def set_position_mode(self, hedge: bool) -> Dict[str, Any]:
        """Enable or disable dual-side (hedge) mode."""
        params = {"dualSidePosition": "true" if hedge else "false"}
        url = f"{BASE_URL}/fapi/v1/positionSide/dual"
        resp = requests.post(url, params=params, headers=self._headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()

    # --- Order helper -------------------------------------------------------------
    def build_order(
        self,
        side: str,
        quantity: float,
        *,
        reduce_only: bool = False,
        position_side: Optional[str] = None,
        time_in_force: Optional[str] = None,
        hedge_mode: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Build order parameters validating Hedge mode and reduceOnly rules."""
        if time_in_force == "GTX" and reduce_only:
            raise ValueError("reduceOnly cannot be used with timeInForce GTX")

        if hedge_mode is None:
            hedge_mode = self.get_position_mode()

        params: Dict[str, Any] = {
            "side": side,
            "quantity": quantity,
            "reduceOnly": reduce_only,
        }

        if hedge_mode:
            opening = not reduce_only
            if opening:
                expected_side = "LONG" if side == "BUY" else "SHORT"
            else:
                expected_side = "SHORT" if side == "BUY" else "LONG"
            if position_side is None:
                position_side = expected_side
            if position_side != expected_side:
                raise ValueError(
                    f"positionSide must be {expected_side} for side={side} reduceOnly={reduce_only}"
                )
            params["positionSide"] = position_side
        else:
            if position_side is not None:
                raise ValueError("positionSide is only valid in Hedge mode")

        if time_in_force:
            params["timeInForce"] = time_in_force

        return params
