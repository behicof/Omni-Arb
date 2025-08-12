"""ماژول مدیریت ریسک و بارگذاری تنظیمات."""
from __future__ import annotations

from typing import Dict, Any

import yaml


def load_risk_config(path: str) -> Dict[str, Any]:
    """بارگذاری تنظیمات ریسک از فایل YAML."""
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}

    try:
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except (FileNotFoundError, PermissionError) as e:
        print(f"Risk config file error: {e}")
        return {}
    except yaml.YAMLError as e:
        print(f"YAML parsing error in risk config: {e}")
        return {}
def calculate_risk(order: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """اعمال حدود ریسک بر روی سفارش."""
    size = min(order.get("size", 1.0), config.get("risk_caps", {}).get("max_position_size", float("inf")))
    leverage = order.get("leverage", 1)
    return {"size": size, "leverage": leverage}
