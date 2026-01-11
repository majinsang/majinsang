from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from MinecraftEnv import MinecraftEnv
from Brain import Brain

def make_env():
    env = MinecraftEnv((24.0, -60.0, -35.0))
    env = Monitor(env)
    return env

if __name__ == "__main__":
    env = DummyVecEnv([make_env])

    # RL 부분 임시 주석

    # model = PPO.load(
    #     "model/minecraft_dxdy_dz_ppo",
    #     env=env,
    #     device="auto"
    # )
    # print("✅ Model loaded, inference start")
    
    brain = Brain()
    networkManager = env.envs[0].unwrapped.networkManager_
    print("✅ Brain initialized")
    print("명령어: 'pred' 입력 시 추론 실행, 'q' 입력 시 종료\n")

    # obs = env.reset()

    while True:
        user_input = input(">>> ").strip().lower()
        
        if user_input == 'q':
            print("프로그램 종료")
            break
        elif user_input == 'pred':
            player_info, inventory, nearby = networkManager.GetPackets()
            
            print("\n" + "="*50)
            print("[패킷 정보]")
            if inventory:
                print(f"  [Player Information]")
                print(f"    - PlayerID: {player_info}")
                print(f"  [Inventory]")
                print(f"    - PlayerID: {inventory.playerId_}")
                print(f"    - Log: {inventory.log_}")
                print(f"    - Planks: {inventory.planks_}")
                print(f"    - Stick: {inventory.stick_}")
                print(f"    - Pickaxe: {inventory.pickaxe_}")
                print(f"    - Crafting Table: {inventory.crafting_table_}")
            else:
                print(f"  [Inventory] 수신 안됨")
                
            if nearby:
                print(f"\n  [Nearby]")
                print(f"    - PlayerID: {nearby.playerId_}")
                print(f"    - Near Tree: {nearby.near_tree_}")
                if nearby.near_tree_:
                    print(f"    - Tree Position: ({nearby.tree_pos_.x_:.1f}, {nearby.tree_pos_.y_:.1f}, {nearby.tree_pos_.z_:.1f})")
                print(f"    - Near Table: {nearby.near_table_}")
                if nearby.near_table_:
                    print(f"    - Table Position: ({nearby.table_pos_.x_:.1f}, {nearby.table_pos_.y_:.1f}, {nearby.table_pos_.z_:.1f})")
            else:
                print(f"  [Nearby] 수신 안됨")
            print("="*50)
            
            brain.UpdateState(inventory, nearby)
            
            if brain.IsReady():
                action = brain.PredictAction()
                if action:
                    print(f"\n[Brain 추론 결과]")
                    print(f"  행동: {action['action_name']}")
                    print(f"  확신도: {action['confidence']:.1f}%")
                    print(f"  현재 상태: {action['current_state']}\n")
            else:
                print("\n⚠ 데이터가 아직 준비되지 않았습니다.\n")
        
        # Movement

        # action, _ = model.predict(obs, deterministic=True)
        # obs, reward, done, info = env.step(action)
        # env.render()
        # if done:
        #     obs = env.reset()