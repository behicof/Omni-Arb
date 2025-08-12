"""Binance Futures mark price client.

By default this module connects to Binance's WebSocket feed.  When the
environment variable ``WS_DISABLED`` is set to ``"1"`` it instead falls back to
REST polling via :mod:`feeds.rest_mark_funding`.
"""
import asyncio
import csv
import datetime as dt
import json
import os
from typing import Optional

import websockets

BINANCE_WS_URL = "wss://fstream.binance.com/ws"


def _write_snapshot(symbol: str, mark_price: str, funding_rate: str, event_time: int) -> None:
    """Append snapshot data to CSV for given symbol."""
    os.makedirs("data/ticks", exist_ok=True)
    path = os.path.join("data", "ticks", f"{symbol}.csv")
    file_exists = os.path.exists(path)
    timestamp = dt.datetime.utcfromtimestamp(event_time / 1000).isoformat()
    with open(path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "markPrice", "fundingRate"])
        writer.writerow([timestamp, mark_price, funding_rate])


async def _handle_message(msg: str) -> None:
    data = json.loads(msg)
    if isinstance(data, list):
        for item in data:
            _write_snapshot(item["s"], item["p"], item["r"], item["E"])
    else:
        _write_snapshot(data["s"], data["p"], data["r"], data["E"])


async def subscribe_mark_price(symbol: Optional[str] = None) -> None:
    """Subscribe to Binance mark price stream.

    Args:
        symbol: Specific symbol to subscribe to. If omitted, subscribes to all symbols.
    """
    if os.getenv("WS_DISABLED") == "1":
        from feeds.rest_mark_funding import poll_mark_funding

        symbols = [symbol] if symbol else ["BTCUSDT"]
        await poll_mark_funding(symbols)
        return

    stream = "!markPrice@arr@1s" if symbol is None else f"{symbol.lower()}@markPrice@1s"
    url = f"{BINANCE_WS_URL}/{stream}"
    backoff = 1
    while True:
        try:
            async with websockets.connect(url) as ws:
                backoff = 1
                async for msg in ws:
                    await _handle_message(msg)
        except Exception as exc:  # pragma: no cover - network errors
            print(f"WebSocket error: {exc}. Reconnecting in {backoff}s...")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 32)


if __name__ == "__main__":  # pragma: no cover
    import argparse

    parser = argparse.ArgumentParser(description="Binance mark price subscriber")
    parser.add_argument("--symbol", help="Symbol to subscribe to", default=None)
    args = parser.parse_args()

    # ``--symbol`` may contain a comma separated list.  When WS is disabled the
    # REST poller can handle multiple symbols.
    if os.getenv("WS_DISABLED") == "1" and args.symbol:
        from feeds.rest_mark_funding import poll_mark_funding

        symbols = [s.strip() for s in args.symbol.split(",") if s.strip()]
        asyncio.run(poll_mark_funding(symbols))
    else:
        asyncio.run(subscribe_mark_price(args.symbol))
