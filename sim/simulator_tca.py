from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Iterable
import csv
import statistics


@dataclass
class Leg:
    """Parameters describing a single trading leg."""
    side: str
    quantity: float
    limit_price: float
    arrival_mid: float


@dataclass
class SimulationResult:
    """Outcome for a simulated leg."""
    filled_qty: float
    avg_price: float
    implementation_shortfall: float


@dataclass
class TCASimulator:
    """Simple limit order fill simulator.

    Attributes capture high level market microstructure effects such as
    fill probability, adverse selection, latency and depth.  These values
    can be calibrated from live trading logs using :meth:`calibrate_from_logs`.
    """

    fill_prob: float
    adverse_selection: float
    latency_ms: float
    depth: float

    @classmethod
    def calibrate_from_logs(cls, path: str | Path) -> "TCASimulator":
        """Calibrate simulator parameters from a CSV log file.

        The log is expected to contain the following columns:
        ``latency_ms`` – time between decision and exchange receipt,
        ``depth`` – available quantity at the limit price,
        ``arrival_mid`` and ``post_fill_mid`` – mid prices, and ``filled``
        indicating whether the order fully filled (``1``/``0`` or
        ``true``/``false``).
        """
        file = Path(path)
        if not file.exists():  # pragma: no cover - defensive coding
            raise FileNotFoundError(f"log file not found: {file}")

        latencies: List[float] = []
        depths: List[float] = []
        slippages: List[float] = []
        filled, total = 0, 0

        with file.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                total += 1
                if row.get("filled", "").lower() in {"1", "true", "yes"}:
                    filled += 1
                try:
                    latencies.append(float(row["latency_ms"]))
                    depths.append(float(row["depth"]))
                    slippages.append(float(row["post_fill_mid"]) - float(row["arrival_mid"]))
                except KeyError:
                    # skip rows missing calibration fields
                    continue

        fill_prob = filled / total if total else 1.0
        latency = statistics.mean(latencies) if latencies else 0.0
        depth = statistics.mean(depths) if depths else 1.0
        adverse = statistics.mean(slippages) if slippages else 0.0

        return cls(fill_prob=fill_prob, adverse_selection=adverse, latency_ms=latency, depth=depth)

    # ------------------------------------------------------------------
    def _effective_fill_ratio(self, qty: float) -> float:
        """Probability of a fill accounting for depth and latency."""
        depth_ratio = min(1.0, self.depth / qty)
        latency_factor = max(0.0, 1.0 - self.latency_ms / 1000.0)
        return self.fill_prob * depth_ratio * latency_factor

    def simulate_leg(self, leg: Leg) -> SimulationResult:
        """Simulate execution for a single leg and compute shortfall."""
        ratio = self._effective_fill_ratio(leg.quantity)
        filled_qty = leg.quantity * ratio

        adverse_move = self.adverse_selection * (self.latency_ms / 1000.0)

        if leg.side.lower() == "buy":
            exec_price = min(leg.limit_price, leg.arrival_mid + adverse_move)
            shortfall = (exec_price - leg.arrival_mid) * filled_qty
        else:  # sell
            exec_price = max(leg.limit_price, leg.arrival_mid - adverse_move)
            shortfall = (leg.arrival_mid - exec_price) * filled_qty

        return SimulationResult(filled_qty=filled_qty, avg_price=exec_price, implementation_shortfall=shortfall)

    def simulate_order(self, legs: Iterable[Leg]) -> List[SimulationResult]:
        """Simulate a list of legs returning per leg results."""
        return [self.simulate_leg(leg) for leg in legs]
