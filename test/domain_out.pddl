(define (domain instance_4-domain)
 (:requirements :strips :typing :numeric-fluents :action-costs)
 (:types counter)
 (:functions (value ?c - counter) (max_int) (total-cost))
 (:action increment
  :parameters ( ?c - counter)
  :precondition (and (<= (+ 1 (value ?c)) (max_int)))
  :effect (and (increase (value ?c) 1) (increase (total-cost) 1)))
 (:action decrement
  :parameters ( ?c - counter)
  :precondition (and (<= 1 (value ?c)))
  :effect (and (decrease (value ?c) 1) (increase (total-cost) 1)))
)
