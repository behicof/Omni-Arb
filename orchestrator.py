"""Simple orchestrator integrating guard checks."""
from typing import Dict
from guards import (
    load_risk_config,
    check_latency,
    check_slippage,
    check_depth,
    check_risk,
)


class Orchestrator:
    """Evaluate signals and emit trading actions."""

    def __init__(self, theta: float, live: bool = False, risk_path: str = "risk.yml") -> None:
        self.theta = theta
        self.live = live
        self.risk_cfg = load_risk_config(risk_path)

    def evaluate(self, signal: Dict[str, float]) -> str:
        """Return "ENTER" when all guard conditions pass."""
        latency_ok = check_latency(signal.get("latency_ms", 0), signal.get("max_leg_latency_ms", float("inf")))
        slippage_ok = check_slippage(signal.get("slippage_bps", 0), signal.get("max_slippage_bps", float("inf")))
        depth_ok = check_depth(signal.get("depth_notional", 0), signal.get("min_depth_notional", 0))
        risk_ok = check_risk(signal.get("symbol", ""), signal.get("notional", 0), self.risk_cfg)
        edge_ok = signal.get("net_edge", 0) >= self.theta

        if all([latency_ok, slippage_ok, depth_ok, risk_ok, edge_ok]):
            return "ENTER"  # still dry-run when live=False
        return "HOLD"
