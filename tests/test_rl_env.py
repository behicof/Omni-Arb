from rl.env import MicrostructureEnv


def test_env_step_shapes():
    env = MicrostructureEnv()
    obs, info = env.reset()
    assert obs.shape == env.observation_space.shape

    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    assert obs.shape == env.observation_space.shape
    assert isinstance(reward, float)
    assert isinstance(terminated, bool)
    assert isinstance(truncated, bool)
    env.close()
