import torch
import torch.nn as nn
import numpy as np
from common import *
from NetworkManager import NetworkManager

class MinecraftMLP(nn.Module):
    def __init__(self, input_size, num_classes):
        super(MinecraftMLP, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, num_classes)
        )
        
    def forward(self, x):
        return self.network(x)

ACTION_MAP = {
    0: "나무 캐기 (CHOP-TREE)",
    1: "판자 만들기 (CRAFT-PLANKS)",
    2: "막대기 만들기 (CRAFT-STICKS)",
    3: "곡괭이 제작 (CRAFT-PICKAXE)",
    4: "나무 찾아가기 (FIND-TREE)",
    5: "작업대 제작 (CRAFT-CRAFTING-TABLE)",
    6: "작업대 설치 (PLACE-CRAFTING-TABLE)",
    7: "작업대로 이동 (MOVE-TO-CRAFTING-TABLE)",
    8: "대기 (WAIT)"
}

class Brain:
    def __init__(self, model_path="minecraft_agent_model.pth"):
        
        # AI 모델 로드
        checkpoint = torch.load(model_path, weights_only=False)
        self.model_ = MinecraftMLP(input_size=7, num_classes=9)
        self.model_.load_state_dict(checkpoint['model_state_dict'])
        self.model_.eval()
        self.scaler_ = checkpoint['scaler']
        
        # 상태 저장
        self.inventory_ = None
        self.nearby_ = None
        
        print(f"Brain 초기화 완료")
        print(f"모델 로드 완료: {model_path}")
    
    def UpdateState(self, inventory: PlayerInventory, nearby: PlayerNearby):
        """외부에서 받은 상태로 업데이트"""
        self.inventory_ = inventory
        self.nearby_ = nearby
    
    def IsReady(self) -> bool:
        """추론 준비 상태 확인"""
        return self.inventory_ is not None
    
    def GetModelInput(self) -> list:
        """모델 입력 데이터 생성"""
        if not self.IsReady():
            return None
        
        return [
            self.inventory_.log_,
            self.inventory_.planks_,
            self.inventory_.stick_,
            self.inventory_.crafting_table_,
            1 if (self.nearby_ and self.nearby_.near_tree_) else 0,
            1 if (self.nearby_ and self.nearby_.near_table_) else 0,
            1 if (self.nearby_ and self.nearby_.near_table_) else 0
        ]
    
    def PredictAction(self) -> dict:
        """다음 행동 추론"""
        model_input = self.GetModelInput()
        if model_input is None:
            return None
        
        # 입력 전처리
        raw_input = np.array([model_input])
        scaled_input = self.scaler_.transform(raw_input)
        input_tensor = torch.FloatTensor(scaled_input)
        
        # 추론
        with torch.no_grad():
            output = self.model_(input_tensor)
            probs = torch.nn.functional.softmax(output, dim=1)
            predicted_idx = torch.argmax(probs).item()
            confidence = probs[0][predicted_idx].item() * 100
        
        return {
            'action_id': predicted_idx,
            'action_name': ACTION_MAP.get(predicted_idx, "UNKNOWN"),
            'confidence': confidence,
            'current_state': {
                'log': model_input[0],
                'planks': model_input[1],
                'stick': model_input[2],
                'crafting_table': model_input[3],
                'near_tree': bool(model_input[4]),
                'near_crafting_table': bool(model_input[5])
            }
        }
    
    
    def GetDebugInfo(self) -> dict:
        """디버그 정보 조회"""
        return {
            'inventory': {
                'log': self.inventory_.log_ if self.inventory_ else 0,
                'planks': self.inventory_.planks_ if self.inventory_ else 0,
                'stick': self.inventory_.stick_ if self.inventory_ else 0,
                'pickaxe': self.inventory_.pickaxe_ if self.inventory_ else 0,
                'crafting_table': self.inventory_.crafting_table_ if self.inventory_ else 0
            } if self.inventory_ else None,
            'nearby': {
                'near_tree': self.nearby_.near_tree_ if self.nearby_ else False,
                'tree_pos': (self.nearby_.tree_pos_.x_, 
                           self.nearby_.tree_pos_.y_, 
                           self.nearby_.tree_pos_.z_) if self.nearby_ else None,
                'near_table': self.nearby_.near_table_ if self.nearby_ else False,
                'table_pos': (self.nearby_.table_pos_.x_, 
                            self.nearby_.table_pos_.y_, 
                            self.nearby_.table_pos_.z_) if self.nearby_ else None
            } if self.nearby_ else None
        }
        
    

def main():
    """Brain 테스트 메인"""
    networkManager = NetworkManager('localhost')
    networkManager.UdpServerOpen(8986)
    networkManager.TcpServerOpen('localhost', 8888)
    networkManager.AcceptConnection()
    
    brain = Brain()
    
    print("\nBrain AI 서버 시작...")
    print("=" * 60)
    
    try:
        while True:
            # NetworkManager에서 상태 수신
            inventory = networkManager.GetPlayerInventory()
            nearby = networkManager.GetPlayerNearby()
            
            # Brain에 상태 전달
            brain.UpdateState(inventory, nearby)
            
            # 추론 준비 확인
            if not brain.IsReady():
                print("대기 중... (인벤토리 정보 수신 대기)")
                continue
            
            # 행동 추론
            action = brain.PredictAction()
            if action:
                print(f"\n[추론 결과]")
                print(f"  행동: {action['action_name']}")
                print(f"  확신도: {action['confidence']:.1f}%")
                print(f"  상태: {action['current_state']}")
            
            # 디버그 정보
            debug = brain.GetDebugInfo()
            print(f"\n[현재 상태]")
            print(f"  인벤토리: {debug['inventory']}")
            print(f"  주변: Tree={debug['nearby']['near_tree']}, Table={debug['nearby']['near_table']}")
            print("-" * 60)
            
            import time
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nBrain AI 서버 종료...")
        networkManager.Close()

if __name__ == "__main__":
    main()
