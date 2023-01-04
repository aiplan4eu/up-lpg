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
