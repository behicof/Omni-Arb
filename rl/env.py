"""Trading environment capturing market microstructure and risk flags."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import yaml

from sim.simulator_tca import TCASimulator, Leg


class MicrostructureEnv(gym.Env):
    """Simple environment combining microstructure data with risk limits.

    Observation: ``[fill_prob, adverse_selection, latency_ms, depth,
    risk_flag_global, risk_flag_symbol]``

    Action: graded exposure in ``[-1, 1]`` representing fraction of
    ``max_notional`` to trade. Positive values are long, negative short.
    """

    metadata = {"render_modes": []}

    def __init__(self, max_steps: int = 100, risk_file: str | Path = "risk.yml"):
        super().__init__()
        self.max_steps = max_steps
        self.sim = TCASimulator(fill_prob=0.9, adverse_selection=0.0, latency_ms=50, depth=1000)
        self.step_count = 0
        self.position_notional = 0.0

        risk_path = Path(risk_file)
        self.risk_cfg: Dict[str, Any] = (
            yaml.safe_load(risk_path.read_text()) if risk_path.exists() else {}
        )
        self.max_notional = float(self.risk_cfg.get("max_notional_per_trade", 1e4))
        self.per_symbol_caps: Dict[str, float] = self.risk_cfg.get("per_symbol_caps", {})

        # State: microstructure (4) + risk flags (2)
        self.observation_space = spaces.Box(-np.inf, np.inf, shape=(6,), dtype=np.float32)
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(1,), dtype=np.float32)

    # ------------------------------------------------------------------
    def _microstructure(self) -> np.ndarray:
        """Return current microstructure features."""
        return np.array(
            [
                self.sim.fill_prob,
                self.sim.adverse_selection,
                self.sim.latency_ms,
                self.sim.depth,
            ],
            dtype=np.float32,
        )

    def _risk_flags(self) -> np.ndarray:
        """Return risk limit flags as binary indicators."""
        global_flag = float(self.position_notional > self.max_notional)
        symbol_cap = float(
            self.position_notional
            > self.per_symbol_caps.get("BTCUSDT", float("inf"))
        )
        return np.array([global_flag, symbol_cap], dtype=np.float32)

    def _get_obs(self) -> np.ndarray:
        return np.concatenate([self._microstructure(), self._risk_flags()])

    # ------------------------------------------------------------------
    def reset(self, *, seed: int | None = None, options: Dict[str, Any] | None = None):
        super().reset(seed=seed)
        self.step_count = 0
        self.position_notional = 0.0
        return self._get_obs(), {}

    # ------------------------------------------------------------------
    def step(self, action: np.ndarray):
        action = float(np.clip(action[0], -1.0, 1.0))
        notional = abs(action) * self.max_notional
        side = "buy" if action >= 0 else "sell"

        leg = Leg(side=side, quantity=notional, limit_price=100.0, arrival_mid=100.0)
        result = self.sim.simulate_leg(leg)
        reward = float(-result.implementation_shortfall)

        self.position_notional += notional
        self.step_count += 1

        obs = self._get_obs()
        terminated = bool(self._risk_flags().any())
        truncated = self.step_count >= self.max_steps
        info: Dict[str, Any] = {}
        return obs, reward, terminated, truncated, info

    # ------------------------------------------------------------------
    def render(self):  # pragma: no cover - not needed for tests
        pass

    def close(self):  # pragma: no cover - nothing to clean up
        pass
