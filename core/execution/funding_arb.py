from dataclasses import dataclass

@dataclass
class FundingArbConfig:
    """Configuration for funding rate arbitrage."""
    theta: float  # minimum net edge required to enter a trade

class FundingArb:
    """Simple rule based funding rate arbitrage module."""
    def __init__(self, config: FundingArbConfig) -> None:
        self.config = config

    def net_edge(self, funding_recv: float, fees: float, borrow: float, slippage: float) -> float:
        """Compute net edge of a potential funding trade."""
        return funding_recv - fees - borrow - slippage

    def should_enter(self, funding_recv: float, fees: float, borrow: float, slippage: float) -> bool:
        """Return True if net edge meets threshold theta."""
        edge = self.net_edge(funding_recv, fees, borrow, slippage)
        return edge >= self.config.theta
