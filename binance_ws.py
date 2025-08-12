"""Binance mark price WebSocket utilities."""
import asyncio
import json
import os
import datetime
from typing import Dict, Any


STREAM_URL = "wss://fstream.binance.com/stream?streams=!markPrice@arr@1s"

# In-memory cache of funding rates
funding_rates: Dict[str, float] = {}

async def process_message(message: str, log_dir: str = "data/ticks") -> None:
    """Process and log a mark price update message."""
    data = json.loads(message)
    rows = data.get("data") or []
    if not rows:
        return

    os.makedirs(log_dir, exist_ok=True)
    date_str = datetime.datetime.utcnow().strftime("%Y%m%d")
    log_path = os.path.join(log_dir, f"{date_str}.log")
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(message + "\n")

    for item in rows:
        symbol = item.get("s")
        rate = item.get("r")
        if symbol and rate is not None:
            try:
                funding_rates[symbol] = float(rate)
            except (TypeError, ValueError):
                continue

async def stream_mark_price(log_dir: str = "data/ticks") -> None:
    import websockets
    """Connect to Binance all market mark price stream."""
    async with websockets.connect(STREAM_URL) as ws:
        async for msg in ws:
            await process_message(msg, log_dir=log_dir)
