"""Risk guard helpers for execution core."""

def check_slippage(expected: float, actual: float, max_slippage: float) -> bool:
    """Validate that slippage is within allowed basis points."""
    if expected == 0:
        return False
    slip = abs(actual - expected) / expected
    return slip <= max_slippage


def check_latency(latency_ms: float, max_latency_ms: float) -> bool:
    return latency_ms <= max_latency_ms


def check_depth(depth: float, min_depth: float) -> bool:
    return depth >= min_depth
