(define (domain minecraft-brain-refined)
  (:requirements :strips :typing :fluents :negative-preconditions)

  (:functions 
    (count-log) (count-planks) (count-sticks)
    (count-crafting-table)   ;; 인벤토리에 보유 중인 작업대 개수
    (total-cost)             ;; 총 비용 (액션 수)
  )

  (:predicates
    (near-tree)
    (placed-crafting-table)  ;; 맵에 작업대가 설치되어 있는지 여부
    (at-crafting-table)      ;; 에이전트가 설치된 작업대 바로 옆에 있는지 여부
    (has-pickaxe)
  )

  ;; 1. 작업대 만들기 (인벤토리에 추가)
  (:action craft-crafting-table
    :parameters ()
    :precondition (and (>= (count-planks) 4) (< (count-crafting-table) 5) (not (placed-crafting-table)))
    :effect (and (decrease (count-planks) 4) (increase (count-crafting-table) 1) (increase (total-cost) 1))
  )

  ;; 2. 작업대 설치하기 (인벤토리 -> 맵)
  (:action place-crafting-table
    :parameters ()
    :precondition (>= (count-crafting-table) 1)
    :effect (and (decrease (count-crafting-table) 1) (placed-crafting-table) (at-crafting-table) (not (near-tree)) (increase (total-cost) 1))
  )

  ;; 3. 설치된 작업대로 이동하기
  (:action move-to-crafting-table
    :parameters ()
    :precondition (and (placed-crafting-table) (not (at-crafting-table)))
    :effect (and (at-crafting-table) (not (near-tree)) (increase (total-cost) 1))
  )

  ;; 4. 곡괭이 제작 (이제 반드시 작업대 옆(at)에 있어야 함)
  (:action craft-pickaxe
    :parameters ()
    :precondition (and (at-crafting-table) (>= (count-planks) 3) (>= (count-sticks) 2))
    :effect (and (decrease (count-planks) 3) (decrease (count-sticks) 2) (has-pickaxe) (increase (total-cost) 1))
  )

  ;; 기존 액션들 (나무 관련)
  (:action find-tree
    :parameters ()
    :precondition (not (near-tree))
    :effect (and (near-tree) (not (at-crafting-table)) (increase (total-cost) 1))
  )

  (:action chop-tree
    :parameters ()
    :precondition (and (near-tree) (< (count-log) 10))
    :effect (and (increase (count-log) 1) (increase (total-cost) 1))
  )

  (:action craft-planks
    :parameters ()
    :precondition (>= (count-log) 1)
    :effect (and (decrease (count-log) 1) (increase (count-planks) 4) (increase (total-cost) 1))
  )

  (:action craft-sticks
    :parameters ()
    :precondition (and (>= (count-planks) 2) (< (count-sticks) 10))
    :effect (and (decrease (count-planks) 2) (increase (count-sticks) 4) (increase (total-cost) 1))
  )
)