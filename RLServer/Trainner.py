from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor

from MinecraftEnv import MinecraftEnv


def make_env():
    env = MinecraftEnv()
    env = Monitor(env)
    return env


if __name__ == "__main__":
    env = DummyVecEnv([make_env])

    model = PPO(
        policy="MlpPolicy",
        env=env,
        learning_rate=3e-4,
        n_steps=1024,
        batch_size=256,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,
        verbose=1,
        device="auto"
    )

    print("🚀 Training start")
    model.learn(total_timesteps=200_000)

    model.save("minecraft_dxdy_dz_ppo")
    print("✅ Model saved")
