import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, Dict, Any

import aiohttp
import httpx
import pandas as pd

WS_BASE = "wss://fstream.binance.com/ws"
PREMIUM_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"
EXCHANGE_URL = "https://fapi.binance.com/fapi/v1/exchangeInfo"


def _ensure_storage(out_dir: Path) -> Tuple[Path, Path]:
    """Ensure output directory exists and return parquet/csv paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / "mark.parquet", out_dir / "mark.csv"


def _append_row(parquet_path: Path, csv_path: Path, row: Dict[str, Any]) -> None:
    """Append a single row to parquet and csv."""
    df = pd.DataFrame([row])
    if parquet_path.exists():
        existing = pd.read_parquet(parquet_path)
        df = pd.concat([existing, df], ignore_index=True)
    df.to_parquet(parquet_path, index=False)
    df.to_csv(csv_path, index=False, mode="a", header=not csv_path.exists())


async def _funding_filter(symbol: str) -> Tuple[float, float, int]:
    """Fetch funding rate cap/floor/interval from exchange info."""
    async with httpx.AsyncClient() as client:
        res = await client.get(EXCHANGE_URL, params={"symbol": symbol})
        data = res.json()["symbols"][0]["filters"]
    cap = floor = interval = None
    for f in data:
        if f.get("filterType") == "FUNDING_RATE":
            cap = float(f["maxFundingRate"])
            floor = float(f["minFundingRate"])
            interval = int(f["fundingInterval"])
            break
    return cap, floor, interval


async def _snapshot(symbol: str, cap: float, floor: float, interval: int) -> Dict[str, Any]:
    """Fetch snapshot using premiumIndex endpoint."""
    async with httpx.AsyncClient() as client:
        res = await client.get(PREMIUM_URL, params={"symbol": symbol})
        snap = res.json()
    return {
        "ts": snap["time"],
        "symbol": snap["symbol"],
        "mark": float(snap["markPrice"]),
        "estFunding": float(snap.get("lastFundingRate", 0.0)),
        "nextFunding": snap.get("nextFundingTime"),
        "cap": cap,
        "floor": floor,
        "interval": interval,
    }


async def stream_mark_price(symbol: str, out_dir: str = "data") -> None:
    """Stream mark price via Binance websocket and persist data."""
    cap, floor, interval = await _funding_filter(symbol)
    out_dir_path = Path(out_dir)
    parquet_path, csv_path = _ensure_storage(out_dir_path)
    url = f"{WS_BASE}/{symbol.lower()}@markPrice@1s"

    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(url) as ws:
                    snap = await _snapshot(symbol, cap, floor, interval)
                    _append_row(parquet_path, csv_path, snap)
                    start = datetime.utcnow()
                    async for msg in ws:
                        if msg.type != aiohttp.WSMsgType.TEXT:
                            continue
                        data = json.loads(msg.data)
                        row = {
                            "ts": data["E"],
                            "symbol": data["s"],
                            "mark": float(data["p"]),
                            "estFunding": float(data["r"]),
                            "nextFunding": data["T"],
                            "cap": cap,
                            "floor": floor,
                            "interval": interval,
                        }
                        _append_row(parquet_path, csv_path, row)
                        if datetime.utcnow() - start > timedelta(hours=23, minutes=55):
                            break
        except Exception:
            await asyncio.sleep(5)
            continue
        await asyncio.sleep(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stream Binance mark price")
    parser.add_argument("symbol", help="Trading symbol, e.g., BTCUSDT")
    parser.add_argument("--out", default="data", help="Output directory")
    args = parser.parse_args()

    asyncio.run(stream_mark_price(args.symbol, args.out))
