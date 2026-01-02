"""
Social Media Investigation Module for Investigatory Journalist Agent (Phase 6.9.2)

Provides deep social media research capabilities:
- Twitter API v2 extended search
- Reddit API extended search
- Social source credibility scoring
- Timeline construction from social mentions
- Eyewitness account identification
"""

from .twitter_investigation import TwitterInvestigationMonitor
from .reddit_investigation import RedditInvestigationMonitor
from .social_credibility import SocialSourceCredibility
from .timeline_constructor import TimelineConstructor
from .eyewitness_detector import EyewitnessDetector

__all__ = [
    'TwitterInvestigationMonitor',
    'RedditInvestigationMonitor',
    'SocialSourceCredibility',
    'TimelineConstructor',
    'EyewitnessDetector',
]
