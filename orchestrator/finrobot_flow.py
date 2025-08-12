"""Minimal orchestrator computing NetEdge from market data."""
from __future__ import annotations
from typing import Dict, Any
from core.calculations import net_edge_bps

DEFAULT_CONFIG: Dict[str, Any] = {
    "spot": 100.0,
    "future": 101.0,
    "costs_bps": 5.0,
}


def run(config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    cfg = DEFAULT_CONFIG.copy()
    if config:
        cfg.update(config)
    edge = net_edge_bps(cfg["spot"], cfg["future"], cfg["costs_bps"])
    return {"net_edge_bps": edge, "config": cfg}


if __name__ == "__main__":  # pragma: no cover
    run()
