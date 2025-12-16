import csv
import random

def get_expert_action(log, planks, stick, has_pickaxe, near_tree, has_crafting_table):
    if has_pickaxe: return 0
    
    if not has_crafting_table:
        if planks >= 7 and stick >= 2: return 6
        elif planks >= 4: return 6
    
    if has_crafting_table and planks >= 3 and stick >= 2: return 4
    
    if not near_tree and (log < 1 and planks < 2): return 5
    
    if stick < 2:
        if planks >= 2: return 3
        elif log >= 1: return 2
        elif near_tree: return 1
        else: return 0
        
    if planks < 3:
        if log >= 1: return 2
        elif near_tree: return 1
        else: return 0

    return 0

# ==========================================
# [실행] 데이터 생성
# ==========================================
def create_csv(filename="dataset.csv", total_samples=2000000):
    print(f"데이터 생성 시작... (총 {total_samples}개)")
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['log', 'planks', 'stick', 'has_pickaxe', 'near_tree', 'has_crafting_table', 'action_label'])
        
        edge_count = int(total_samples * 0.3)
        for _ in range(edge_count):
            log = 0
            planks = random.choice([1, 2, 3, 4]) 
            stick = 0
            has_pickaxe = 0
            near_tree = 1
            has_crafting_table = 0
            
            label = get_expert_action(log, planks, stick, has_pickaxe, near_tree, has_crafting_table)
            writer.writerow([log, planks, stick, has_pickaxe, near_tree, has_crafting_table, label])

        for _ in range(total_samples - edge_count):
            log = random.randint(0, 5)
            planks = random.randint(0, 10)
            stick = random.randint(0, 5)
            has_pickaxe = 1 if random.random() < 0.1 else 0
            near_tree = 1 if random.random() < 0.8 else 0
            has_crafting_table = 1 if random.random() < 0.3 else 0
            
            label = get_expert_action(log, planks, stick, has_pickaxe, near_tree, has_crafting_table)
            writer.writerow([log, planks, stick, has_pickaxe, near_tree, has_crafting_table, label])
            
    print(f"완료! '{filename}' 파일이 생성되었습니다.")

if __name__ == "__main__":
    create_csv()