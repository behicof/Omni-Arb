"""Position sizing utilities."""

def size_position(max_notional: float, price: float, margin_buffer: float) -> float:
    """Compute order quantity given max notional and margin buffer."""
    if price <= 0:
        raise ValueError("price must be positive")
    base_qty = max_notional / price
    return base_qty * (1 - margin_buffer)
