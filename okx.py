"""
ماژول ارتباط با OKX برای پشتیبانی از حالت Live و Demo.
"""
from typing import Any, Dict, Optional
import os
import requests

BASE_URL = "https://www.okx.com"


def _request(method: str, endpoint: str, *, params: Optional[Dict[str, Any]] = None,
             data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None,
             live: Optional[int] = None) -> Dict[str, Any]:
    """
    ارسال درخواست به OKX. در حالت Demo هدر x-simulated-trading: 1 اضافه می‌شود.

    :param method: نوع متد HTTP
    :param endpoint: مسیر اندپوینت (باید با /api/v5/ شروع شود)
    :param params: پارامترهای کوئری
    :param data: بدنه درخواست
    :param headers: هدرهای اضافی
    :param live: 1 برای حالت واقعی، 0 برای Demo. در صورت None از متغیر محیطی LIVE استفاده می‌شود.
    :return: پاسخ به صورت دیکشنری
    """
    if live is None:
        live = int(os.getenv("LIVE", "1"))
    url = f"{BASE_URL}{endpoint}"
    headers = headers.copy() if headers else {}
    if endpoint.startswith("/api/v5/") and not live:
        headers.setdefault("x-simulated-trading", "1")
    response = requests.request(method, url, params=params, json=data, headers=headers)
    return response.json()


def place_order(order: Dict[str, Any], live: Optional[int] = None) -> Dict[str, Any]:
    """ارسال سفارش (v5) به OKX."""
    return _request("POST", "/api/v5/trade/order", data=order, live=live)
