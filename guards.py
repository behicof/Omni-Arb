"""Utility guard checks for order validation."""
from typing import Dict
import yaml


def load_risk_config(path: str = "risk.yml") -> Dict[str, float]:
    """Load risk configuration from a YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_latency(latency_ms: float, max_leg_latency_ms: float) -> bool:
    return latency_ms <= max_leg_latency_ms


def check_slippage(slippage_bps: float, max_slippage_bps: float) -> bool:
    return slippage_bps <= max_slippage_bps


def check_depth(depth_notional: float, min_depth_notional: float) -> bool:
    return depth_notional >= min_depth_notional


def check_risk(symbol: str, notional: float, risk_cfg: Dict[str, Dict[str, float]]) -> bool:
    """Validate notional against risk caps."""
    max_trade = risk_cfg.get("max_notional_per_trade", float("inf"))
    per_symbol = risk_cfg.get("per_symbol_caps", {})
    symbol_cap = per_symbol.get(symbol, float("inf"))
    return notional <= max_trade and notional <= symbol_cap
