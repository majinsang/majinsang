import csv
import random

# ==========================================
# [설정] 선생님의 지식 (정확한 규칙)
# ==========================================
def get_expert_action(log, planks, stick, has_pickaxe, near_tree):
    # 0:대기, 1:나무캐기, 2:판자제작, 3:막대기제작, 4:곡괭이제작
    
    # 이미 목표 달성
    if has_pickaxe: return 0
    
    # 곡괭이 제작 가능? (판자3, 막대기2)
    if planks >= 3 and stick >= 2: return 4 
    
    # 막대기가 부족한 상황
    if stick < 2:
        if planks >= 2: return 3      # 판자가 2개 이상이면 막대기 제작 (중요!)
        elif log >= 1: return 2       # 판자 없으면 원목으로 판자 제작
        elif near_tree: return 1      # 나무 캐기
        else: return 0
        
    # 막대기는 있는데 판자가 부족한 상황
    if planks < 3:
        if log >= 1: return 2         # 판자 제작
        elif near_tree: return 1      # 나무 캐기
        else: return 0

    return 0

# ==========================================
# [실행] 데이터 생성
# ==========================================
def create_csv(filename="dataset.csv", total_samples=2000000):
    print(f"데이터 생성 시작... (총 {total_samples}개)")
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['log', 'planks', 'stick', 'has_pickaxe', 'near_tree', 'action_label'])
        
        # 1. [집중 교육] 엣지 케이스 (전체의 30% 할당)
        # AI가 헷갈려하는 '판자 0~1개 vs 2개' 상황을 집중적으로 넣음
        edge_count = int(total_samples * 0.3)
        for _ in range(edge_count):
            log = 0
            # 판자가 1개거나 2개인 상황을 반반 확률로 강제 주입
            planks = random.choice([1, 2]) 
            stick = 0
            has_pickaxe = 0
            near_tree = 1 # 나무는 앞에 있음
            
            label = get_expert_action(log, planks, stick, has_pickaxe, near_tree)
            writer.writerow([log, planks, stick, has_pickaxe, near_tree, label])

        # 2. [일반 교육] 랜덤 상황 (나머지 70%)
        for _ in range(total_samples - edge_count):
            log = random.randint(0, 5)
            planks = random.randint(0, 10)
            stick = random.randint(0, 5)
            has_pickaxe = 1 if random.random() < 0.1 else 0
            near_tree = 1 if random.random() < 0.8 else 0
            
            label = get_expert_action(log, planks, stick, has_pickaxe, near_tree)
            writer.writerow([log, planks, stick, has_pickaxe, near_tree, label])
            
    print(f"완료! '{filename}' 파일이 생성되었습니다.")

if __name__ == "__main__":
    create_csv()