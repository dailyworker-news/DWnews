"""
Worker Impact Scorer

Scores events based on their impact on working-class people ($45k-$350k income bracket).
This is the most important dimension (30% weight) in newsworthiness scoring.

Scoring factors:
- Direct impact on wages, working conditions, job security
- Number of workers affected
- Income bracket relevance ($45k-$350k)
- Labor rights and union activity
- Economic impact on working families
"""

import re
from typing import Dict, Optional


class WorkerImpactScorer:
    """Evaluates how much an event affects working-class people"""

    # High-impact labor keywords (score boost: +3-4)
    HIGH_IMPACT_KEYWORDS = [
        'strike', 'walkout', 'union', 'unionize', 'organize',
        'collective bargaining', 'labor union', 'workers union',
        'picket', 'labor action', 'work stoppage'
    ]

    # Medium-impact labor keywords (score boost: +2-3)
    MEDIUM_IMPACT_KEYWORDS = [
        'wage', 'salary', 'pay', 'overtime', 'benefits',
        'layoff', 'layoffs', 'fired', 'termination',
        'working conditions', 'workplace safety', 'osha',
        'unfair labor practice', 'labor violation',
        'minimum wage', 'living wage', 'pay raise'
    ]

    # Worker rights keywords (score boost: +1-2)
    WORKER_RIGHTS_KEYWORDS = [
        'labor rights', 'worker rights', 'employment law',
        'labor law', 'overtime pay', 'sick leave', 'paid leave',
        'healthcare', 'pension', 'retirement', '401k',
        'contract', 'labor contract', 'arbitration'
    ]

    # Negative impact keywords (indicates harm to workers)
    HARM_KEYWORDS = [
        'exploitation', 'unsafe', 'dangerous', 'injury', 'death',
        'discrimination', 'harassment', 'retaliation',
        'wage theft', 'unpaid', 'illegal', 'violation'
    ]

    # Job sectors with high working-class representation
    WORKING_CLASS_SECTORS = [
        'warehouse', 'retail', 'restaurant', 'food service',
        'manufacturing', 'construction', 'transportation',
        'delivery', 'driver', 'trucking', 'logistics',
        'healthcare worker', 'nurse', 'nursing', 'caregiver',
        'teacher', 'education', 'school', 'janitor', 'custodial',
        'service worker', 'gig worker', 'contractor'
    ]

    # Scale indicators (number of workers affected)
    SCALE_NATIONAL = ['nationwide', 'national', 'federal', 'all workers', 'every worker']
    SCALE_LARGE = ['thousands', 'hundreds', 'major', 'massive', 'widespread']
    SCALE_MEDIUM = ['dozens', 'several', 'multiple', 'group of']

    def __init__(self):
        """Initialize the worker impact scorer"""
        pass

    def score(self, event: Dict) -> float:
        """
        Score an event's impact on working-class people (0-10)

        Args:
            event: Dict with keys: title, description, source_url, discovered_from

        Returns:
            float: Score from 0-10, where 10 = maximum worker impact
        """
        title = (event.get('title') or '').lower()
        description = (event.get('description') or '').lower()
        combined_text = f"{title} {description}"

        score = 0.0

        # 1. Check for high-impact labor keywords (0-4 points)
        high_impact_count = self._count_keywords(combined_text, self.HIGH_IMPACT_KEYWORDS)
        score += min(4.0, high_impact_count * 1.5)

        # 2. Check for medium-impact labor keywords (0-3 points)
        medium_impact_count = self._count_keywords(combined_text, self.MEDIUM_IMPACT_KEYWORDS)
        score += min(3.0, medium_impact_count * 0.8)

        # 3. Check for worker rights keywords (0-2 points)
        rights_count = self._count_keywords(combined_text, self.WORKER_RIGHTS_KEYWORDS)
        score += min(2.0, rights_count * 0.5)

        # 4. Check for harm/exploitation (0-2 points bonus)
        harm_count = self._count_keywords(combined_text, self.HARM_KEYWORDS)
        score += min(2.0, harm_count * 0.7)

        # 5. Check for working-class sectors (0-2 points)
        sector_count = self._count_keywords(combined_text, self.WORKING_CLASS_SECTORS)
        score += min(2.0, sector_count * 0.6)

        # 6. Check for scale indicators (0-2 points)
        scale_score = self._score_scale(combined_text)
        score += scale_score

        # 7. Check for dollar amounts (wage changes, etc.) (0-1.5 points)
        dollar_score = self._score_dollar_amounts(combined_text)
        score += dollar_score

        # 8. Check for worker count mentions (0-1.5 points)
        worker_count_score = self._score_worker_count(combined_text)
        score += worker_count_score

        # Cap at 10 and ensure minimum of 0
        final_score = max(0.0, min(10.0, score))

        return round(final_score, 2)

    def _count_keywords(self, text: str, keywords: list) -> int:
        """Count how many keywords appear in text"""
        count = 0
        for keyword in keywords:
            if keyword in text:
                count += 1
        return count

    def _score_scale(self, text: str) -> float:
        """Score based on scale indicators (how many workers affected)"""
        if any(word in text for word in self.SCALE_NATIONAL):
            return 2.0
        elif any(word in text for word in self.SCALE_LARGE):
            return 1.5
        elif any(word in text for word in self.SCALE_MEDIUM):
            return 1.0
        return 0.0

    def _score_dollar_amounts(self, text: str) -> float:
        """Score based on dollar amount mentions (wage increases, etc.)"""
        # Look for dollar amounts
        dollar_pattern = r'\$[\d,]+(?:\.\d{2})?'
        dollar_matches = re.findall(dollar_pattern, text)

        if not dollar_matches:
            return 0.0

        # Check context around dollar amounts
        wage_context = ['wage', 'pay', 'salary', 'hour', 'raise', 'increase', 'cut', 'reduce']
        has_wage_context = any(word in text for word in wage_context)

        if has_wage_context and len(dollar_matches) > 0:
            return 1.5
        elif len(dollar_matches) > 0:
            return 0.5

        return 0.0

    def _score_worker_count(self, text: str) -> float:
        """Score based on explicit worker count mentions"""
        # Look for patterns like "1000 workers", "500 employees"
        worker_count_pattern = r'(\d{1,3}(?:,\d{3})*)\s*(?:workers|employees|people|members)'
        matches = re.findall(worker_count_pattern, text)

        if not matches:
            return 0.0

        # Extract the largest number
        try:
            counts = [int(m.replace(',', '')) for m in matches]
            max_count = max(counts)

            # Score based on magnitude
            if max_count >= 10000:
                return 1.5  # 10k+ workers
            elif max_count >= 1000:
                return 1.2  # 1k-10k workers
            elif max_count >= 100:
                return 0.8  # 100-1k workers
            else:
                return 0.4  # <100 workers
        except (ValueError, TypeError):
            return 0.0

    def explain_score(self, event: Dict) -> Dict:
        """
        Provide detailed explanation of how score was calculated

        Args:
            event: Event dictionary

        Returns:
            Dict with score breakdown
        """
        title = (event.get('title') or '').lower()
        description = (event.get('description') or '').lower()
        combined_text = f"{title} {description}"

        explanation = {
            'final_score': self.score(event),
            'breakdown': {
                'high_impact_keywords': self._count_keywords(combined_text, self.HIGH_IMPACT_KEYWORDS),
                'medium_impact_keywords': self._count_keywords(combined_text, self.MEDIUM_IMPACT_KEYWORDS),
                'worker_rights_keywords': self._count_keywords(combined_text, self.WORKER_RIGHTS_KEYWORDS),
                'harm_keywords': self._count_keywords(combined_text, self.HARM_KEYWORDS),
                'working_class_sectors': self._count_keywords(combined_text, self.WORKING_CLASS_SECTORS),
                'scale_score': self._score_scale(combined_text),
                'dollar_score': self._score_dollar_amounts(combined_text),
                'worker_count_score': self._score_worker_count(combined_text)
            }
        }

        return explanation
