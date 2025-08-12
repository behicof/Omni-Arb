"""گاردهای بررسی قبل از ارسال سفارش."""
from __future__ import annotations

import datetime as _dt
import json
from typing import Dict, Any

import yaml


class GuardChecker:
    """بررسی شرایط تأخیر، اسلیپیج، عمق و حدود ریسک."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    @classmethod
    def from_yaml(cls, path: str) -> "GuardChecker":
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        return cls(data)

    @property
    def net_edge_bps_threshold(self) -> float:
        return float(self.config.get("net_edge_bps_threshold", 0))

    def passes(self, metrics: Dict[str, Any]) -> bool:
        if metrics.get("latency_ms", 0) > self.config.get("max_latency_ms", float("inf")):
            return False
        if metrics.get("slippage_bps", 0) > self.config.get("max_slippage_bps", float("inf")):
            return False
        if metrics.get("depth_units", 0) < self.config.get("min_depth_units", 0):
            return False
        caps = self.config.get("risk_caps", {})
        if metrics.get("notional", 0) > caps.get("max_notional", float("inf")):
            return False
        if metrics.get("daily_loss", 0) > caps.get("max_daily_loss", float("inf")):
            return False
        return True

    def log_trade(self, trade: Dict[str, Any]) -> None:
        """ثبت لاگ معامله."""
        entry = {"timestamp": _dt.datetime.utcnow().isoformat(), **trade}
        with open("trade_audit.log", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
