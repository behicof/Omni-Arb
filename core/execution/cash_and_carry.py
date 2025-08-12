def calculate_basis(futures_price: float, spot_price: float) -> float:
    """Return the relative basis between futures and spot."""
    if spot_price == 0:
        raise ValueError("spot_price must be non-zero")
    return (futures_price - spot_price) / spot_price


def should_enter_basis_trade(basis: float, fees: float, carry_cost: float, slippage: float, threshold: float) -> bool:
    """Decide whether to enter a cash and carry trade."""
    net = basis - fees - carry_cost - slippage
    return net >= threshold
