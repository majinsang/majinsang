import subprocess
import os

BASE_DIR = "/majinsang/majinsang_brain"
# Metric-FF 사용
FF_PATH = os.path.join(BASE_DIR, "metric-ff-linux/ff")  # 현재 디렉토리의 metric-ff-linux 사용
DOMAIN_FILE = os.path.join(BASE_DIR, "minecraft_domain.pddl")
TEMP_PROB = os.path.join(BASE_DIR, "debug_prob.pddl")

print("=" * 50)
print("Minecraft PDDL 플래너 테스트")
print("=" * 50)

# 입력 형식 안내
print("\n[입력 형식]")
print("공백으로 구분된 9개의 값을 한 줄에 입력하세요:")
print("통나무 판자 막대기 작업대 나무근처 작업대설치 작업대앞 곡괭이보유 목표곡괭이")
print("- 숫자: 개수 (통나무, 판자, 막대기, 작업대)")
print("- 0/1: 불린 값 (나무근처, 작업대설치, 작업대앞, 곡괭이보유, 목표곡괭이)")
print("\n예시:")
print("  1 0 0 1 1 0 0 0 1  → 통나무1, 판자0, 막대기0, 작업대1, 나무근처O, 목표곡괭이O")
print("  0 7 2 0 0 0 0 0 1  → 통나무0, 판자7, 막대기2, 작업대0, 목표곡괭이O")
print("  2 0 0 0 1 0 0 0 1  → 통나무2, 판자0, 막대기0, 작업대0, 나무근처O, 목표곡괭이O")
print()

# 사용자로부터 한 줄로 입력 받기
input_line = input("입력: ").strip()
values = input_line.split()

if len(values) != 9:
    print(f"오류: 9개의 값이 필요합니다. (입력된 개수: {len(values)})")
    exit(1)

try:
    count_log = int(values[0])
    count_planks = int(values[1])
    count_sticks = int(values[2])
    count_crafting_table = int(values[3])
    near_tree = bool(int(values[4]))
    placed_crafting_table = bool(int(values[5]))
    at_crafting_table = bool(int(values[6]))
    has_pickaxe = bool(int(values[7]))
    goal_has_pickaxe = bool(int(values[8]))
except ValueError as e:
    print(f"오류: 입력 형식이 잘못되었습니다. {e}")
    exit(1)

print("\n[입력된 값]")
print(f"통나무: {count_log}, 판자: {count_planks}, 막대기: {count_sticks}, 작업대: {count_crafting_table}")
print(f"나무근처: {near_tree}, 작업대설치: {placed_crafting_table}, 작업대앞: {at_crafting_table}")
print(f"곡괭이보유: {has_pickaxe}, 목표곡괭이: {goal_has_pickaxe}")

# PDDL 문제 파일 생성
init_predicates = []
if near_tree:
    init_predicates.append("(near-tree)")
if placed_crafting_table:
    init_predicates.append("(placed-crafting-table)")
if at_crafting_table:
    init_predicates.append("(at-crafting-table)")
if has_pickaxe:
    init_predicates.append("(has-pickaxe)")

pddl_content = f"""(define (problem p) 
  (:domain minecraft-brain-refined)
  (:init 
    (= (count-log) {count_log}) 
    (= (count-planks) {count_planks}) 
    (= (count-sticks) {count_sticks})
    (= (count-crafting-table) {count_crafting_table})
    (= (total-cost) 0)
    {' '.join(init_predicates)}
  )
  (:goal (has-pickaxe))
  (:metric minimize (total-cost))
)"""

with open(TEMP_PROB, "w") as f:
    f.write(pddl_content)

print("\n" + "=" * 50)
print("생성된 PDDL 문제:")
print("=" * 50)
print(pddl_content)

print("\n" + "=" * 50)
print("Metric-FF 플래너 실행 중...")
print("=" * 50)

# 간단한 자원 계산 체크
print("\n[자원 분석]")
total_planks_available = count_log * 4 + count_planks
sticks_available = count_sticks
print(f"통나무 {count_log}개 → 판자 최대 {count_log * 4}개 생성 가능")
print(f"현재 판자: {count_planks}개")
print(f"총 사용 가능한 판자: {total_planks_available}개")
print(f"현재 막대기: {sticks_available}개")

# 막대기가 부족하면 판자로 만들어야 함
sticks_needed = max(0, 2 - sticks_available)
planks_for_sticks = 0
if sticks_needed > 0:
    planks_for_sticks = 2  # 판자 2개 → 막대기 4개
    print(f"막대기 부족 → 판자 {planks_for_sticks}개로 막대기 4개 제작 필요")

planks_remaining = total_planks_available - planks_for_sticks
print(f"\n곡괭이 제작에 필요: 판자 3개, 막대기 2개")
print(f"제작 후 남은 판자: {planks_remaining}개")

if planks_remaining >= 3 and (sticks_available >= 2 or planks_for_sticks > 0):
    print("✓ 자원 충분: 플랜을 찾을 수 있을 것으로 예상됩니다.")
else:
    print("✗ 자원 부족: 이 상태에서는 곡괭이를 만들 수 없을 수 있습니다!")
    if planks_remaining < 3:
        print(f"  - 판자가 {3 - planks_remaining}개 부족합니다.")
        print(f"  - 통나무 {((3 - planks_remaining + 3) // 4)}개를 더 구하거나, 판자를 더 가져야 합니다.")

print("\n" + "=" * 50)

try:
    # Metric-FF 사용
    result = subprocess.run([
        FF_PATH, 
        "-o", DOMAIN_FILE,
        "-f", TEMP_PROB
    ], capture_output=True, text=True, timeout=30)
    
    stdout_text = result.stdout.strip()
    stderr_text = result.stderr.strip()
    
    print("\n[실행 결과 - STDOUT]")
    if stdout_text:
        print(result.stdout)
    else:
        print("(출력 없음)")
    
    if stderr_text:
        print("\n[실행 결과 - STDERR]")
        print(result.stderr)
    
    print("\n" + "=" * 50)
    
    # Metric-FF 플랜 파싱
    if "found legal plan" in stdout_text.lower():
        print("✓ 성공: 플랜이 발견되었습니다!")
        
        # 플랜 추출
        lines = stdout_text.split('\n')
        plan_started = False
        plan_steps = []
        
        for line in lines:
            if "found legal plan" in line.lower():
                plan_started = True
                continue
            if plan_started:
                if line.strip().startswith("step"):
                    # "step    0: CHOP-TREE" 형식 파싱
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        action = parts[1].strip()
                        plan_steps.append(action)
                elif line.strip().startswith("plan cost"):
                    break
        
        if plan_steps:
            print("\n[발견된 플랜]")
            for i, action in enumerate(plan_steps):
                print(f"  {i}: {action}")
            print(f"\n총 {len(plan_steps)}개의 액션")
            
    elif "goal can be simplified to false" in stdout_text.lower() or "unsolvable" in stdout_text.lower():
        print("✗ 불가능: 이 문제는 해결할 수 없습니다 (unsolvable).")
    else:
        print("✗ 실패: 플랜을 찾지 못했습니다.")
    
    print("=" * 50)

except subprocess.TimeoutExpired:
    print("\n✗ 타임아웃: 플래너 실행 시간 초과 (30초)")
except Exception as e:
    print(f"\n✗ 시스템 에러: {e}")