(define (domain blocksworld_test_problem_problem_problem_problem_problem_problem_problem_problem_problem_problem-domain)
 (:predicates (clear ?x - object) (on_table ?x - object) (arm_empty) (holding ?x - object) (on ?x - object ?y - object))
 (:action pickup
  :parameters ( ?ob - object)
  :precondition (and (clear ?ob) (on_table ?ob) (arm_empty))
  :effect (and (holding ?ob) (not (clear ?ob)) (not (on_table ?ob)) (not (arm_empty))))
 (:action putdown
  :parameters ( ?ob - object)
  :precondition (and (holding ?ob))
  :effect (and (clear ?ob) (arm_empty) (on_table ?ob) (not (holding ?ob))))
 (:action stack
  :parameters ( ?ob - object ?underob - object)
  :precondition (and (clear ?underob) (holding ?ob))
  :effect (and (arm_empty) (clear ?ob) (on ?ob ?underob) (not (clear ?underob)) (not (holding ?ob))))
 (:action unstack
  :parameters ( ?ob - object ?underob - object)
  :precondition (and (on ?ob ?underob) (clear ?ob) (arm_empty))
  :effect (and (holding ?ob) (clear ?underob) (not (on ?ob ?underob)) (not (clear ?ob)) (not (arm_empty))))
)
