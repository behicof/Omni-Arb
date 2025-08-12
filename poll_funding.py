"""Poll Binance funding endpoints and compute net edge."""
from __future__ import annotations
import time
from typing import Dict

import requests

BINANCE_BASE = "https://fapi.binance.com"
FEE_BPS = 2
CARRY_BPS = 1
SLIPPAGE_BPS = 1


def fetch_funding(symbol: str) -> Dict[str, float]:
    rate = requests.get(f"{BINANCE_BASE}/fapi/v1/fundingRate", params={"symbol": symbol, "limit": 1}).json()[0]
    info = requests.get(f"{BINANCE_BASE}/fapi/v1/fundingInfo", params={"symbol": symbol}).json()[0]
    return {
        "fundingRate": float(rate["fundingRate"]) * 1e4,
        "capRate": float(info.get("capRate", 0)) * 1e4,
        "nextFundingTime": int(rate["fundingTime"]),
    }


def net_edge_bps(symbol: str) -> Dict[str, float]:
    data = fetch_funding(symbol)
    edge = data["fundingRate"] - FEE_BPS - CARRY_BPS - SLIPPAGE_BPS
    data["NetEdge_bps"] = edge
    data["ts"] = int(time.time()*1000)
    return data


if __name__ == "__main__":
    import sys, json
    print(json.dumps(net_edge_bps(sys.argv[1])))
