"""Training utilities for reinforcement learning agents."""
from __future__ import annotations

from typing import Any

try:
    import hydra
    from omegaconf import DictConfig
except ImportError:  # pragma: no cover - optional dependency for tests
    hydra = None
    DictConfig = Any  # type: ignore


def train(cfg: Any):
    """Train an RL agent according to the provided Hydra config."""
    from stable_baselines3 import SAC, PPO
    from stable_baselines3.common.callbacks import BaseCallback
    from stable_baselines3.common.evaluation import evaluate_policy
    import numpy as np

    from .env import TradingEnv

    class OOSSharpeStop(BaseCallback):
        """Callback to stop training when out-of-sample Sharpe falls below threshold."""

        def __init__(self, eval_env, eval_freq: int, eval_episodes: int, threshold: float):
            super().__init__()
            self.eval_env = eval_env
            self.eval_freq = eval_freq
            self.eval_episodes = eval_episodes
            self.threshold = threshold

        def _on_step(self) -> bool:
            if self.n_calls % self.eval_freq != 0:
                return True
            returns, _ = evaluate_policy(
                self.model,
                self.eval_env,
                n_eval_episodes=self.eval_episodes,
                deterministic=True,
                return_episode_rewards=True,
            )
            returns = np.array(returns)
            sharpe = returns.mean() * np.sqrt(252) / (returns.std() + 1e-8)
            # stop training if Sharpe below threshold
            return bool(sharpe >= self.threshold)

    env = TradingEnv(seed=cfg.env.seed)
    eval_env = TradingEnv(seed=cfg.env.seed + 1)

    algo = cfg.algo.lower()
    if algo == "sac":
        model = SAC(cfg.model.policy, env, learning_rate=cfg.model.learning_rate, verbose=0)
    elif algo == "ppo":
        model = PPO(cfg.model.policy, env, learning_rate=cfg.model.learning_rate, verbose=0)
    else:  # pragma: no cover - safeguard
        raise ValueError(f"Unknown algorithm: {cfg.algo}")

    callback = OOSSharpeStop(
        eval_env,
        eval_freq=cfg.eval_freq,
        eval_episodes=cfg.eval_episodes,
        threshold=cfg.early_stop_sharpe,
    )
    model.learn(total_timesteps=cfg.train.total_timesteps, callback=callback)
    return model


if hydra is not None:

    @hydra.main(version_base=None, config_path="../conf/rl", config_name="sac")
    def main(cfg: DictConfig):
        train(cfg)

else:  # pragma: no cover - executed only when hydra isn't installed

    def main(cfg: DictConfig):  # type: ignore[override]
        raise ImportError("hydra-core is required to run this script")


if __name__ == "__main__":
    main()  # type: ignore[misc]
