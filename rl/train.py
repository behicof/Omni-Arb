"""Training script for RL agents with early stopping based on OOS Sharpe."""

from __future__ import annotations

from typing import Any

import numpy as np
import hydra
from omegaconf import DictConfig
from stable_baselines3 import SAC, PPO
from stable_baselines3.common.callbacks import BaseCallback

from .env import MicrostructureEnv


class SharpeEarlyStopCallback(BaseCallback):
    """Stop training if out-of-sample Sharpe fails to improve."""

    def __init__(self, eval_env: MicrostructureEnv, eval_freq: int = 1000, patience: int = 5):
        super().__init__()
        self.eval_env = eval_env
        self.eval_freq = eval_freq
        self.patience = patience
        self.best_sharpe = -np.inf
        self.wait = 0
        self.stop_training = False

    def _on_step(self) -> bool:
        if self.n_calls % self.eval_freq == 0:
            returns = []
            for _ in range(5):
                obs, _ = self.eval_env.reset()
                done = False
                total = 0.0
                while not done:
                    action, _ = self.model.predict(obs, deterministic=True)
                    obs, reward, terminated, truncated, _ = self.eval_env.step(action)
                    done = terminated or truncated
                    total += reward
                returns.append(total)
            returns = np.array(returns)
            sharpe = returns.mean() / (returns.std() + 1e-8)
            if sharpe > self.best_sharpe:
                self.best_sharpe = sharpe
                self.wait = 0
            else:
                self.wait += 1
            if self.wait >= self.patience:
                self.stop_training = True
                return False
        return True


@hydra.main(version_base=None, config_path="../conf/rl", config_name="sac")
def train(cfg: DictConfig) -> None:
    """Entry point for training via Hydra configs."""
    env = MicrostructureEnv(**cfg.env)
    eval_env = MicrostructureEnv(**cfg.env)

    if cfg.algo == "sac":
        model = SAC(cfg.policy, env, **cfg.sac)
    elif cfg.algo == "ppo":
        model = PPO(cfg.policy, env, **cfg.ppo)
    else:  # pragma: no cover - defensive
        raise ValueError(f"Unknown algorithm: {cfg.algo}")

    callback = SharpeEarlyStopCallback(eval_env, cfg.eval_freq, cfg.patience)
    model.learn(total_timesteps=cfg.total_timesteps, callback=callback)
    model.save("model.zip")

    env.close()
    eval_env.close()


if __name__ == "__main__":  # pragma: no cover - script entry point
    train()
