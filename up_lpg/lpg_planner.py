import pkg_resources
import re
import os
import sys
import tempfile
import unified_planning as up
from fractions import Fraction
from unified_planning.model import ProblemKind, AbstractProblem
from unified_planning.plans import PlanKind, Plan
from unified_planning.engines import PlanGenerationResult, PlanGenerationResultStatus
from unified_planning.engines import PDDLPlanner, Credits, LogMessage, PlanGenerationResult
from unified_planning.exceptions import UPException
from unified_planning.engines.pddl_anytime_planner import PDDLAnytimePlanner
from unified_planning.engines.mixins.plan_repairer import PlanRepairerMixin
from typing import Callable, Optional, List, Union, Iterator, IO

credits = Credits('LPG',
                  'UNIBS Team',
                  'ivan.serina@unibs.it',
                  'https://lpg.unibs.it',
                  '<license>',
                  'LPG is a planner based on local search and planning graphs.',
                  'LPG (Local search for Planning Graphs) is a planner based on local search and planning graphs.')

lpg_os = {'win32':'winlpg.exe',
          'linux': 'lpg'}

LPG_EPSILON = 0.00025

class LPGEngine(PDDLPlanner):

    def __init__(self, **kwargs):
        super().__init__(needs_requirements=False)
        self.parameter = []
        for param, val in kwargs.items():
            self.parameter.append(str(param))
            if val != '':
                self.parameter.append(str(val))

    @property
    def name(self) -> str:
        return 'lpg'

    def _get_cmd(self, domain_filename: str, problem_filename: str, plan_filename: str) -> List[str]:
            base_command = pkg_resources.resource_filename(__name__, lpg_os[sys.platform]), '-o', domain_filename, '-f', problem_filename, '-n', '1', '-out', plan_filename, *self.parameter
            return base_command

    def  _get_engine_epsilon(self) -> Optional[Fraction]:
        return LPG_EPSILON

    def _plan_from_file(self, problem: 'up.model.Problem', plan_filename: str, get_item_named: Callable[[str],
            Union[
                'up.model.Type',
                'up.model.Action',
                'up.model.Fluent',
                'up.model.Object',
                'up.model.Parameter',
                'up.model.Variable',
            ],
        ],) -> 'up.plans.Plan':
        '''Takes a problem and a filename and returns the plan parsed from the file.'''
        actions = []
        tt = False
        if 'CONTINUOUS_TIME' in problem.kind.features:
            tt = True
        with open(plan_filename) as plan:
            for line in plan.readlines():
                if re.match(r'^\s*(;.*)?$', line):
                    continue
                res = re.match(r'^[\d.]+:\s*\(\s*([\w?-]+)((\s+[\w?-]+)*)\s*\)\s*\[.*\]$', line.lower().split(' ;;')[0])
                if res:
                    action = get_item_named(res.group(1))
                    parameters = []
                    for p in res.group(2).split():
                        p_correct = get_item_named(p)
                        parameters.append(problem.environment.expression_manager.ObjectExp(p_correct))
                    if tt:
                        start = re.match(r'^([\d.]+):', line).group(1)
                        dur = re.match(r'^[\d.]+:\s*\(\s*[\w?-]+((\s+[\w?-]+)*)\s*\)\s*\[([\d.]+)\]$', line).group(3)
                        actions.append((start,up.plans.ActionInstance(action, tuple(parameters)),dur))
                    else:
                        actions.append(up.plans.ActionInstance(action, tuple(parameters)))
                elif re.match(r'no solution', line):
                    return None
                else:
                    raise UPException('Error parsing plan generated by ' + self.__class__.__name__)

        if tt:
            return up.plans.TimeTriggeredPlan(actions)
        else:
            return up.plans.SequentialPlan(actions)

    def _result_status(
        self,
        problem: 'up.model.Problem',
        plan: Optional['up.plan.Plan'],
        retval: int = 0,
        log_messages: Optional[List['LogMessage']] = None,
        ) -> 'PlanGenerationResultStatus':
        if retval != 0:
            return PlanGenerationResultStatus.INTERNAL_ERROR
        elif plan is None:
            return PlanGenerationResultStatus.UNSOLVABLE_INCOMPLETELY
        else:
            return PlanGenerationResultStatus.SOLVED_SATISFICING

    @staticmethod
    def supported_kind() -> 'ProblemKind':
        supported_kind = ProblemKind(version=2)
        supported_kind.set_problem_class('ACTION_BASED')  # type: ignore
        supported_kind.set_problem_type('SIMPLE_NUMERIC_PLANNING')  # type: ignore
        supported_kind.set_problem_type("GENERAL_NUMERIC_PLANNING")  # type: ignore
        supported_kind.set_typing('FLAT_TYPING')  # type: ignore
        supported_kind.set_typing('HIERARCHICAL_TYPING')  # type: ignore
        supported_kind.set_fluents_type('INT_FLUENTS')  # type: ignore
        supported_kind.set_fluents_type('REAL_FLUENTS')  # type: ignore
        supported_kind.set_conditions_kind('EQUALITIES')  # type: ignore
        supported_kind.set_effects_kind('INCREASE_EFFECTS')  # type: ignore
        supported_kind.set_effects_kind('DECREASE_EFFECTS')  # type: ignore
        supported_kind.set_effects_kind('STATIC_FLUENTS_IN_NUMERIC_ASSIGNMENTS')  # type: ignore
        supported_kind.set_effects_kind('FLUENTS_IN_NUMERIC_ASSIGNMENTS')  # type: ignore
        supported_kind.set_time('CONTINUOUS_TIME')  # type: ignore
        supported_kind.set_quality_metrics('PLAN_LENGTH') # type: ignore
        supported_kind.set_expression_duration('INT_TYPE_DURATIONS')  # type: ignore
        supported_kind.set_expression_duration('REAL_TYPE_DURATIONS')  # type: ignore
        supported_kind.set_expression_duration('STATIC_FLUENTS_IN_DURATIONS')  # type: ignore
        supported_kind.set_actions_cost_kind('INT_NUMBERS_IN_ACTIONS_COST')  # type: ignore
        supported_kind.set_actions_cost_kind('REAL_NUMBERS_IN_ACTIONS_COST')  # type: ignore
        supported_kind.set_actions_cost_kind('STATIC_FLUENTS_IN_ACTIONS_COST')  # type: ignore
        supported_kind.set_actions_cost_kind('FLUENTS_IN_ACTIONS_COST')  # type: ignore
        return supported_kind

    @staticmethod
    def supports(problem_kind: 'ProblemKind') -> bool:
        return problem_kind <= LPGEngine.supported_kind()

    @staticmethod
    def get_credits(**kwargs) -> Optional['Credits']:
        return credits

class LPGAnytimeEngine(LPGEngine, PDDLAnytimePlanner):

    def __init__(self):
        super().__init__()
        self._options = []

    @property
    def name(self) -> str:
        return 'lpg-anytime'

    def _get_anytime_cmd(self, domain_filename: str, problem_filename: str, plan_filename: str) -> List[str]:
        base_command = [pkg_resources.resource_filename(__name__, lpg_os[sys.platform]),
        '-o', domain_filename,
        '-f', problem_filename,
        '-n', '1000',
        '-noout'] + self._options
        return base_command

    def _get_solutions(
        self,
        problem: 'up.model.AbstractProblem',
        timeout: Optional[float] = None,
        output_stream: Optional[IO[str]] = None,
    ) -> Iterator['up.engines.results.PlanGenerationResult']:
        import threading
        import queue

        q: queue.Queue = queue.Queue()

        if timeout is not None:
            self._options.extend(['-cputime', str(timeout)])
        else:
            self._options.extend(['-cputime', '1200'])

        class Writer(up.AnyBaseClass):
            def __init__(self, os, q, engine):
                self._os = os
                self._q = q
                self._engine = engine
                self._plan = []
                self._storing = False

            def write(self, txt: str):
                if self._os is not None:
                    self._os.write(txt)
                for l in txt.splitlines():
                    if '   Time: (ACTION) [action Duration; action Cost]' in l:
                        self._storing = True
                    elif 'METRIC_VALUE' in l or 'Solution number:' in l and self._storing:
                        plan_str = '\n'.join(self._plan)
                        plan = self._engine._plan_from_str(
                            problem, plan_str, self._engine._writer.get_item_named
                        )
                        res = PlanGenerationResult(
                            PlanGenerationResultStatus.INTERMEDIATE,
                            plan=plan,
                            engine_name=self._engine.name,
                        )
                        self._q.put(res)
                        self._plan = []
                        self._storing = False
                    elif self._storing and l:
                        self._plan.append(l.split(':')[1].split('[')[0])

        def run():
            writer: IO[str] = Writer(output_stream, q, self)
            res = self._solve(problem, output_stream=writer, anytime=True)
            q.put(res)

        try:
            t = threading.Thread(target=run, daemon=True)
            t.start()
            status = PlanGenerationResultStatus.INTERMEDIATE
            while status == PlanGenerationResultStatus.INTERMEDIATE:
                res = q.get()
                status = res.status
                yield res
        finally:
            if self._process is not None:
                try:
                    self._process.kill()
                except OSError:
                    pass  # This can happen if the process is already terminated
            t.join()

    @staticmethod
    def ensures(anytime_guarantee: up.engines.AnytimeGuarantee) -> bool:
        if anytime_guarantee == up.engines.AnytimeGuarantee.INCREASING_QUALITY:
            return True
        return False


class LPGPlanRepairer(LPGEngine, PlanRepairerMixin):

    def __init__(self):
        super().__init__()
        self._options = []

    @property
    def name(self) -> str:
        return 'lpg-repairer'

    def _repair(self, problem: AbstractProblem, plan: Plan) -> PlanGenerationResult:
        with tempfile.TemporaryDirectory() as tempdir:
            plan_to_repair_filename = os.path.join(tempdir, "plan_to_repair.SOL")
            self.plan_to_file(plan, plan_to_repair_filename)
            self._options.extend(['-input_plan', plan_to_repair_filename])
            return self.solve(problem)

    def plan_to_file(self, plan: Plan, out: IO[str]):
        with open(out, "w") as f:
            for i, act in enumerate(plan.actions):
                parameters = str(act.actual_parameters).replace('(','').replace(')','').replace(',','')
                if parameters == '':
                    f.write(f'{i}:   ({act.action.name})  [1]\n')
                else:
                    f.write(f'{i}:   ({act.action.name} {parameters})  [1]\n')

    @staticmethod
    def supports_plan(plan_kind: "up.plans.PlanKind") -> bool:
        return plan_kind == PlanKind.SEQUENTIAL_PLAN
