"""Binance connectivity utilities.

This module implements:

B-1  Mark price WebSocket stream at 1s intervals with
     exponential backoff and automatic reconnect. Each
     update snapshot (ts, markPrice, fundingRate, nextFundingTime)
     is appended to a CSV file.

B-2  Periodic REST polling of funding rate and funding info
     endpoints.  Using these values a `net edge` is calculated
     via clamping to the reported cap/floor and published every
     second.

The implementation relies on the official Binance Futures APIs.
"""
from __future__ import annotations

import asyncio
import csv
import json
import time
from pathlib import Path
from typing import Iterable, Dict, Any

import requests

BINANCE_WS_URL = "wss://fstream.binance.com/stream"
BINANCE_REST_BASE = "https://fapi.binance.com"


def compute_net_edge(rate: float, cap: float, floor: float) -> float:
    """Clamp *rate* between *cap* and *floor* and return the result."""
    return max(min(rate, cap), floor)


async def mark_price_stream(symbols: Iterable[str], csv_file: str | Path) -> None:
    """Stream mark prices for *symbols* and append CSV snapshots.

    Each message from ``<symbol>@markPrice@1s`` contains the mark
    price ``p``, funding rate ``r`` and next funding time ``T``.
    Snapshots are written as ``ts, markPrice, fundingRate, nextFundingTime``.

    The connection is retried with exponential backoff on failure.
    """

    csv_path = Path(csv_file)
    streams = "/".join(f"{s.lower()}@markPrice@1s" for s in symbols)
    url = f"{BINANCE_WS_URL}?streams={streams}"
    backoff = 1

    # ensure CSV has header
    if not csv_path.exists():
        with csv_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ts", "markPrice", "fundingRate", "nextFundingTime"])

    # import websockets lazily so that unit tests can run without the
    # dependency installed.
    import websockets  # type: ignore

    while True:
        try:
            async with websockets.connect(url) as ws:
                backoff = 1  # reset after successful connect
                async for msg in ws:
                    payload = json.loads(msg).get("data", {})
                    ts = int(payload.get("E", 0))
                    mark_price = float(payload.get("p", 0))
                    funding_rate = float(payload.get("r", 0))
                    next_funding = int(payload.get("T", 0))
                    with csv_path.open("a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([ts, mark_price, funding_rate, next_funding])
        except (ConnectionClosed, InvalidURI, OSError) as exc:  # pragma: no cover - network failures
            print("WebSocket error", exc)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)  # exponential backoff


def poll_funding_info(symbols: Iterable[str], interval: float = 1.0) -> None:
    """Poll funding endpoints and publish the calculated net edge.

    ``GET /fapi/v1/fundingRate`` provides the latest rate while
    ``GET /fapi/v1/fundingInfo`` yields the cap, floor and interval.
    ``net edge`` is the funding rate clamped between cap and floor.
    """
    session = requests.Session()
    while True:  # pragma: no cover - long running loop
        for symbol in symbols:
            rate_resp = session.get(
                f"{BINANCE_REST_BASE}/fapi/v1/fundingRate",
                params={"symbol": symbol, "limit": 1},
                timeout=10,
            ).json()
            # Ensure rate_resp is a list with at least one element
            if not isinstance(rate_resp, list) or len(rate_resp) == 0:
                # Optionally log error responses if rate_resp is a dict
                if isinstance(rate_resp, dict) and "msg" in rate_resp:
                    print(f"Error response for {symbol}: {rate_resp.get('msg')}")
                continue
            rate = float(rate_resp[0]["fundingRate"])

            info_resp: Dict[str, Any] = session.get(
                f"{BINANCE_REST_BASE}/fapi/v1/fundingInfo",
                params={"symbol": symbol},
                timeout=10,
            ).json()
            cap = float(info_resp.get("fundingRateCap", 0))
            floor = float(info_resp.get("fundingRateFloor", 0))
            net_edge = compute_net_edge(rate, cap, floor)
            interval_ms = int(info_resp.get("fundingInterval", 0))
            print(
                f"{symbol} fundingRate={rate} netEdge={net_edge} interval={interval_ms}ms"
            )
    backoff = 1
    while True:  # pragma: no cover - long running loop
        try:
            for symbol in symbols:
                rate_resp = session.get(
                    f"{BINANCE_REST_BASE}/fapi/v1/fundingRate",
                    params={"symbol": symbol, "limit": 1},
                    timeout=10,
                ).json()
                if not rate_resp:
                    continue
                rate = float(rate_resp[0]["fundingRate"])

                info_resp: Dict[str, Any] = session.get(
                    f"{BINANCE_REST_BASE}/fapi/v1/fundingInfo",
                    params={"symbol": symbol},
                    timeout=10,
                ).json()
                cap = float(info_resp.get("fundingRateCap", 0))
                floor = float(info_resp.get("fundingRateFloor", 0))
                net_edge = compute_net_edge(rate, cap, floor)
                interval_ms = int(info_resp.get("fundingInterval", 0))
                print(
                    f"{symbol} fundingRate={rate} netEdge={net_edge} interval={interval_ms}ms"
                )
            time.sleep(interval)
            backoff = 1  # reset after successful poll
        except Exception as exc:  # pragma: no cover - network failures
            print("REST polling error", exc)
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)  # exponential backoff
