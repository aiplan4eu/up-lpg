from tokenize import String
import pkg_resources
import re
import unified_planning as up
from unified_planning.model import ProblemKind
from unified_planning.exceptions import UPException
import asyncio
from asyncio.subprocess import PIPE
import subprocess
import sys
import tempfile
import os
import re
import time
import unified_planning as up
from unified_planning.engines.results import LogLevel, PlanGenerationResult, PlanGenerationResultStatus
from unified_planning.io.pddl_writer import PDDLWriter
from unified_planning.exceptions import UPException
from asyncio.subprocess import PIPE
from typing import IO, Any, Callable, Optional, List, Tuple, cast
from unified_planning.engines import PDDLPlanner, Credits, LogMessage


USE_ASYNCIO_ON_UNIX = False
ENV_USE_ASYNCIO = os.environ.get("UP_USE_ASYNCIO_PDDL_PLANNER")
if ENV_USE_ASYNCIO is not None:
    USE_ASYNCIO_ON_UNIX = ENV_USE_ASYNCIO.lower() in ["true", "1"]


credits = Credits('LPG',
                  'UNIBS Team',
                  'ivan.serina@unibs.it',
                  'https://lpg.unibs.it',
                  '<license>',
                  'LPG is a planner based on local search and planning graphs.',
                  'LPG (Local search for Planning Graphs) is a planner based on local search and planning graphs.')

class LPGEngine(PDDLPlanner):

    def __init__(self):
        super().__init__(needs_requirements=False)

    @staticmethod
    def name() -> str:
        return 'lpg'

    def _get_cmd(self, domain_filename: str, problem_filename: str, plan_filename: str) -> List[str]:
        base_command = [pkg_resources.resource_filename(__name__, 'lpg'), '-o', domain_filename, '-f', problem_filename, '-n', '1', '-out', plan_filename]
        return base_command

    def _solve(self, problem: 'up.model.AbstractProblem',
               callback: Optional[Callable[['up.engines.results.PlanGenerationResult'], None]] = None,
               heuristic: Optional[Callable[["up.model.state.ROState"], Optional[float]]] = None,
               timeout: Optional[float] = None,
               output_stream: Optional[IO[str]] = None) -> 'up.engines.results.PlanGenerationResult':
        assert isinstance(problem, up.model.Problem)
        #callback()
        w = PDDLWriter(problem, self._needs_requirements)
        plan = None
        logs: List['up.engines.results.LogMessage'] = []
        with tempfile.TemporaryDirectory() as tempdir:
            domain_filename = os.path.join(tempdir, 'domain.pddl')
            problem_filename = os.path.join(tempdir, 'problem.pddl')
            plan_filename = os.path.join(tempdir, 'plan.txt')
            w.write_domain(domain_filename)
            w.write_problem(problem_filename)
            cmd = self._get_cmd(domain_filename, problem_filename, plan_filename)
            #callback(output_stream = plan_filename)

            if output_stream is None:
                # If we do not have an output stream to write to, we simply call
                # a subprocess and retrieve the final output and error with communicate
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                timeout_occurred: bool = False
                proc_out: List[str] = []
                proc_err: List[str] = []
                try:
                    out_err_bytes = process.communicate(timeout=timeout)
                    proc_out, proc_err = [[x.decode()] for x in out_err_bytes]
                except subprocess.TimeoutExpired:
                    timeout_occurred = True
                retval = process.returncode
            else:
                if sys.platform == "win32":
                    # On windows we have to use asyncio (does not work inside notebooks)
                    try:
                        loop = asyncio.ProactorEventLoop()
                        exec_res = loop.run_until_complete(run_command_asyncio(cmd, output_stream=output_stream, timeout=timeout))
                    finally:
                        loop.close()
                else:
                    # On non-windows OSs, we can choose between asyncio and posix
                    # select (see comment on USE_ASYNCIO_ON_UNIX variable for details)
                    if USE_ASYNCIO_ON_UNIX:
                        exec_res = asyncio.run(PDDLPlanner.run_command_asyncio(cmd, output_stream=output_stream, timeout=timeout))
                    else:
                        exec_res = PDDLPlanner.run_command_posix_select(cmd, output_stream=output_stream, timeout=timeout)
                timeout_occurred, (proc_out, proc_err), retval = exec_res

            logs.append(up.engines.results.LogMessage(LogLevel.INFO, ''.join(proc_out)))
            logs.append(up.engines.results.LogMessage(LogLevel.ERROR, ''.join(proc_err)))
            if os.path.isfile(plan_filename):
                plan = self._plan_from_file(problem, plan_filename)
            if timeout_occurred and retval != 0:
                return PlanGenerationResult(PlanGenerationResultStatus.TIMEOUT, plan=plan, log_messages=logs, engine_name=self.name)
        status: PlanGenerationResultStatus = self._result_status(problem, plan)
        return PlanGenerationResult(status, plan, log_messages=logs, engine_name=self.name)

    def _get_action_named(self, problem, action_name):
        '''Takes a problem and a name of an action and returns the action'''
        actions = problem.actions
        res_split = re.split(r'-|_', action_name.group(1).lower())
        for a in actions: 
            a_split = re.split(r'-|_', a.name.lower())
            if(a_split == res_split):
                return a
        raise UPException('Action not found')
        
    def _get_object_named(self, problem, parameter):
        '''Takes a problem and a parameter and returns the object'''
        objects = problem.all_objects
        for o in objects: 
            o_split = re.split(r'-|_', o.name.lower())
            par_split = re.split(r'-|_', parameter.lower())
            if(o_split == par_split):
                return o
        raise UPException('Object not found')

    def _plan_from_file(self, problem: 'up.model.Problem', plan_filename: str) -> 'up.plans.Plan':
        '''Takes a problem and a filename and returns the plan parsed from the file.'''
        actions = []
        with open(plan_filename) as plan:
            for line in plan.readlines():
                if re.match(r'^\s*(;.*)?$', line):
                    continue
                res = re.match(r'^\d+:\s*\(\s*([\w?-]+)((\s+[\w?-]+)*)\s*\)\s*\[\d+\]$', line.lower())
                if res:
                    action = self._get_action_named(problem, res)
                    parameters = []
                    for p in res.group(2).split():
                        p_correct = self._get_object_named(problem, p)
                        parameters.append(problem.env.expression_manager.ObjectExp(p_correct))
                    actions.append(up.plans.ActionInstance(action, tuple(parameters)))
                else:
                    raise UPException('Error parsing plan generated by ' + self.__class__.__name__)
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
            return PlanGenerationResultStatus.UNSOLVABLE_PROVEN
        else:
            return PlanGenerationResultStatus.SOLVED_SATISFICING
    

    @staticmethod
    def supported_kind() -> 'ProblemKind':
        supported_kind = ProblemKind()
        supported_kind.set_problem_class('ACTION_BASED')  # type: ignore
        supported_kind.set_numbers('CONTINUOUS_NUMBERS')  # type: ignore
        supported_kind.set_problem_type('SIMPLE_NUMERIC_PLANNING')  # type: ignore
        supported_kind.set_typing('FLAT_TYPING')  # type: ignore
        supported_kind.set_typing('HIERARCHICAL_TYPING')  # type: ignore
        supported_kind.set_fluents_type('NUMERIC_FLUENTS')  # type: ignore
        # supported_kind.set_conditions_kind('NEGATIVE_CONDITIONS')  # type: ignore
        # supported_kind.set_conditions_kind('DISJUNCTIVE_CONDITIONS')  # type: ignore
        supported_kind.set_conditions_kind('EQUALITY')  # type: ignore
        supported_kind.set_numbers('DISCRETE_NUMBERS')  # type: ignore
        supported_kind.set_effects_kind('INCREASE_EFFECTS')  # type: ignore
        supported_kind.set_effects_kind('DECREASE_EFFECTS')
        supported_kind.set_time('CONTINUOUS_TIME')  # type: ignore
        supported_kind.set_expression_duration('STATIC_FLUENTS_IN_DURATION')  # type: ignore
        return supported_kind

    @staticmethod
    def supports(problem_kind: 'ProblemKind') -> bool:
        return problem_kind <= LPGEngine.supported_kind()

    @staticmethod
    def get_credits(**kwargs) -> Optional['Credits']:
        return credits


class LPGAnytimeEngine(PDDLPlanner):

    def __init__(self):
        super().__init__(needs_requirements=False)

    @staticmethod
    def name() -> str:
        return 'lpg'

    def _get_cmd(self, domain_filename: str, problem_filename: str, plan_filename: str) -> List[str]:
        base_command = [pkg_resources.resource_filename(__name__, 'lpg'), '-o', domain_filename, '-f', problem_filename, '-n', '100', '-out', plan_filename]
        return base_command
    
    def _solve(self, problem: 'up.model.AbstractProblem',
               callback: Optional[Callable[['up.engines.results.PlanGenerationResult'], None]] = None,
               heuristic: Optional[Callable[["up.model.state.ROState"], Optional[float]]] = None,
               timeout: Optional[float] = None,
               output_stream: Optional[IO[str]] = None) -> 'up.engines.results.PlanGenerationResult':
        assert isinstance(problem, up.model.Problem)
        #callback()
        w = PDDLWriter(problem, self._needs_requirements)
        plan = None
        logs: List['up.engines.results.LogMessage'] = []
        with tempfile.TemporaryDirectory() as tempdir:
            domain_filename = os.path.join(tempdir, 'domain.pddl')
            problem_filename = os.path.join(tempdir, 'problem.pddl')
            plan_filename = os.path.join(tempdir, 'plan.txt')
            w.write_domain(domain_filename)
            w.write_problem(problem_filename)
            cmd = self._get_cmd(domain_filename, problem_filename, plan_filename)
            #callback(output_stream = plan_filename)

            if output_stream is None:
                # If we do not have an output stream to write to, we simply call
                # a subprocess and retrieve the final output and error with communicate
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                timeout_occurred: bool = False
                proc_out: List[str] = []
                proc_err: List[str] = []
                try:
                    out_err_bytes = process.communicate(timeout=timeout)
                    proc_out, proc_err = [[x.decode()] for x in out_err_bytes]
                except subprocess.TimeoutExpired:
                    timeout_occurred = True
                retval = process.returncode
            else:
                if sys.platform == "win32":
                    # On windows we have to use asyncio (does not work inside notebooks)
                    try:
                        loop = asyncio.ProactorEventLoop()
                        exec_res = loop.run_until_complete(run_command_asyncio(cmd, output_stream=output_stream, timeout=timeout))
                    finally:
                        loop.close()
                else:
                    # On non-windows OSs, we can choose between asyncio and posix
                    # select (see comment on USE_ASYNCIO_ON_UNIX variable for details)
                    if USE_ASYNCIO_ON_UNIX:
                        exec_res = asyncio.run(PDDLPlanner.run_command_asyncio(cmd, output_stream=output_stream, timeout=timeout))
                    else:
                        exec_res = PDDLPlanner.run_command_posix_select(cmd, output_stream=output_stream, timeout=timeout)
                timeout_occurred, (proc_out, proc_err), retval = exec_res

            logs.append(up.engines.results.LogMessage(LogLevel.INFO, ''.join(proc_out)))
            logs.append(up.engines.results.LogMessage(LogLevel.ERROR, ''.join(proc_err)))
            if os.path.isfile(plan_filename):
                plan = self._plan_from_file(problem, plan_filename)
            if timeout_occurred and retval != 0:
                return PlanGenerationResult(PlanGenerationResultStatus.TIMEOUT, plan=plan, log_messages=logs, engine_name=self.name)
        status: PlanGenerationResultStatus = self._result_status(problem, plan)
        return PlanGenerationResult(status, plan, log_messages=logs, engine_name=self.name)


    def _get_action_named(self, problem, action_name):
        '''Takes a problem and a name of an action and returns the action'''
        actions = problem.actions
        res_split = re.split(r'-|_', action_name.group(1).lower())
        for a in actions: 
            a_split = re.split(r'-|_', a.name.lower())
            if(a_split == res_split):
                return a
        raise ValueError
        
    def _get_object_named(self, problem, parameter):
        '''Takes a problem and a parameter and returns the object'''
        objects = problem.all_objects
        for o in objects: 
            o_split = re.split(r'-|_', o.name.lower())
            par_split = re.split(r'-|_', parameter.lower())
            if(o_split == par_split):
                return o
        raise ValueError

    def _plan_from_file(self, problem: 'up.model.Problem', plan_filename: str) -> 'up.plans.Plan':
        '''Takes a problem and a filename and returns the plan parsed from the file.'''
        actions = []
        with open(plan_filename) as plan:
            for line in plan.readlines():
                if re.match(r'^\s*(;.*)?$', line):
                    continue
                res = re.match(r'^\d+:\s*\(\s*([\w?-]+)((\s+[\w?-]+)*)\s*\)\s*\[\d+\]$', line.lower())
                if res:
                    action = self._get_action_named(problem, res)
                    parameters = []
                    for p in res.group(2).split():
                        p_correct = self._get_object_named(problem, p)
                        parameters.append(problem.env.expression_manager.ObjectExp(p_correct))
                    actions.append(up.plans.ActionInstance(action, tuple(parameters)))
                else:
                    raise UPException('Error parsing plan generated by ' + self.__class__.__name__)
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
            return PlanGenerationResultStatus.UNSOLVABLE_PROVEN
        else:
            return PlanGenerationResultStatus.SOLVED_SATISFICING

    @staticmethod
    def supported_kind() -> 'ProblemKind':
        supported_kind = ProblemKind()
        supported_kind.set_problem_class('ACTION_BASED')  # type: ignore
        supported_kind.set_problem_type('SIMPLE_NUMERIC_PLANNING')  # type: ignore
        supported_kind.set_numbers('CONTINUOUS_NUMBERS')  # type: ignore
        supported_kind.set_typing('FLAT_TYPING')  # type: ignore
        supported_kind.set_typing('HIERARCHICAL_TYPING')  # type: ignore
        supported_kind.set_fluents_type('NUMERIC_FLUENTS')  # type: ignore
        # supported_kind.set_conditions_kind('NEGATIVE_CONDITIONS')  # type: ignore
        # supported_kind.set_conditions_kind('DISJUNCTIVE_CONDITIONS')  # type: ignore
        supported_kind.set_conditions_kind('EQUALITY')  # type: ignore
        supported_kind.set_numbers('DISCRETE_NUMBERS')  # type: ignore
        supported_kind.set_effects_kind('INCREASE_EFFECTS')  # type: ignore
        supported_kind.set_effects_kind('DECREASE_EFFECTS')
        supported_kind.set_time('CONTINUOUS_TIME')  # type: ignore
        supported_kind.set_expression_duration('STATIC_FLUENTS_IN_DURATION')  # type: ignore
        return supported_kind

    @staticmethod
    def supports(problem_kind: 'ProblemKind') -> bool:
        return problem_kind <= LPGEngine.supported_kind()

    @staticmethod
    def get_credits(**kwargs) -> Optional['Credits']:
        return credits
