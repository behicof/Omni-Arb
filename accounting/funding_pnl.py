"""محاسبه و ثبت PnL تأمین مالی.

این ماژول هزینه‌ی تأمین مالی را بر اساس نرمال پوزیشن و نرخ تأمین مالی
محاسبه کرده و هر پنجره‌ی تسویه را لاگ می‌کند. همچنین خلاصه‌ی روزانه‌ی
تأمین مالی را برمی‌گرداند.
"""

from __future__ import annotations

import datetime as _dt
import logging
from dataclasses import dataclass
from collections import defaultdict
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

# مقدار پیش‌فرض فاصله‌ی تسویه در ساعت
DEFAULT_SCHEDULE_HOURS = 8

# نگاشت فاصله‌ی تسویه برای سمبل‌های خاص (بر حسب ساعت)
# در صورت اعلام رسمی می‌توان این نگاشت را به‌روزرسانی کرد.
PER_SYMBOL_SCHEDULE: Dict[str, int] = {}


def read_settlement_schedule(symbol: str) -> _dt.timedelta:
    """خواندن فاصله‌ی تسویه برای سمبل مشخص.

    ابتدا از نگاشت محلی استفاده می‌کنیم و در صورت عدم وجود، تلاش می‌کنیم
    اطلاعات را از API رسمی صرافی MEXC بخوانیم. در صورت بروز خطا یا عدم
    دسترسی، مقدار پیش‌فرض ۸ ساعت برگردانده می‌شود.
    """

    sym = symbol.upper()
    hours = PER_SYMBOL_SCHEDULE.get(sym)
    if hours is not None:
        return _dt.timedelta(hours=hours)

    url = f"https://contract.mexc.com/api/v1/contract/detail/{sym}"
    try:
        resp = httpx.get(url, timeout=10)
        data = resp.json().get("data", {})
        interval_ms = data.get("fundingInterval")
        if interval_ms:
            # API مقدار میلی‌ثانیه برمی‌گرداند
            hours = int(interval_ms) / 3_600_000
            return _dt.timedelta(hours=hours)
    except Exception as exc:  # pragma: no cover - فقط جهت لاگ خطا
        logger.debug("failed to fetch settlement schedule for %s: %s", sym, exc)

    return _dt.timedelta(hours=DEFAULT_SCHEDULE_HOURS)


@dataclass
class FundingRecord:
    """ثبت هر رخداد تأمین مالی."""

    timestamp: _dt.datetime
    symbol: str
    position_nominal: float
    funding_rate: float
    funding_fee: float


class FundingPnL:
    """مدیریت و خلاصه‌سازی سود/زیان تأمین مالی."""

    def __init__(self) -> None:
        self.records: List[FundingRecord] = []

    def log_window(
        self,
        symbol: str,
        position_nominal: float,
        funding_rate: float,
        timestamp: Optional[_dt.datetime] = None,
    ) -> float:
        """محاسبه و ثبت هزینه‌ی تأمین مالی برای یک پنجره‌ی تسویه.

        علامت نرخ مشخص می‌کند که هزینه پرداخت می‌شود یا دریافت. مقدار
        بازگشتی همان هزینه‌ی تأمین مالی است.
        """

        if timestamp is None:
            timestamp = _dt.datetime.utcnow()

        fee = position_nominal * funding_rate
        record = FundingRecord(timestamp, symbol, position_nominal, funding_rate, fee)
        self.records.append(record)
        logger.info(
            "funding %s | nominal=%s rate=%s fee=%s",
            symbol,
            position_nominal,
            funding_rate,
            fee,
        )
        return fee

    def summarize_window(
        self,
        start: _dt.datetime,
        end: _dt.datetime,
        symbol: Optional[str] = None,
    ) -> Dict[str, float]:
        """جمع تأمین مالی تحقق‌یافته در بازه‌ی زمانی داده‌شده."""

        summary: Dict[str, float] = defaultdict(float)
        for rec in self.records:
            if start <= rec.timestamp < end and (symbol is None or rec.symbol == symbol):
                summary[rec.symbol] += rec.funding_fee
        return dict(summary)

    def summarize_daily(self) -> Dict[_dt.date, float]:
        """خلاصه‌ی روزانه‌ی تأمین مالی."""

        summary: Dict[_dt.date, float] = defaultdict(float)
        for rec in self.records:
            summary[rec.timestamp.date()] += rec.funding_fee
        return dict(summary)
