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
        problem.environment.factory.add_engine(name = "lpg", module_name = "up_lpg.lpg_planner", class_name = "LPGEngine")

        with OneshotPlanner(name='lpg') as planner:
            result = planner.solve(problem)
            self.assertEqual(result.status.name, 'SOLVED_SATISFICING')


    def test_plan_not_found(self):
        reader = PDDLReader()
        domain_filename = sys.path[0] + "/pddl/sailing_domain.pddl"
        problem_filename = sys.path[0] + "/pddl/sailing_3_3_1229.pddl"
        problem = reader.parse_problem(domain_filename,problem_filename)
        problem.environment.factory.add_engine(name = "lpg", module_name = "up_lpg.lpg_planner", class_name = "LPGEngine")

        with OneshotPlanner(name='lpg') as planner:
            result = planner.solve(problem)
            self.assertTrue(result.status == up.engines.PlanGenerationResultStatus.UNSOLVABLE_INCOMPLETELY)


    def test_anytime(self):
        reader = PDDLReader()
        domain_filename = sys.path[0] + '/pddl/rovers_domain.pddl'
        problem_filename = sys.path[0] + '/pddl/rovers_pfile1.pddl'
        problem = reader.parse_problem(domain_filename,problem_filename)
        problem.add_quality_metric(up.model.metrics.MinimizeSequentialPlanLength())
        problem.environment.factory.add_engine(name = "lpg-anytime", module_name = "up_lpg.lpg_planner", class_name = "LPGAnytimeEngine")

        with AnytimePlanner(name='lpg-anytime') as planner:
                solutions = []
                for p in planner.get_solutions(problem,4):
                    if p.plan is not None:
                        solutions.append(p.plan)
                        self.assertEqual(p.status.name, 'INTERMEDIATE')
                self.assertTrue(len(solutions) >= 1)


    def test_plan_repair(self):
        reader = PDDLReader()
        domain_filename = sys.path[0] + '/pddl/plan_repair/rovers_domain.pddl'
        problem_filename = sys.path[0] + '/pddl/plan_repair/rovers_pfile3.pddl'
        bad_plan_filename = sys.path[0] + '/pddl/plan_repair/plan_p.SOL'
        problem = reader.parse_problem(domain_filename, problem_filename)

        w = PDDLWriter(problem, False)
        w.write_domain(domain_filename)
        w.write_problem(problem_filename)

        with OneshotPlanner(name='lpg') as planner:
            bad_plan = planner._plan_from_file(problem, bad_plan_filename, w.get_item_named)
            with PlanValidator(problem_kind=problem.kind, plan_kind=bad_plan.kind) as validator:
                res = validator.validate(problem, bad_plan)
                self.assertEqual(res.status, up.engines.ValidationResultStatus.INVALID)

        problem.environment.factory.add_engine(name = "lpg-repairer", module_name = "up_lpg.lpg_planner", class_name = "LPGPlanRepairer")

        with PlanRepairer(name='lpg-repairer') as repairer:
            new_plan = repairer.repair(problem, bad_plan).plan
            with PlanValidator(problem_kind=problem.kind, plan_kind=new_plan.kind) as validator:
                res = validator.validate(problem, new_plan)
                self.assertEqual(res.status, up.engines.ValidationResultStatus.VALID)



