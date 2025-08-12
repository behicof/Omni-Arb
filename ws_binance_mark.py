"""Subscribe to Binance mark price stream and persist snapshots."""
import asyncio
import csv
import json
import time
from pathlib import Path
from typing import List

import websockets

WS_BASE = "wss://fstream.binance.com/ws"


def _row_path(symbol: str) -> Path:
    return Path(f"{symbol.lower()}_mark.csv")


async def stream_mark(symbol: str) -> None:
    url = f"{WS_BASE}/{symbol.lower()}@markPrice@1s"
    backoff = 1
    path = _row_path(symbol)
    with path.open("a", newline="") as f:
        writer = csv.writer(f)
        while True:
            try:
                async with websockets.connect(url, ping_interval=20) as ws:
                    async for msg in ws:
                        data = json.loads(msg)
                        writer.writerow([int(time.time()*1000), data["p"], data.get("r"), data.get("T")])
                        f.flush()
                backoff = 1
            except Exception:
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)


def main(symbols: List[str]) -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*(stream_mark(s) for s in symbols)))


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
