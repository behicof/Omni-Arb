"""Poll Binance funding endpoints and compute NetEdge."""

from __future__ import annotations
import os
from typing import Dict, List

import requests

BASE_URL = "https://fapi.binance.com"


def fetch_funding_rate(symbol: str) -> Dict:
    resp = requests.get(f"{BASE_URL}/fapi/v1/fundingRate", params={"symbol": symbol, "limit": 1})
    resp.raise_for_status()
    return resp.json()[0]


def fetch_funding_info(symbol: str) -> Dict:
    resp = requests.get(f"{BASE_URL}/fapi/v1/fundingInfo", params={"symbol": symbol})
    resp.raise_for_status()
    data = resp.json()
    return data[0] if isinstance(data, list) else data


def calc_net_edge(funding_recv: float, fees: float, carry: float, slippage: float) -> float:
    return funding_recv - fees - carry - slippage


def poll(symbols: List[str], fees: float = 0, carry: float = 0, slippage: float = 0) -> List[Dict[str, float]]:
    edges = []
    for sym in symbols:
        fr = fetch_funding_rate(sym)
        info = fetch_funding_info(sym)
        funding_recv = float(fr.get("fundingRate", 0)) * 10000  # bps
        edge = calc_net_edge(funding_recv, fees, carry, slippage)
        edges.append({"symbol": sym, "NetEdge_bps": edge, "nextFunding": info.get("nextFundingTime")})
    return edges


if __name__ == "__main__":
    syms = os.getenv("SYMBOLS", "BTCUSDT").split(",")
    results = poll(syms)
    for r in results:
        print(r)
