"""Minimal Binance REST helper functions for testing."""
from __future__ import annotations

import requests
from typing import Dict, Any, Optional
import datetime

BASE_URL = "https://fapi.binance.com"

class BinanceAPIError(Exception):
    """Exception raised for Binance API errors."""
    def __init__(self, code: int, msg: str):
        super().__init__(f"{code}: {msg}")
        self.code = code
        self.msg = msg

def _request(method: str, path: str, *, params: Optional[Dict[str, Any]] = None,
             data: Optional[Dict[str, Any]] = None, session: Optional[requests.sessions.Session] = None) -> Any:
    sess = session or requests
    url = BASE_URL + path
    resp = getattr(sess, method.lower())(url, params=params, data=data)
    result = resp.json()
    if isinstance(result, dict) and "code" in result and result.get("code") not in (0, 200):
        raise BinanceAPIError(result["code"], result.get("msg", ""))
    return result

def place_order(order: Dict[str, Any], *, live: bool = True, session: Optional[requests.sessions.Session] = None) -> Dict[str, Any]:
    """Place an order or test order depending on ``live`` flag."""
    path = "/fapi/v1/order" + ("" if live else "/test")
    return _request("post", path, params=order, session=session)

def set_position_mode(hedge: bool, *, session: Optional[requests.sessions.Session] = None) -> Dict[str, Any]:
    data = {"dualSidePosition": "true" if hedge else "false"}
    return _request("post", "/fapi/v1/positionSide/dual", data=data, session=session)

def get_position_mode(*, session: Optional[requests.sessions.Session] = None) -> bool:
    result = _request("get", "/fapi/v1/positionSide/dual", session=session)
    if isinstance(result, dict):
        return result.get("dualSidePosition", False)
    return False

def funding_pnl_report(start_time: int, end_time: int, *, symbol: Optional[str] = None,
                       session: Optional[requests.sessions.Session] = None) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "incomeType": "FUNDING_FEE",
        "startTime": start_time,
        "endTime": end_time,
    }
    if symbol:
        params["symbol"] = symbol
    records = _request("get", "/fapi/v1/income", params=params, session=session)
    report: Dict[str, Dict[str, Any]] = {}
    for rec in records:
        ts = int(rec["time"])
        date = datetime.datetime.utcfromtimestamp(ts / 1000).strftime("%Y-%m-%d")
        income = float(rec["income"])
        day = report.setdefault(date, {"total": 0.0, "settlements": []})
        day["total"] += income
        day["settlements"].append(ts)
    return report
