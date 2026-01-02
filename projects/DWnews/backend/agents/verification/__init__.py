"""
Verification Agent - Source Verification & Attribution

This module provides source verification and fact-checking capabilities
for the automated journalism pipeline.
"""

from .source_identifier import SourceIdentifier
from .cross_reference import CrossReferenceVerifier
from .fact_classifier import FactClassifier
from .source_ranker import SourceRanker

__all__ = [
    'SourceIdentifier',
    'CrossReferenceVerifier',
    'FactClassifier',
    'SourceRanker'
]
