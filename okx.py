"""Minimal OKX REST client with demo/live switch.

All demo requests automatically include the header ``x-simulated-trading: 1``
while live requests omit it.  OKX funding calculations clamp rates between a
cap and floor as described in the official documentation.  OKX have announced
that the formula may change (e.g. the historical 8‑hour sample), therefore the
implementation keeps the logic minimal and documents this behaviour here.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import requests

OKX_BASE_URL = "https://www.okx.com"


class OKXClient:
    """Simple wrapper around the OKX REST API."""

    def __init__(self, demo: bool = True) -> None:
        self.demo = demo
        self.session = requests.Session()
        if demo:
            # All demo requests must carry this header.
            self.session.headers.update({"x-simulated-trading": "1"})

    def request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Perform a REST request against OKX.

        When ``demo`` is False the ``x-simulated-trading`` header is omitted
        automatically to access the live environment.
        """
        url = f"{OKX_BASE_URL}{endpoint}"
        response = self.session.request(method, url, params=params, timeout=10)
        return response.json()
