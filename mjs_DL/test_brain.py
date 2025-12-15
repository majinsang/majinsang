import torch
import torch.nn as nn

class MinecraftBrain(nn.Module):
    def __init__(self):
        super(MinecraftBrain, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(5, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 5) 
        )

    def forward(self, x):
        return self.network(x)

ACTION_MAP = {
    0: "대기 (IDLE)", 
    1: "나무 캐기 (MINE_LOG)", 
    2: "판자 만들기 (CRAFT_PLANKS)", 
    3: "막대기 만들기 (CRAFT_STICK)", 
    4: "곡괭이 만들기 (CRAFT_PICKAXE)"
}

def load_model():
    model = MinecraftBrain()
    try:
        model.load_state_dict(torch.load("minecraft_brain.pth", weights_only=True))
        model.eval()
        print("✅ 모델 로드 성공! (minecraft_brain.pth)")
        return model
    except FileNotFoundError:
        print("❌ 오류: 'minecraft_brain.pth' 파일이 없습니다. 학습(train_model.py)을 먼저 실행해주세요.")
        return None

def run_inference():
    model = load_model()
    if model is None: return

    print("\n=== 🧠 AI 에이전트 테스트 (종료하려면 'q' 입력) ===")
    
    while True:
        print("\n------------------------------------------------")
        print("현재 인벤토리와 상황을 입력해주세요.")
        
        try:
            input_str = input("입력 > [원목, 판자, 막대기, 곡괭이(0/1), 나무근처(0/1)] (예: 0 5 0 0 1) : ")
            
            if input_str.lower() == 'q':
                print("테스트를 종료합니다.")
                break
            
            inputs = list(map(float, input_str.split()))
            
            if len(inputs) != 5:
                print("⚠️ 경고: 5개의 숫자를 띄어쓰기로 구분해서 입력해주세요.")
                continue

            input_tensor = torch.FloatTensor([inputs])
            
            with torch.no_grad():
                output = model(input_tensor)
                predicted_idx = torch.argmax(output).item()
                probs = torch.nn.functional.softmax(output, dim=1)
                confidence = probs[0][predicted_idx].item() * 100

            action_name = ACTION_MAP[predicted_idx]
            print(f"\n🤖 AI의 판단: [ {action_name} ]")
            print(f"📊 확신도: {confidence:.2f}%")
            
            print(f"\n📋 각 행동별 상세 점수:")
            print(f"{'행동':<25} {'로짓(점수)':<12} {'확률':<10}")
            print("-" * 50)
            for idx in range(5):
                score = output[0][idx].item()
                prob = probs[0][idx].item() * 100
                marker = "👉 " if idx == predicted_idx else "   "
                print(f"{marker}{ACTION_MAP[idx]:<23} {score:>8.4f}    {prob:>6.2f}%")

        except ValueError:
            print("⚠️ 숫자만 입력해주세요.")
        except Exception as e:
            print(f"⚠️ 오류 발생: {e}")

if __name__ == "__main__":
    run_inference()