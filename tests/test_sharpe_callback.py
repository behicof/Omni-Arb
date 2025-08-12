from rl.env import MicrostructureEnv
from rl.train import SharpeEarlyStopCallback
from stable_baselines3 import SAC


def test_sharpe_early_stops():
    env = MicrostructureEnv()
    eval_env = MicrostructureEnv()
    model = SAC(
        "MlpPolicy",
        env,
        learning_rate=1e-3,
        buffer_size=100,
        batch_size=32,
        train_freq=1,
        gradient_steps=1,
        ent_coef=0.0,
    )
    callback = SharpeEarlyStopCallback(eval_env, eval_freq=1, patience=0)
    model.learn(total_timesteps=5, callback=callback)
    assert callback.stop_training
    env.close()
    eval_env.close()
