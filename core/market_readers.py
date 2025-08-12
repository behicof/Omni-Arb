"""Market readers for funding and basis data."""
from datetime import datetime
import csv
import os
from typing import Dict
import requests

from .utils import net_edge_bps

BINANCE_BASE = "https://fapi.binance.com"
OKX_BASE = "https://www.okx.com"


def fetch_binance(symbol: str = "BTCUSDT") -> Dict[str, float]:
    try:
        fr = requests.get(
            f"{BINANCE_BASE}/fapi/v1/fundingRate", params={"symbol": symbol, "limit": 1}
        ).json()[0]
        fi = requests.get(
            f"{BINANCE_BASE}/fapi/v1/fundingInfo", params={"symbol": symbol}
        ).json()[0]
        return {
            "rate": float(fr["fundingRate"]),
            "cap": float(fi.get("fundingRateCap", 0)),
            "floor": float(fi.get("fundingRateFloor", 0)),
        }
    except Exception:
        return {"rate": 0.0, "cap": 0.0, "floor": 0.0}


def fetch_okx(inst_id: str = "BTC-USDT-SWAP") -> Dict[str, float]:
    try:
        instruments = requests.get(
            f"{OKX_BASE}/api/v5/public/instruments",
            params={"instType": "SWAP", "instId": inst_id},
        ).json()
        inst = instruments["data"][0]
        return {
            "rate": float(inst.get("fundingRate", 0)),
            "cap": float(inst.get("fundingFeeCap", 0) or 0),
            "floor": float(inst.get("fundingFeeFloor", 0) or 0),
        }
    except Exception:
        return {"rate": 0.0, "cap": 0.0, "floor": 0.0}


def snapshot(symbol: str = "BTCUSDT", inst_id: str = "BTC-USDT-SWAP", path: str = "data/ticks") -> float:
    binance = fetch_binance(symbol)
    okx = fetch_okx(inst_id)
    net = net_edge_bps(binance["rate"], okx["rate"])

    os.makedirs(path, exist_ok=True)
    csv_path = os.path.join(path, "funding_snapshot.csv")
    headers = ["timestamp", "binance_rate", "okx_rate", "net_edge_bps"]
    row = [datetime.utcnow().isoformat(), binance["rate"], okx["rate"], net]

    write_header = not os.path.exists(csv_path)
    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(headers)
        writer.writerow(row)
    return net
