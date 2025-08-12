"""Funding rate polling and NetEdge computation for Binance Futures.

This module fetches funding rate history and funding info (cap/floor/interval)
from Binance every second and publishes computed NetEdge in basis points to the
orchestrator.

It also documents OKX's funding fee mechanism for reference.
"""
import asyncio
from typing import Dict, List, Callable

import requests

BINANCE_FUNDING_RATE_URL = "https://fapi.binance.com/fapi/v1/fundingRate"
BINANCE_FUNDING_INFO_URL = "https://fapi.binance.com/fapi/v1/fundingInfo"


def _clamp(value: float, floor: float, cap: float) -> float:
    """Clamp *value* between *floor* and *cap*."""
    return max(min(value, cap), floor)


def fetch_funding_rate(symbol: str) -> float:
    """Fetch latest funding rate for *symbol* from Binance."""
    resp = requests.get(
        BINANCE_FUNDING_RATE_URL,
        params={"symbol": symbol, "limit": 1},
        timeout=10,
        proxies={"http": None, "https": None},
    )
    data = resp.json()
    return float(data[0]["fundingRate"])


def fetch_funding_info(symbol: str) -> Dict[str, float]:
    """Fetch funding cap/floor/interval for *symbol* from Binance."""
    resp = requests.get(
        BINANCE_FUNDING_INFO_URL,
        params={"symbol": symbol},
        timeout=10,
        proxies={"http": None, "https": None},
    )
    data = resp.json()[0]
    return {
        "cap": float(data.get("fundingRateCap", 0)),
        "floor": float(data.get("fundingRateFloor", 0)),
        "intervalHours": float(data.get("fundingIntervalHours", 0)),
        # Binance provides estimated and last funding rates; use estimated as proxy
        "avgPremium": float(data.get("estimatedRate") or data.get("lastFundingRate") or 0),
    }


def compute_net_edge_bps(symbol: str) -> float:
    """Compute NetEdge in basis points for *symbol*.

    NetEdge = fundingRate - Clamp[avgPremium, cap, floor]
    OKX funding fee mechanism (for documentation):
        funding_rate = Clamp[average_premium_index, cap, floor]
    where Clamp[x, cap, floor] = min(max(x, floor), cap)
    """
    rate = fetch_funding_rate(symbol)
    info = fetch_funding_info(symbol)
    clamped = _clamp(info["avgPremium"], info["floor"], info["cap"])
    return (rate - clamped) * 10_000


def publish_to_orchestrator(symbol: str, edge_bps: float) -> None:
    """Publish NetEdge to orchestrator (currently logs to stdout)."""
    payload = {"symbol": symbol, "netEdge_bps": edge_bps}
    # TODO: Replace print with actual orchestrator publication (e.g., HTTP POST)
    print("Publishing", payload)


async def poll_net_edges(
    symbols: List[str], publish: Callable[[str, float], None], iterations: int | None = None
) -> None:
    """Poll Binance every second and publish NetEdge for *symbols*.

    :param symbols: لیست نمادها
    :param publish: تابع انتشار به orchestrator
    :param iterations: تعداد تکرار (None برای حلقه بی‌نهایت)
    """
    count = 0
    while iterations is None or count < iterations:
        for sym in symbols:
            try:
                edge = compute_net_edge_bps(sym)
            except Exception as exc:  # noqa: BLE001 - log and continue
                print(f"Error computing NetEdge for {sym}: {exc}")
                continue
            publish(sym, edge)
        count += 1
        await asyncio.sleep(1)


if __name__ == "__main__":
    # Example run for two iterations to avoid infinite loop in demos/tests.
    asyncio.run(poll_net_edges(["BTCUSDT"], publish_to_orchestrator, iterations=2))
