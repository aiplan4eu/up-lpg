import unified_planning 
from unified_planning.shortcuts import *
from unified_planning.io.pddl_reader import PDDLReader
from unified_planning.io.pddl_writer import PDDLWriter
from unittest import TestCase



reader = PDDLReader()
domain_filename = sys.path[0] + "/domain.pddl"
problem_filename = sys.path[0] + "/problem.pddl"

problem = reader.parse_problem(domain_filename,problem_filename)
problem.add_quality_metric(MinimizeSequentialPlanLength())
print(problem)
w = PDDLWriter(problem)
domain_out = sys.path[0] + "/domain_out.pddl"
problem_out= sys.path[0] + "/problem_out.pddl"
w.write_domain(domain_out)
w.write_problem(problem_out)

problem = reader.parse_problem(domain_out, problem_out)

with OneshotPlanner(name='lpg') as planner:
            result = planner.solve(problem)
            if result.status == up.engines.PlanGenerationResultStatus.SOLVED_SATISFICING:
                print("Lpg returned: %s" % result.plan)
            else:
                print("No plan found.")
