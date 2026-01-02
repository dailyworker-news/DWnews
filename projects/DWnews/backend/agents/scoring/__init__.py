"""
Newsworthiness Scoring Package

Contains all scoring modules for the Evaluation Agent.
Each scorer evaluates events on a specific dimension (0-10 scale).
"""

from .worker_impact_scorer import WorkerImpactScorer
from .timeliness_scorer import TimelinessScorer
from .verifiability_scorer import VerifiabilityScorer
from .regional_scorer import RegionalScorer
from .conflict_scorer import ConflictScorer
from .novelty_scorer import NoveltyScorer

__all__ = [
    'WorkerImpactScorer',
    'TimelinessScorer',
    'VerifiabilityScorer',
    'RegionalScorer',
    'ConflictScorer',
    'NoveltyScorer'
]
