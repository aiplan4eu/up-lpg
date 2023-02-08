import unified_planning 
from unified_planning.shortcuts import *
from unified_planning.io.pddl_reader import PDDLReader
from unified_planning.io.pddl_writer import PDDLWriter
from unittest import TestCase

class LPGTestPlanNotFound(TestCase):

    def test_plan_not_found(self):

        reader = PDDLReader()
        domain_filename = sys.path[0] + "/pddl/sailing_domain.pddl"
        problem_filename = sys.path[0] + "/pddl/sailing_3_3_1229.pddl"

        problem = reader.parse_problem(domain_filename,problem_filename)




        with OneshotPlanner(name='lpg') as planner:

            result = planner.solve(problem)
            self.assertTrue(result.status == up.engines.PlanGenerationResultStatus.UNSOLVABLE_INCOMPLETELY )