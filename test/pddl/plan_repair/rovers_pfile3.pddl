(define (problem roverprob3726_problem_problem_problem_problem-problem)
 (:domain roverprob3726_problem_problem_problem_problem-domain)
 (:objects
   rover0 rover1 - rover
   waypoint0 waypoint1 waypoint2 waypoint3 - waypoint
   rover0store rover1store - store
   camera0 camera1 - camera
   colour high_res low_res - mode
   general - lander
   objective0 objective1 - objective
 )
 (:init (visible waypoint0 waypoint1) (visible waypoint1 waypoint0) (visible waypoint0 waypoint3) (visible waypoint3 waypoint0) (visible waypoint1 waypoint2) (visible waypoint2 waypoint1) (visible waypoint1 waypoint3) (visible waypoint3 waypoint1) (visible waypoint2 waypoint0) (visible waypoint0 waypoint2) (visible waypoint3 waypoint2) (visible waypoint2 waypoint3) (= (recharges) 0) (at_rock_sample waypoint0) (in_sun waypoint0) (at_rock_sample waypoint1) (in_sun waypoint1) (at_soil_sample waypoint2) (at_rock_sample waypoint2) (at_lander general waypoint0) (channel_free general) (= (energy rover0) 50) (at_ rover0 waypoint1) (available rover0) (store_of rover0store rover0) (empty rover0store) (equipped_for_soil_analysis rover0) (equipped_for_rock_analysis rover0) (equipped_for_imaging rover0) (can_traverse rover0 waypoint1 waypoint0) (can_traverse rover0 waypoint0 waypoint1) (can_traverse rover0 waypoint1 waypoint3) (can_traverse rover0 waypoint3 waypoint1) (= (energy rover1) 50) (at_ rover1 waypoint3) (available rover1) (store_of rover1store rover1) (empty rover1store) (equipped_for_soil_analysis rover1) (equipped_for_rock_analysis rover1) (equipped_for_imaging rover1) (can_traverse rover1 waypoint3 waypoint0) (can_traverse rover1 waypoint0 waypoint3) (can_traverse rover1 waypoint3 waypoint2) (can_traverse rover1 waypoint2 waypoint3) (can_traverse rover1 waypoint0 waypoint1) (can_traverse rover1 waypoint1 waypoint0) (on_board camera0 rover0) (calibration_target camera0 objective1) (supports camera0 low_res) (on_board camera1 rover1) (calibration_target camera1 objective0) (supports camera1 colour) (supports camera1 high_res) (supports camera1 low_res) (visible_from objective0 waypoint0) (visible_from objective0 waypoint1) (visible_from objective1 waypoint0) (visible_from objective1 waypoint1))
 (:goal (and (and (communicated_soil_data waypoint2) (communicated_rock_data waypoint0) (communicated_image_data objective0 colour))))
)
