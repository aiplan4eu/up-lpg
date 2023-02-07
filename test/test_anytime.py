import unified_planning
from unified_planning.shortcuts import *
from unified_planning.io.pddl_reader import PDDLReader
from unittest import TestCase

class LPGTestAnytime(TestCase):

    def test_anytime(self):

        reader = PDDLReader()
        domain_filename = sys.path[0] + '/pddl/rovers_domain.pddl'
        problem_filename = sys.path[0] + '/pddl/rovers_pfile1.pddl'

        problem = reader.parse_problem(domain_filename,problem_filename)
        problem.add_quality_metric(MinimizeSequentialPlanLength())

<<<<<<< Updated upstream
        with AnytimePlanner(name='lpg-anytime') as planner:
                solutions = []
                for p in planner.get_solutions(problem,4):
                    if p.plan is not None:
                        solutions.append(p.plan)
                        self.assertEqual(p.status.name, 'INTERMEDIATE')
                self.assertTrue(len(solutions) >= 1)
=======
        with AnytimePlanner(name="lpg-anytime") as planner:

               solutions = []
               for p in planner.get_solutions(problem,4):
                if p.plan is not None:
                    solutions.append(p.plan)
                    print(p.plan)


    def test_anytimeReader(self):

        reader = PDDLReader()
        domain_filename = sys.path[0] + "/domain.pddl"
        problem_filename = sys.path[0] + "/problem.pddl"

        problem = reader.parse_problem(domain_filename,problem_filename)
        problem.add_quality_metric(MinimizeSequentialPlanLength())

        with AnytimePlanner(name="lpg-anytime") as planner:

               solutions = []
               for p in planner.get_solutions(problem,4):
                if p.plan is not None:
                    solutions.append(p.plan)
                    print(p.plan)
>>>>>>> Stashed changes
