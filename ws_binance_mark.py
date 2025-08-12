"""WebSocket client for Binance mark price stream."""

from __future__ import annotations
import asyncio
import json
from typing import List

import aiohttp
import pandas as pd

STREAM_URL = "wss://fstream.binance.com/ws/{symbol}@markPrice@1s"

async def stream_mark_price(symbol: str, csv_path: str = "mark.csv", parquet_path: str = "mark.parquet") -> None:
    """Subscribe to mark price stream and persist data."""
    data: List[dict] = []
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(STREAM_URL.format(symbol=symbol.lower())) as ws:
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            payload = json.loads(msg.data)
                            mark = {
                                "ts": payload.get("E"),
                                "markPrice": payload.get("p"),
                                "fundingRate": payload.get("r"),
                                "nextFunding": payload.get("T"),
                            }
                            data.append(mark)
                            df = pd.DataFrame(data)
                            df.to_csv(csv_path, index=False)
                            df.to_parquet(parquet_path, index=False)
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            break
        except Exception:
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(stream_mark_price("btcusdt"))
