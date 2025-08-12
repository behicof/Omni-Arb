from pathlib import Path
from typing import Dict, Any
import csv
import time

import httpx
import pandas as pd

FUNDING_INFO_URL = "https://fapi.binance.com/fapi/v1/fundingInfo"
FUNDING_RATE_URL = "https://fapi.binance.com/fapi/v1/fundingRate"
EXCHANGE_URL = "https://fapi.binance.com/fapi/v1/exchangeInfo"


def _funding_filter(symbol: str) -> Dict[str, Any]:
    with httpx.Client() as client:
        res = client.get(EXCHANGE_URL, params={"symbol": symbol})
        filters = res.json()["symbols"][0]["filters"]
    for f in filters:
        if f.get("filterType") == "FUNDING_RATE":
            return {
                "cap": float(f["maxFundingRate"]),
                "floor": float(f["minFundingRate"]),
                "interval": int(f["fundingInterval"]),
            }
    return {"cap": None, "floor": None, "interval": None}


def _ensure_storage(out_dir: Path) -> (Path, Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / "funding.parquet", out_dir / "funding.csv"


def _append_row(parquet_path: Path, csv_path: Path, row: Dict[str, Any]) -> None:
    df = pd.DataFrame([row])
    if parquet_path.exists():
        existing = pd.read_parquet(parquet_path)
        df = pd.concat([existing, df], ignore_index=True)
    df.to_parquet(parquet_path, index=False)
    df.to_csv(csv_path, index=False, mode="a", header=not csv_path.exists())


def poll_funding(symbol: str, out_dir: str = "data") -> None:
    filt = _funding_filter(symbol)
    with httpx.Client() as client:
        info = client.get(FUNDING_INFO_URL, params={"symbol": symbol}).json()
        info = info[0] if isinstance(info, list) else info
        rate = client.get(FUNDING_RATE_URL, params={"symbol": symbol, "limit": 1}).json()
        rate = rate[0] if isinstance(rate, list) else rate
    row = {
        "ts": info.get("time", int(time.time() * 1000)),
        "symbol": info.get("symbol", symbol),
        "mark": float(info.get("markPrice", 0.0)),
        "estFunding": float(info.get("nextFundingRate", rate.get("fundingRate", 0.0))),
        "nextFunding": info.get("nextFundingTime"),
        "cap": filt["cap"],
        "floor": filt["floor"],
        "interval": filt["interval"],
    }
    out_dir_path = Path(out_dir)
    parquet_path, csv_path = _ensure_storage(out_dir_path)
    _append_row(parquet_path, csv_path, row)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Poll Binance funding info")
    parser.add_argument("symbol", help="Trading symbol, e.g., BTCUSDT")
    parser.add_argument("--out", default="data", help="Output directory")
    args = parser.parse_args()

    poll_funding(args.symbol, args.out)
