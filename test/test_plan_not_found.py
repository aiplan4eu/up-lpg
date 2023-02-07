import unified_planning 
from unified_planning.shortcuts import *
from unified_planning.io.pddl_reader import PDDLReader
from unified_planning.io.pddl_writer import PDDLWriter
from unittest import TestCase



reader = PDDLReader()
domain_filename = sys.path[0] + "/pddl/sailing_domain.pddl"
problem_filename = sys.path[0] + "/pddl/sailing_3_3_1229.pddl"

problem = reader.parse_problem(domain_filename,problem_filename)

with OneshotPlanner(name='lpg') as planner:
            result = planner.solve(problem)
            print (result)
            if result.status == up.engines.PlanGenerationResultStatus.SOLVED_SATISFICING:
                print("Lpg returned: %s" % result.plan)
            else:
                print("No plan found.")