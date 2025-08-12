"""
ماژول مدیریت حالت پوزیشن و اعتبارسنجی سفارش‌ها برای حالت Hedge.
"""
from typing import Dict, Any


class PositionMode:
    """انواع حالت‌های پوزیشن قابل پشتیبانی."""
    ONE_WAY = "ONE_WAY"
    HEDGE = "HEDGE"


_current_mode = PositionMode.ONE_WAY


def set_position_mode(mode: str) -> None:
    """تنظیم حالت پوزیشن سراسری."""
    if mode not in (PositionMode.ONE_WAY, PositionMode.HEDGE):
        raise ValueError("mode must be ONE_WAY or HEDGE")
    global _current_mode
    _current_mode = mode


def get_position_mode() -> str:
    """دریافت حالت پوزیشن فعلی."""
    return _current_mode


def validate_order(order: Dict[str, Any]) -> None:
    """
    اعتبارسنجی پارامترهای سفارش بر اساس حالت پوزیشن.

    در حالت Hedge وجود `positionSide` اجباری و باید یکی از مقادیر LONG/SHORT باشد.
    همچنین فیلد `reduceOnly` در صورت وجود باید مقدار بولی داشته باشد.

    در حالت One Way استفاده از `positionSide` مجاز نیست.
    """
    mode = get_position_mode()
    position_side = order.get("positionSide")
    reduce_only = order.get("reduceOnly")

    if mode == PositionMode.HEDGE:
        if position_side not in ("LONG", "SHORT"):
            raise ValueError("positionSide required for hedge mode and must be LONG or SHORT")
        if reduce_only is not None and not isinstance(reduce_only, bool):
            raise ValueError("reduceOnly must be boolean")
    else:
        if position_side is not None:
            raise ValueError("positionSide is not allowed in one-way mode")
        if reduce_only is not None and not isinstance(reduce_only, bool):
            raise ValueError("reduceOnly must be boolean")
