from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback

from MinecraftEnv import MinecraftEnv


def make_env():
    env = MinecraftEnv((10.0, -60.0, 10.0))
    env = Monitor(env)
    return env


if __name__ == "__main__":
    # 환경 생성
    env = DummyVecEnv([make_env])

    # PPO 모델 생성
    model = PPO(
        policy="MlpPolicy",
        env=env,
        learning_rate=3e-4,
        n_steps=2048,  # 더 많은 step 수집 (마인크래프트는 느림)
        batch_size=64,  # 더 작은 batch (안정성)
        n_epochs=10,  # epoch 수 명시
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,  # exploration 장려
        verbose=1,
        tensorboard_log="./ppo_minecraft_tensorboard/",  # 텐서보드 로그
        device="auto"
    )

    # Callback 설정
    checkpoint_callback = CheckpointCallback(
        save_freq=10000,  # 10k step마다 저장
        save_path="./models/",
        name_prefix="minecraft_ppo"
    )

    print("🚀 Training start")
    print(f"Total timesteps: 100,000")
    print(f"Target position: (10.0, -60.0, 10.0)")
    
    # 학습 시작
    model.learn(
        total_timesteps=100_000,  # 100 → 100,000으로 수정!
        callback=checkpoint_callback,
        progress_bar=True  # 진행 바 표시
    )

    # 모델 저장
    model.save("minecraft_navigation_ppo_final")
    print("✅ Model saved: minecraft_navigation_ppo_final.zip")

    # 학습된 모델 테스트
    print("\n🎮 Testing trained model...")
    obs = env.reset()
    for i in range(100):
        action, _states = model.predict(obs, deterministic=True)
        obs, rewards, dones, info = env.step(action)
        if dones[0]:
            print(f"✅ Goal reached in {i+1} steps!")
            break
    
    env.close()