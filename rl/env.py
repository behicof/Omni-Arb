import numpy as np
import gymnasium as gym
from gymnasium import spaces


class TradingEnv(gym.Env):
    """Simple trading environment using microstructure data and risk flags.

    Observation space consists of microstructure features (price, spread, volume)
    and two binary risk flags. The action space is a single continuous value
    representing graded exposure between -1 (full short) and +1 (full long).
    """

    metadata = {"render.modes": []}

    def __init__(self, max_steps: int = 100, seed: int | None = None):
        super().__init__()
        self.max_steps = max_steps
        self.step_count = 0
        self.rng = np.random.default_rng(seed)

        # observation: price, spread, volume, risk_on, drawdown_flag
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(5,), dtype=np.float32
        )

        # action: graded exposure in [-1, 1]
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(1,), dtype=np.float32)
        self.state = np.zeros(5, dtype=np.float32)

    def _get_obs(self) -> np.ndarray:
        return self.state.copy()

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        self.step_count = 0
        price = 100 + self.rng.normal()
        spread = self.rng.uniform(0.01, 0.1)
        volume = self.rng.uniform(1, 10)
        risk_on = 0.0
        drawdown_flag = 0.0
        self.state = np.array([price, spread, volume, risk_on, drawdown_flag], dtype=np.float32)
        return self._get_obs(), {}

    def step(self, action: np.ndarray):
        self.step_count += 1
        exposure = float(np.clip(action[0], -1.0, 1.0))

        # simulate price change
        price_change = self.rng.normal(scale=0.1)
        reward = exposure * price_change

        price = self.state[0] + price_change
        spread = self.rng.uniform(0.01, 0.1)
        volume = self.rng.uniform(1, 10)
        risk_on = 1.0 if abs(exposure) > 0.5 else 0.0
        drawdown_flag = 1.0 if reward < -0.1 else 0.0
        self.state = np.array([price, spread, volume, risk_on, drawdown_flag], dtype=np.float32)

        terminated = self.step_count >= self.max_steps
        truncated = False
        info = {"reward": reward}
        return self._get_obs(), reward, terminated, truncated, info
