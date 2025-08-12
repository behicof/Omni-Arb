"""
ماژول ارتباط با بایننس فیوچرز برای ارسال سفارش‌ها.
"""
from typing import Any, Dict, Optional
import os
import requests

BASE_URL = "https://fapi.binance.com"


def place_order(order: Dict[str, Any], live: Optional[int] = None) -> Dict[str, Any]:
    """
    ارسال سفارش به بایننس. در صورت LIVE=0 درخواست به اندپوینت تست ارسال می‌شود.

    :param order: اطلاعات سفارش
    :param live: 1 برای ارسال واقعی، 0 برای تست. اگر مقدار داده نشود از متغیر محیطی LIVE استفاده می‌شود.
    :return: پاسخ به صورت دیکشنری
    """
    if live is None:
        live = int(os.getenv("LIVE", "0"))
    endpoint = "/fapi/v1/order" if live else "/fapi/v1/order/test"
    url = f"{BASE_URL}{endpoint}"
    response = requests.post(url, data=order)
    return response.json()
