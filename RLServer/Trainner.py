"""
Minecraft Navigation - RL Algorithm Comparison
연속 행동 공간(Continuous Action Space)에 적합한 알고리즘 비교
"""

from stable_baselines3 import PPO, SAC, TD3, A2C
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.noise import NormalActionNoise, OrnsteinUhlenbeckActionNoise
import numpy as np

from MinecraftEnv import MinecraftEnv


def make_env():
    env = MinecraftEnv((10.0, -60.0, 10.0))
    env = Monitor(env)
    return env


# ============================================================================
# 1. SAC (Soft Actor-Critic) - 🏆 추천 1순위
# ============================================================================
# 장점:
# - Off-policy (샘플 효율성 최고)
# - 자동 온도 조절 (exploration/exploitation 균형)
# - 연속 행동 공간에서 SOTA 성능
# - 안정적이고 robust
# 
# 단점:
# - 메모리 사용량 많음 (replay buffer)
# - 학습 초반 느림
# ============================================================================

def train_sac():
    print("=" * 60)
    print("🔥 SAC (Soft Actor-Critic) Training")
    print("=" * 60)
    
    env = DummyVecEnv([make_env])
    
    model = SAC(
        policy="MlpPolicy",
        env=env,
        learning_rate=3e-4,
        buffer_size=100_000,  # Replay buffer 크기
        learning_starts=1000,  # 이만큼 모은 후 학습 시작
        batch_size=256,  # 큰 배치 (샘플 효율성)
        tau=0.005,  # Target network soft update
        gamma=0.99,
        train_freq=1,  # 매 step마다 학습
        gradient_steps=1,
        ent_coef='auto',  # 자동 entropy 조절 (중요!)
        target_update_interval=1,
        target_entropy='auto',
        verbose=1,
        tensorboard_log="./sac_minecraft_tensorboard/",
        device="auto"
    )
    
    checkpoint_callback = CheckpointCallback(
        save_freq=10000,
        save_path="./models/sac/",
        name_prefix="minecraft_sac"
    )
    
    eval_callback = EvalCallback(
        env,
        best_model_save_path="./models/sac/best/",
        log_path="./logs/sac/",
        eval_freq=5000,
        n_eval_episodes=5,
        deterministic=True
    )
    
    print("🚀 SAC Training - 샘플 효율성이 최고!")
    model.learn(
        total_timesteps=200_000,  # SAC는 더 적은 step으로도 학습 가능
        callback=[checkpoint_callback, eval_callback],
        progress_bar=True
    )
    
    model.save("minecraft_sac_final")
    print("✅ SAC Model saved")
    
    env.close()
    return model


# ============================================================================
# 2. TD3 (Twin Delayed DDPG) - 🏆 추천 2순위
# ============================================================================
# 장점:
# - Off-policy (샘플 효율성 좋음)
# - SAC보다 단순하고 빠름
# - 과추정(overestimation) 문제 해결
# - 안정적
#
# 단점:
# - SAC보다 탐험 능력 약간 떨어짐
# - Noise 파라미터 튜닝 필요
# ============================================================================

def train_td3():
    print("=" * 60)
    print("⚡ TD3 (Twin Delayed DDPG) Training")
    print("=" * 60)
    
    env = DummyVecEnv([make_env])
    
    # Action noise 설정 (exploration을 위해)
    n_actions = env.action_space.shape[-1]
    action_noise = NormalActionNoise(
        mean=np.zeros(n_actions),
        sigma=0.1 * np.ones(n_actions)
    )
    
    model = TD3(
        policy="MlpPolicy",
        env=env,
        learning_rate=3e-4,
        buffer_size=100_000,
        learning_starts=1000,
        batch_size=256,
        tau=0.005,
        gamma=0.99,
        train_freq=(1, "step"),
        gradient_steps=1,
        action_noise=action_noise,  # Exploration noise
        policy_delay=2,  # Policy는 2번에 1번 업데이트
        target_policy_noise=0.2,  # Target policy smoothing
        target_noise_clip=0.5,
        verbose=1,
        tensorboard_log="./td3_minecraft_tensorboard/",
        device="auto"
    )
    
    checkpoint_callback = CheckpointCallback(
        save_freq=10000,
        save_path="./models/td3/",
        name_prefix="minecraft_td3"
    )
    
    eval_callback = EvalCallback(
        env,
        best_model_save_path="./models/td3/best/",
        log_path="./logs/td3/",
        eval_freq=5000,
        n_eval_episodes=5,
        deterministic=True
    )
    
    print("🚀 TD3 Training - 빠르고 안정적!")
    model.learn(
        total_timesteps=200_000,
        callback=[checkpoint_callback, eval_callback],
        progress_bar=True
    )
    
    model.save("minecraft_td3_final")
    print("✅ TD3 Model saved")
    
    env.close()
    return model


# ============================================================================
# 3. PPO (Proximal Policy Optimization) - 현재 사용 중
# ============================================================================
# 장점:
# - 가장 안정적
# - 튜닝하기 쉬움
# - On-policy (현재 정책으로만 학습)
#
# 단점:
# - 샘플 효율성 낮음 (더 많은 timestep 필요)
# - Off-policy보다 느림
# ============================================================================

def train_ppo():
    print("=" * 60)
    print("🛡️ PPO (Proximal Policy Optimization) Training")
    print("=" * 60)
    
    env = DummyVecEnv([make_env])
    
    model = PPO(
        policy="MlpPolicy",
        env=env,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,
        vf_coef=0.5,
        max_grad_norm=0.5,
        verbose=1,
        tensorboard_log="./ppo_minecraft_tensorboard/",
        device="auto"
    )
    
    checkpoint_callback = CheckpointCallback(
        save_freq=10000,
        save_path="./models/ppo/",
        name_prefix="minecraft_ppo"
    )
    
    eval_callback = EvalCallback(
        env,
        best_model_save_path="./models/ppo/best/",
        log_path="./logs/ppo/",
        eval_freq=5000,
        n_eval_episodes=5,
        deterministic=True
    )
    
    print("🚀 PPO Training - 안정적이지만 느림")
    model.learn(
        total_timesteps=500_000,  # PPO는 더 많이 필요
        callback=[checkpoint_callback, eval_callback],
        progress_bar=True
    )
    
    model.save("minecraft_ppo_final")
    print("✅ PPO Model saved")
    
    env.close()
    return model


# ============================================================================
# 성능 비교 표
# ============================================================================
"""
┌──────────────┬────────────┬──────────────┬────────────┬──────────────┐
│ Algorithm    │ 샘플 효율성 │ 학습 속도     │ 안정성     │ 추천도       │
├──────────────┼────────────┼──────────────┼────────────┼──────────────┤
│ SAC          │ ⭐⭐⭐⭐⭐ │ ⭐⭐⭐⭐     │ ⭐⭐⭐⭐   │ 🏆🏆🏆      │
│ TD3          │ ⭐⭐⭐⭐   │ ⭐⭐⭐⭐⭐   │ ⭐⭐⭐⭐   │ 🏆🏆        │
│ PPO          │ ⭐⭐       │ ⭐⭐         │ ⭐⭐⭐⭐⭐ │ 🏆          │
│ A2C          │ ⭐         │ ⭐⭐⭐       │ ⭐⭐⭐     │              │
└──────────────┴────────────┴──────────────┴────────────┴──────────────┘

필요한 Timesteps 비교:
- SAC: 200,000 ~ 300,000
- TD3: 200,000 ~ 300,000
- PPO: 500,000 ~ 1,000,000
- A2C: 1,000,000+

메모리 사용량:
- SAC: 높음 (replay buffer 100k)
- TD3: 높음 (replay buffer 100k)
- PPO: 낮음 (on-policy)
- A2C: 낮음 (on-policy)
"""


# ============================================================================
# 추천 알고리즘 선택 가이드
# ============================================================================
"""
✅ SAC를 사용하세요 (if):
- 샘플 효율성이 중요 (환경 실행이 느림)
- 최고 성능 원함
- 메모리 여유 있음
- 연속 행동 공간

✅ TD3를 사용하세요 (if):
- SAC보다 빠른 학습 원함
- 메모리 절약하면서도 좋은 성능
- 간단한 구현

✅ PPO를 사용하세요 (if):
- 가장 안정적인 학습 원함
- 하이퍼파라미터 튜닝에 시간 못 씀
- 메모리 제약 있음

❌ A2C는 비추천:
- 샘플 효율성 너무 낮음
- 다른 알고리즘이 모두 더 나음
"""


# ============================================================================
# 테스트 함수
# ============================================================================

def test_model(model_path, algorithm_name):
    print(f"\n🎮 Testing {algorithm_name} model...")
    env = DummyVecEnv([make_env])
    
    # 알고리즘에 맞게 로드
    if algorithm_name == "SAC":
        model = SAC.load(model_path)
    elif algorithm_name == "TD3":
        model = TD3.load(model_path)
    elif algorithm_name == "PPO":
        model = PPO.load(model_path)
    
    success_count = 0
    total_rewards = []
    
    for episode in range(10):
        obs = env.reset()
        episode_reward = 0
        
        for step in range(1000):
            action, _states = model.predict(obs, deterministic=True)
            obs, rewards, dones, info = env.step(action)
            episode_reward += rewards[0]
            
            if dones[0]:
                success_count += 1
                print(f"✅ Episode {episode+1}: Success in {step+1} steps, reward: {episode_reward:.2f}")
                break
        else:
            print(f"❌ Episode {episode+1}: Failed, reward: {episode_reward:.2f}")
        
        total_rewards.append(episode_reward)
    
    print(f"\n📊 {algorithm_name} Results:")
    print(f"Success rate: {success_count}/10 ({success_count*10}%)")
    print(f"Average reward: {np.mean(total_rewards):.2f} ± {np.std(total_rewards):.2f}")
    
    env.close()

def main(algorithm):
    if algorithm == "sac":
        train_sac()
        test_model("minecraft_sac_final", "SAC")
    
    elif algorithm == "td3":
        train_td3()
        test_model("minecraft_td3_final", "TD3")
    
    elif algorithm == "ppo":
        train_ppo()
        test_model("minecraft_ppo_final", "PPO")
    
    elif algorithm == "all":
        print("🔬 Training all algorithms for comparison...\n")
        
        # 각 알고리즘 학습
        print("\n" + "="*60)
        train_sac()
        
        print("\n" + "="*60)
        train_td3()
        
        print("\n" + "="*60)
        train_ppo()
        
        # 비교 테스트
        print("\n" + "="*60)
        print("📊 FINAL COMPARISON")
        print("="*60)
        
        test_model("minecraft_sac_final", "SAC")
        test_model("minecraft_td3_final", "TD3")
        test_model("minecraft_ppo_final", "PPO")
    
    else:
        print(f"Unknown algorithm: {algorithm}")
        print("Available: sac, td3, ppo, all")


if __name__ == "__main__":
    import sys
    
    is_debug = True
    
    if is_debug:
        # Debug 모드일 때는 기본값으로 실행
        print("🐛 Debug Mode - Running with default algorithm: sac")
        algorithm = "sac"
        main(algorithm)
    else:
        # 일반 실행 모드
        if len(sys.argv) < 2:
            print("Usage: python train_comparison.py [sac|td3|ppo|all]")
            sys.exit(1)
        
        algorithm = sys.argv[1].lower()
        main(algorithm)