"""ماژول اجرای سفارش با استفاده از GuardChecker."""
import asyncio
from typing import Dict, Any

from .guards import GuardChecker


class OrderExecutor:
    """کلاس اجرای سفارش‌ها (به صورت dry-run برای تست اولیه)."""

    def __init__(self, config_path: str = "configs/risk.yml") -> None:
        self.guard = GuardChecker.from_yaml(config_path)

    async def place(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """شبیه‌سازی ارسال سفارش با بررسی گاردها."""
        if action.get("action") == "ENTER":
            net_edge = action.get("NetEdge_bps", 0)
            if net_edge < self.guard.net_edge_bps_threshold or not self.guard.passes(action):
                self.guard.log_trade({**action, "status": "blocked"})
                return {"status": "blocked", "details": action}
        await asyncio.sleep(1)
        self.guard.log_trade({**action, "status": "success"})
        return {"status": "success", "details": action}
