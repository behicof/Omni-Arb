"""نسخه‌ی ساده‌شده‌ی موتور اجرا برای تست."""

from typing import Dict, Any
import asyncio


class OrderExecutor:
    async def place(self, action: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return {"status": "success", "details": action}
