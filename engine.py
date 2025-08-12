"""Entry point for market data engine.

This engine uses WebSocket feeds by default. It can be switched to a REST
fallback via the ``--ws-disabled`` flag or by setting ``WS_DISABLED=1`` in the
environment.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os


LOGGER = logging.getLogger(__name__)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Market data engine")
    parser.add_argument(
        "--ws-disabled",
        action="store_true",
        help="Use REST polling instead of WebSocket feeds",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    ws_disabled = args.ws_disabled or os.getenv("WS_DISABLED") == "1"

    if ws_disabled:
        LOGGER.warning("WebSocket disabled, using REST fallback")
        from feeds import rest_mark_funding

        asyncio.run(rest_mark_funding.run())
    else:
        from binance_ws import subscribe_mark_price

        asyncio.run(subscribe_mark_price())


if __name__ == "__main__":  # pragma: no cover
    main()
