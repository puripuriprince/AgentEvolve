"""Core functionality for AgentEvolve."""

from .agent import EvolutionAgent
from .templates import EvolutionTemplate, TemplateRegistry
from .evaluator import EvaluatorGenerator

__all__ = ["EvolutionAgent", "EvolutionTemplate", "TemplateRegistry", "EvaluatorGenerator"]
