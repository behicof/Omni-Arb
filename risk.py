"""
ماژول محاسبه ریسک و اعتبارسنجی سفارش.
"""
from typing import Dict, Any
import requests


def _fetch_exchange_info(symbol: str, exchange: str = "BINANCE") -> Dict[str, Any]:
    """دریافت اطلاعات نماد از صرافی مشخص."""
    if exchange == "BINANCE":
        url = "https://api.binance.com/api/v3/exchangeInfo"
        params = {"symbol": symbol}
    elif exchange == "OKX":
        url = "https://www.okx.com/api/v5/public/instruments"
        params = {"instType": "SPOT", "instId": symbol}
    else:
        raise ValueError("Unsupported exchange")
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def validate_order_filters(symbol: str, quantity: float, price: float, exchange: str = "BINANCE") -> None:
    """اعتبارسنجی فیلترهای LOT_SIZE و MIN_NOTIONAL قبل از ارسال سفارش."""
    info = _fetch_exchange_info(symbol, exchange)
    if exchange == "BINANCE":
        symbol_info = info.get("symbols", [])[0]
    else:
        # ساختار پاسخ OKX متفاوت است؛ برای سادگی از اولین رکورد استفاده می‌کنیم
        symbol_info = info.get("data", [])[0]
    filters = {f["filterType"]: f for f in symbol_info.get("filters", [])}

    lot = filters.get("LOT_SIZE", {})
    step_size = float(lot.get("stepSize", 1))
    min_qty = float(lot.get("minQty", 0))
    max_qty = float(lot.get("maxQty", float("inf")))

    min_notional = float(filters.get("MIN_NOTIONAL", {}).get("minNotional", 0))
    notional = quantity * price

    qty_ok = min_qty <= quantity <= max_qty and (quantity / step_size).is_integer()
    notional_ok = notional >= min_notional
    if not (qty_ok and notional_ok):
        raise ValueError("Order does not satisfy LOT_SIZE یا MIN_NOTIONAL")


def calculate_risk(order: Dict[str, Any]) -> Dict[str, Any]:
    """
    محاسبه تنظیمات ریسک برای سفارش.

    :param order: دیکشنری سفارش اولیه
    :return: دیکشنری شامل تنظیمات ریسک (size, leverage و غیره)
    """
    symbol = order.get("symbol")
    quantity = float(order.get("quantity", 0))
    price = float(order.get("price", 0))
    exchange = order.get("exchange", "BINANCE")
    if symbol and quantity and price:
        validate_order_filters(symbol, quantity, price, exchange)
    return {"size": order.get("size", 1.0), "leverage": order.get("leverage", 1)}