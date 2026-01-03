import socket
import struct
import torch
import torch.nn as nn
import time
import os
import numpy as np

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

class GameState:
    def __init__(self):
        self.player_id = 0
        self.position = (0.0, 0.0, 0.0)
        
        self.log_count = 0
        self.planks_count = 0
        self.stick_count = 0
        self.crafting_table_inv = 0
        
        self.near_tree = False
        self.placed_table = False
        self.at_table = False
        
        self.has_player_info = False
        self.has_inventory = False
        self.has_nearby_info = False
    
    def update_player_info(self, player_id, x, y, z, yaw, pitch):
        self.player_id = player_id
        self.position = (x, y, z)
        self.has_player_info = True
    
    def update_inventory(self, player_id, log, planks, stick, pickaxe, crafting_table):
        self.log_count = log
        self.planks_count = planks
        self.stick_count = stick
        self.crafting_table_inv = crafting_table
        self.has_inventory = True
    
    def update_nearby_info(self, near_oak, oak_x, oak_y, oak_z, near_table, table_x, table_y, table_z):
        self.near_tree = bool(near_oak)
        self.placed_table = bool(near_table)
        self.at_table = self.placed_table and True
        self.has_nearby_info = True

    def get_model_raw_input(self):
        return [
            self.log_count, 
            self.planks_count, 
            self.stick_count, 
            self.crafting_table_inv,
            1 if self.near_tree else 0,
            1 if self.placed_table else 0,
            1 if self.at_table else 0
        ]

class AIAgent:
    def __init__(self, model_path="minecraft_agent_model.pth"):
        checkpoint = torch.load(model_path, weights_only=False)
        
        self.model = MinecraftMLP(input_size=7, num_classes=9)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()
        
        self.scaler = checkpoint['scaler']
        self.game_state = GameState()
        print(f"모델 및 Scaler 로드 완료")

    def predict_action(self):
        raw_input = np.array([self.game_state.get_model_raw_input()])
        
        scaled_input = self.scaler.transform(raw_input)
        input_tensor = torch.FloatTensor(scaled_input)
        
        with torch.no_grad():
            output = self.model(input_tensor)
            probs = torch.nn.functional.softmax(output, dim=1)
            predicted_idx = torch.argmax(probs).item()
            confidence = probs[0][predicted_idx].item() * 100
            
        return predicted_idx, confidence, output, probs

def run_server(ip="127.0.0.1", port=8888):
    print("MJS_Brain 로드중")
    
    try:
        ai_agent = AIAgent()
    except Exception as e:
        print(f"모델 로드 실패: {e}")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    
    last_prediction_time = 0

    while True:
        data, addr = sock.recvfrom(4096)
        packet_id = data[0]
        current_time = time.time()
        
        try:
            if packet_id == 0x01:
                p_id, x, y, z, yaw, pitch = struct.unpack('<Iddddd', data[1:45])
                ai_agent.game_state.update_player_info(p_id, x, y, z, yaw, pitch)
            elif packet_id == 0x02:
                p_id, l, p, s, pk, ct = struct.unpack('<IIIIII', data[1:25])
                ai_agent.game_state.update_inventory(p_id, l, p, s, pk, ct)
            elif packet_id == 0x03:
                p_id, n_o, ox, oy, oz, n_t, tx, ty, tz = struct.unpack('<IBdddBddd', data[1:55])
                ai_agent.game_state.update_nearby_info(n_o, ox, oy, oz, n_t, tx, ty, tz)

                if ai_agent.game_state.has_inventory and (current_time - last_prediction_time >= 3.0):
                    idx, conf, out, probs = ai_agent.predict_action()
                    
                    print(f"\n다음 행동: {ACTION_MAP[idx]} (확신도: {conf:.2f}%)")
                    print(f"    인벤토리: 원목={ai_agent.game_state.log_count}, 판자={ai_agent.game_state.planks_count}, 막대기={ai_agent.game_state.stick_count}, 작업대={ai_agent.game_state.crafting_table_inv}")
                    print(f"    주변정보: 나무근처={'✅' if ai_agent.game_state.near_tree else '❌'}, 작업대설치={'✅' if ai_agent.game_state.placed_table else '❌'}, 작업대근처={'✅' if ai_agent.game_state.at_table else '❌'}")
                    
                    response = struct.pack('<BI', 0x10, idx)
                    sock.sendto(response, addr)
                    last_prediction_time = current_time

        except Exception as e:
            print(f"패킷 처리 오류: {e}")

if __name__ == "__main__":
    run_server()