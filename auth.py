"""
ماژول احراز هویت برای صرافی MEXC فیوچرز.

TODO: پیاده‌سازی امضای درخواست و تولید هدرهای لازم.
"""
from typing import Dict

def generate_auth_headers(api_key: str, secret: str) -> Dict[str, str]:
    """
    تولید هدرهای احراز هویت.
    
    :param api_key: کلید API
    :param secret: کلید مخفی
    :return: دیکشنری حاوی هدرها
    """
    # TODO: ایجاد امضای درخواست مناسب
    return {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }