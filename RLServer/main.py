from stable_baselines3 import SAC
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from MinecraftEnv import MinecraftEnv

def make_env():
    env = MinecraftEnv((10.0, -60.0, 10.0))
    env = Monitor(env)
    return env

if __name__ == "__main__":
    env = DummyVecEnv([make_env])

    model = SAC.load(
        "models/sac/best/best_model",
        env=env,
        device="auto"
    )

    print("✅ SAC Model loaded, inference start")

    obs = env.reset()

    while True:
        action, _ = model.predict(obs, deterministic=True)

        obs, reward, done, info = env.step(action)
        env.render()

        if done:
            obs = env.reset()