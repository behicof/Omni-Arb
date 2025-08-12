"""Utility for querying and setting Binance Futures position mode.

This module provides helper functions for the `/fapi/v1/positionSide/dual`
endpoints which allow switching between one-way and hedge (dual) position
modes. The functions accept an optional ``session`` argument so they can be
conveniently unit tested by injecting a mock object implementing the `requests`
interface.
"""
from __future__ import annotations

from typing import Any, Dict
import requests

BASE_URL = "https://fapi.binance.com"


def get_position_mode(session: Any = requests) -> bool:
    """Return ``True`` if dual-side position mode is enabled.

    Parameters
    ----------
    session: Any
        HTTP session compatible with :mod:`requests`. Defaults to the global
        :mod:`requests` module.
    """
    resp = session.get(f"{BASE_URL}/fapi/v1/positionSide/dual")
    resp.raise_for_status()
    data: Dict[str, Any] = resp.json()
    # API returns "true" or "false" as strings
    return data.get("dualSidePosition") == "true"


def set_position_mode(dual: bool, session: Any = requests) -> Dict[str, Any]:
    """Set dual-side position mode.

    Parameters
    ----------
    dual: bool
        ``True`` to enable hedge (dual-side) mode, ``False`` for one-way mode.
    session: Any
        HTTP session compatible with :mod:`requests`.
    """
    mode = "true" if dual else "false"
    resp = session.post(
        f"{BASE_URL}/fapi/v1/positionSide/dual", params={"dualSidePosition": mode}
    )
    resp.raise_for_status()
    return resp.json()
