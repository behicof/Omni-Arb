"""
اینترفیس پایه برای پالیسی‌های معاملاتی.
"""
from typing import Protocol, Dict, Any

class Policy(Protocol):
    def decide(self, signal: Dict[str, Any], risk: Dict[str, Any]) -> Dict[str, Any]:
        """
        تصمیم‌گیری بر اساس سیگنال و پارامترهای ریسک.
        
        :param signal: دیکشنری سیگنال
        :param risk: دیکشنری پارامترهای ریسک
        :return: دیکشنری شامل {action: 'enter'|'exit'|'hold', size: float, leverage: int, sl: float, tp: float}
        """
        ...
