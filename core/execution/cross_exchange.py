from dataclasses import dataclass

@dataclass
class CrossExchangeEdge:
    """Edge computed between two exchanges."""
    price_a: float
    price_b: float
    fees: float

    def net_edge(self) -> float:
        return self.price_b - self.price_a - self.fees


def is_profitable(edge: CrossExchangeEdge, threshold: float) -> bool:
    """Check if price difference minus fees exceeds threshold."""
    return edge.net_edge() >= threshold
