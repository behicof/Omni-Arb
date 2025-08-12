"""REST polling for mark price and funding rates.

For each symbol supplied, this module polls Binance or OKX REST endpoints to
fetch mark price, estimated funding rate and next funding time.  Snapshots are
written to ``data/ticks/YYYYMMDD/<symbol>.csv`` with schema::

    ts,symbol,mark,estFunding,nextFunding,src

The scheduler respects per-symbol rate limits (1 request/second) and applies an
exponential backoff on HTTP 429 or 5xx responses.
"""
from __future__ import annotations

import asyncio
import csv
import datetime as dt
import os
from typing import Iterable

import aiohttp

BINANCE_PREMIUM_INDEX = "https://fapi.binance.com/fapi/v1/premiumIndex"
BINANCE_FUNDING_RATE = "https://fapi.binance.com/fapi/v1/fundingRate"

OKX_FUNDING_RATE = "https://www.okx.com/api/v5/public/funding-rate"
OKX_INDEX_TICKERS = "https://www.okx.com/api/v5/market/index-tickers"

POLL_INTERVAL_MS = 1_000
SRC = "REST"


def _csv_path(symbol: str) -> str:
    date_dir = dt.datetime.utcnow().strftime("%Y%m%d")
    path = os.path.join("data", "ticks", date_dir)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{symbol}.csv")


def _write_row(symbol: str, mark: float, est_funding: float, next_funding: str) -> None:
    ts = dt.datetime.utcnow().isoformat()
    path = _csv_path(symbol)
    file_exists = os.path.exists(path)
    with open(path, "a", newline="") as fh:
        writer = csv.writer(fh)
        if not file_exists:
            writer.writerow(["ts", "symbol", "mark", "estFunding", "nextFunding", "src"])
        writer.writerow([ts, symbol, mark, est_funding, next_funding, SRC])


async def _fetch_binance(session: aiohttp.ClientSession, symbol: str) -> None:
    params = {"symbol": symbol}
    async with session.get(BINANCE_PREMIUM_INDEX, params=params) as resp:
        resp.raise_for_status()
        data = await resp.json()
    mark = float(data.get("markPrice", 0))
    est_funding = float(data.get("lastFundingRate", 0))
    next_funding_ms = int(data.get("nextFundingTime", 0))
    next_funding = dt.datetime.utcfromtimestamp(next_funding_ms / 1000).isoformat()
    # sanity call (ignore response contents)
    async with session.get(BINANCE_FUNDING_RATE, params={"symbol": symbol, "limit": 1}) as resp:
        resp.raise_for_status()
        await resp.read()
    _write_row(symbol, mark, est_funding, next_funding)


async def _fetch_okx(session: aiohttp.ClientSession, inst_id: str) -> None:
    headers = {"x-simulated-trading": os.getenv("OKX_DEMO", "0")}
    async with session.get(OKX_FUNDING_RATE, params={"instId": inst_id}, headers=headers) as resp:
        resp.raise_for_status()
        data = (await resp.json())["data"][0]
    est_funding = float(data.get("fundingRate", 0))
    next_funding = data.get("fundingTime", "")
    index_id = inst_id.replace("-SWAP", "")
    async with session.get(OKX_INDEX_TICKERS, params={"instId": index_id}, headers=headers) as resp:
        resp.raise_for_status()
        idx = (await resp.json())["data"][0]
    mark = float(idx.get("idxPx") or idx.get("markPx") or 0)
    _write_row(inst_id, mark, est_funding, next_funding)


async def _poll_symbol(session: aiohttp.ClientSession, symbol: str) -> None:
    backoff = POLL_INTERVAL_MS / 1000
    await asyncio.sleep(0)  # allow loop to start
    while True:
        try:
            if "-" in symbol:
                await _fetch_okx(session, symbol)
            else:
                await _fetch_binance(session, symbol)
            await asyncio.sleep(POLL_INTERVAL_MS / 1000)
            backoff = POLL_INTERVAL_MS / 1000
        except aiohttp.ClientResponseError as exc:  # HTTP errors
            if exc.status == 429 or 500 <= exc.status < 600:
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)
            else:
                raise
        except Exception:
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def poll_mark_funding(symbols: Iterable[str]) -> None:
    """Poll mark price and funding info for *symbols* forever."""
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(_poll_symbol(session, sym)) for sym in symbols]
        await asyncio.gather(*tasks)


if __name__ == "__main__":  # pragma: no cover
    import argparse

    parser = argparse.ArgumentParser(description="REST mark/funding poller")
    parser.add_argument("--symbols", required=True, help="Comma separated symbols")
    args = parser.parse_args()
    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    asyncio.run(poll_mark_funding(symbols))
