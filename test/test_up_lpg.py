import unified_planning
from unified_planning.shortcuts import *
from unified_planning.io.pddl_writer import PDDLWriter
from unified_planning.io.pddl_reader import PDDLReader
from unittest import TestCase

class LPGtest(TestCase):

    def test_lpg(self):
        Location = UserType('Location')

        robot_at = unified_planning.model.Fluent('robot_at', BoolType(), l=Location)
        connected = unified_planning.model.Fluent('connected', BoolType(), l_from=Location, l_to=Location)

        move = unified_planning.model.InstantaneousAction('move', l_from=Location, l_to=Location)
        l_from = move.parameter('l_from')
        l_to = move.parameter('l_to')
        move.add_precondition(connected(l_from, l_to))
        move.add_precondition(robot_at(l_from))
        move.add_effect(robot_at(l_from), False)
        move.add_effect(robot_at(l_to), True)
        print(move)
        
        problem = unified_planning.model.Problem('robot')
        problem.add_fluent(robot_at, default_initial_value=False)
        problem.add_fluent(connected, default_initial_value=False)
        problem.add_action(move)

        NLOC = 10
        locations = [unified_planning.model.Object('l%s' % i, Location) for i in range(NLOC)]
        problem.add_objects(locations)

        problem.set_initial_value(robot_at(locations[0]), True)
        for i in range(NLOC - 1):
            problem.set_initial_value(connected(locations[i], locations[i+1]), True)


        problem.add_goal(robot_at(locations[-1]))
        print(problem)       

        with OneshotPlanner(name='lpg') as planner:
            result = planner.solve(problem)
            if result.status == up.engines.PlanGenerationResultStatus.SOLVED_SATISFICING:
                print("Lpg returned: %s" % result.plan)
            else:
                print("No plan found.")
