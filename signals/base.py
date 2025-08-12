"""
اینترفیس پایه برای سیگنال‌ها.
"""
from typing import Protocol, Dict, Any


class Signal(Protocol):
    def compute(self, market: str, timestamp: int) -> Dict[str, Any]:
        """تولید سیگنال برای بازار مشخص."""
        ...
