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
        default=os.getenv("WS_DISABLED", "").lower() in {"1", "true", "yes"},
        help="Use REST polling instead of WebSocket feeds."
        " Set WS_DISABLED=1 to enable by default.",
    )
    return parser.parse_args([] if __name__ != "__main__" else None)


def main() -> None:
    args = _parse_args()

    if args.ws_disabled:
        LOGGER.warning("WS blocked → using REST fallback")
        from feeds import rest_mark_funding

        asyncio.run(rest_mark_funding.run())
    else:
        from binance_ws import subscribe_mark_price

        asyncio.run(subscribe_mark_price())


if __name__ == "__main__":  # pragma: no cover
    main()
