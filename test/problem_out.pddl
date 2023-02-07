(define (problem instance_4-problem)
 (:domain instance_4-domain)
 (:objects
   c0 c1 c2 c3 - counter
 )
 (:init (= (max_int) 10) (= (value c0) 0) (= (value c1) 0) (= (value c2) 0) (= (value c3) 0))
 (:goal (and (and (<= (+ 1 (value c0)) (value c1)) (<= (+ 1 (value c1)) (value c2)) (<= (+ 1 (value c2)) (value c3)))))
 (:metric minimize (total-cost))
)
