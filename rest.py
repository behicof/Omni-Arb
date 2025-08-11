"""
ماژول ارتباط REST با صرافی MEXC فیوچرز.

TODO: پیاده‌سازی دریافت داده‌های بازار، ایجاد سفارش و سایر عملیات REST.
"""
from typing import Any, Dict
import requests

BASE_URL = "https://contract.mexc.com"

def get_market_data(endpoint: str, params: Dict[str, Any] = {}) -> Dict[str, Any]:
    """
    دریافت داده‌های بازار از MEXC فیوچرز.
    
    :param endpoint: مسیر API
    :param params: پارامترهای درخواست
    :return: پاسخ به صورت دیکشنری
    """
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, params=params)
    return response.json()

def place_order(order_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    ارسال سفارش به MEXC فیوچرز.
    
    :param order_details: اطلاعات سفارش
    :return: نتیجه سفارش
    """
    url = f"{BASE_URL}/api/v1/private/order"
    response = requests.post(url, json=order_details)
    return response.json()