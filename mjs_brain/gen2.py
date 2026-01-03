import subprocess
import os
import random
import csv
from concurrent.futures import ProcessPoolExecutor, as_completed

BASE_DIR = "/majinsang/majinsang_brain"
PLANNER_PATH = os.path.join(BASE_DIR, "metric-ff-linux/ff")
DOMAIN_FILE = os.path.join(BASE_DIR, "minecraft_domain.pddl")
OUTPUT_CSV = os.path.join(BASE_DIR, "minecraft_mlp_data_final.csv")

NUM_SAMPLES = 50000
NUM_CORES = 12

ACTION_MAP = {
    "chop-tree": 0, "craft-planks": 1, "craft-sticks": 2, "craft-pickaxe": 3,
    "find-tree": 4, "craft-crafting-table": 5, "place-crafting-table": 6,
    "move-to-crafting-table": 7, "wait": 8
}

def get_skewed_value(max_val, n=4):
    return int(max_val * (random.random() ** n))

def run_single_planning(task_id):
    temp_prob = os.path.join(BASE_DIR, f"temp_p_{task_id}.pddl")
    
    state = {
        'log': get_skewed_value(64),
        'planks': get_skewed_value(64),
        'sticks': get_skewed_value(64),
        'inv_table': 1 if random.random() < 0.1 else 0, 
        'near_tree': random.choice([True, False]),
        'placed_table': random.choice([True, False]) if random.random() < 0.3 else False,
        'at_table': False
    }
    
    if state['placed_table']:
        state['at_table'] = random.choice([True, False])
    if state['at_table']:
        state['placed_table'] = True

    pddl_content = f"""(define (problem p) 
  (:domain minecraft-brain-refined)
  (:init 
    (= (count-log) {state['log']}) 
    (= (count-planks) {state['planks']}) 
    (= (count-sticks) {state['sticks']})
    (= (count-crafting-table) {state['inv_table']})
    (= (total-cost) 0)
    {'(near-tree)' if state['near_tree'] else ''}
    {'(placed-crafting-table)' if state['placed_table'] else ''}
    {'(at-crafting-table)' if state['at_table'] else ''}
  )
  (:goal (has-pickaxe))
  (:metric minimize (total-cost))
)"""

    with open(temp_prob, "w") as f:
        f.write(pddl_content)

    try:
        result = subprocess.run(
            [PLANNER_PATH, "-o", DOMAIN_FILE, "-f", temp_prob], 
            capture_output=True, text=True, timeout=5
        )
        
        # 플랜 파싱
        for line in result.stdout.split('\n'):
            if "step" in line.lower() and "0:" in line:
                action_name = line.split(":", 1)[1].strip().lower()
                label = ACTION_MAP.get(action_name, 8)
                
                os.remove(temp_prob)
                
                return [
                    state['log'], state['planks'], state['sticks'], state['inv_table'],
                    1 if state['near_tree'] else 0, 
                    1 if state['placed_table'] else 0, 
                    1 if state['at_table'] else 0, 
                    label
                ]
    except Exception as e:
        print(f"Task {task_id} failed: {e}")
    
    try:
        os.remove(temp_prob)
    except:
        pass
    
    return None

if __name__ == "__main__":
    print(f"--- [균형 최적화] 12코어 데이터 수집 시작 (목표: {NUM_SAMPLES}) ---")
    final_data = []
    processed = 0

    with ProcessPoolExecutor(max_workers=NUM_CORES) as executor:
        futures = {executor.submit(run_single_planning, i): i for i in range(NUM_SAMPLES)}
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                final_data.append(result)
            
            processed += 1
            if processed % 1000 == 0:
                print(f"진행: {processed}/{NUM_SAMPLES} ({len(final_data)} 성공)")

    # CSV 저장
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(['log', 'planks', 'sticks', 'inv_table', 'near_tree', 'placed_table', 'at_table', 'action_label'])
        writer.writerows(final_data)

    print(f"\n--- 데이터 생성 완료: {len(final_data)}개 ---")
    print(f"저장 위치: {OUTPUT_CSV}")