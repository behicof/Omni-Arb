"""Minimal OKX exchange client placeholder."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class OKXConfig:
    api_key: str = ""
    api_secret: str = ""
    passphrase: str = ""

class OKXExchange:
    """Placeholder for OKX REST/WS interactions."""
    def __init__(self, config: OKXConfig) -> None:
        self.config = config

    def get_funding_rate(self, symbol: str) -> float:
        raise NotImplementedError("Funding rate retrieval not implemented")

    def place_order(self, symbol: str, side: str, quantity: float, price: float, tif: str = "IOC") -> Dict[str, Any]:
        raise NotImplementedError("Order placement not implemented")
