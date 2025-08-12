"""اینترفیس اجرایی."""
from typing import Protocol, Dict, Any


class Executor(Protocol):
    async def place(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """ارسال سفارش با توجه به اکشن."""
        ...
