"""
Conflict/Controversy Scorer

Scores events based on conflict, injustice, or struggle.
Worker vs. employer dynamics, power imbalances, injustice.

Scoring factors:
- Labor conflict (strikes, disputes)
- Power dynamics (workers vs. management)
- Injustice/unfairness
- Legal conflicts (lawsuits, violations)
- Social conflict
"""

from typing import Dict


class ConflictScorer:
    """Evaluates conflict and controversy in events"""

    # High-conflict labor actions (score boost: +3-4)
    HIGH_CONFLICT_KEYWORDS = [
        'strike', 'walkout', 'protest', 'demonstration',
        'lockout', 'picket', 'boycott', 'work stoppage',
        'labor dispute', 'labor conflict', 'standoff'
    ]

    # Legal conflict keywords (score boost: +2-3)
    LEGAL_CONFLICT_KEYWORDS = [
        'lawsuit', 'sued', 'litigation', 'court case',
        'legal action', 'violation', 'complaint', 'charges',
        'settlement', 'verdict', 'ruling', 'injunction',
        'class action', 'labor violation', 'unfair labor practice'
    ]

    # Injustice/unfairness keywords (score boost: +2-3)
    INJUSTICE_KEYWORDS = [
        'injustice', 'unfair', 'discrimination', 'inequality',
        'exploitation', 'abuse', 'harassment', 'retaliation',
        'wrongful', 'illegal', 'unlawful', 'violated rights',
        'denied', 'refused', 'fired illegally', 'wage theft'
    ]

    # Power dynamics keywords (score boost: +1-2)
    POWER_DYNAMICS_KEYWORDS = [
        'workers vs', 'employees vs', 'union vs',
        'management', 'employer', 'corporation', 'company',
        'fight for', 'demand', 'demands', 'fighting back',
        'stand up', 'resist', 'oppose', 'challenge'
    ]

    # Struggle/resistance keywords (score boost: +1-2)
    STRUGGLE_KEYWORDS = [
        'struggle', 'battle', 'fight', 'resistance',
        'organize', 'organizing', 'mobilize', 'rally',
        'solidarity', 'united', 'together', 'collective action'
    ]

    # Safety/danger keywords (score boost: +2-3)
    SAFETY_KEYWORDS = [
        'unsafe', 'dangerous', 'hazardous', 'risk',
        'injury', 'death', 'accident', 'workplace death',
        'osha violation', 'safety violation', 'negligence'
    ]

    # Resolution/agreement keywords (score reduction: -1 to -2)
    RESOLUTION_KEYWORDS = [
        'agreement', 'settled', 'resolved', 'compromise',
        'deal reached', 'contract signed', 'ratified',
        'peaceful', 'amicable', 'consensus'
    ]

    def __init__(self):
        """Initialize the conflict scorer"""
        pass

    def score(self, event: Dict) -> float:
        """
        Score an event's conflict/controversy level (0-10)

        Args:
            event: Dict with keys: title, description

        Returns:
            float: Score from 0-10, where 10 = maximum conflict/controversy
        """
        title = (event.get('title') or '').lower()
        description = (event.get('description') or '').lower()
        combined_text = f"{title} {description}"

        score = 0.0

        # 1. Check for high-conflict labor actions (0-4 points)
        high_conflict_count = sum(1 for keyword in self.HIGH_CONFLICT_KEYWORDS if keyword in combined_text)
        score += min(4.0, high_conflict_count * 2.0)

        # 2. Check for legal conflicts (0-3 points)
        legal_count = sum(1 for keyword in self.LEGAL_CONFLICT_KEYWORDS if keyword in combined_text)
        score += min(3.0, legal_count * 1.0)

        # 3. Check for injustice/unfairness (0-3 points)
        injustice_count = sum(1 for keyword in self.INJUSTICE_KEYWORDS if keyword in combined_text)
        score += min(3.0, injustice_count * 1.0)

        # 4. Check for power dynamics (0-2 points)
        power_count = sum(1 for keyword in self.POWER_DYNAMICS_KEYWORDS if keyword in combined_text)
        score += min(2.0, power_count * 0.7)

        # 5. Check for struggle/resistance (0-2 points)
        struggle_count = sum(1 for keyword in self.STRUGGLE_KEYWORDS if keyword in combined_text)
        score += min(2.0, struggle_count * 0.7)

        # 6. Check for safety issues (0-3 points)
        safety_count = sum(1 for keyword in self.SAFETY_KEYWORDS if keyword in combined_text)
        score += min(3.0, safety_count * 1.5)

        # 7. Reduce score for resolutions (peaceful endings)
        resolution_count = sum(1 for keyword in self.RESOLUTION_KEYWORDS if keyword in combined_text)
        if resolution_count >= 2:
            score -= 2.0
        elif resolution_count >= 1:
            score -= 1.0

        # 8. Bonus for multiple conflict dimensions
        # If event has labor conflict + legal + injustice = very newsworthy
        dimensions = 0
        if high_conflict_count > 0:
            dimensions += 1
        if legal_count > 0:
            dimensions += 1
        if injustice_count > 0:
            dimensions += 1
        if safety_count > 0:
            dimensions += 1

        if dimensions >= 3:
            score += 1.5
        elif dimensions >= 2:
            score += 0.5

        # Cap at 10 and ensure minimum of 0
        final_score = max(0.0, min(10.0, score))

        return round(final_score, 2)

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

        high_conflict_count = sum(1 for k in self.HIGH_CONFLICT_KEYWORDS if k in combined_text)
        legal_count = sum(1 for k in self.LEGAL_CONFLICT_KEYWORDS if k in combined_text)
        injustice_count = sum(1 for k in self.INJUSTICE_KEYWORDS if k in combined_text)
        power_count = sum(1 for k in self.POWER_DYNAMICS_KEYWORDS if k in combined_text)
        struggle_count = sum(1 for k in self.STRUGGLE_KEYWORDS if k in combined_text)
        safety_count = sum(1 for k in self.SAFETY_KEYWORDS if k in combined_text)
        resolution_count = sum(1 for k in self.RESOLUTION_KEYWORDS if k in combined_text)

        dimensions = sum([
            1 if high_conflict_count > 0 else 0,
            1 if legal_count > 0 else 0,
            1 if injustice_count > 0 else 0,
            1 if safety_count > 0 else 0
        ])

        explanation = {
            'final_score': self.score(event),
            'breakdown': {
                'high_conflict_count': high_conflict_count,
                'legal_conflict_count': legal_count,
                'injustice_count': injustice_count,
                'power_dynamics_count': power_count,
                'struggle_count': struggle_count,
                'safety_count': safety_count,
                'resolution_count': resolution_count,
                'conflict_dimensions': dimensions
            }
        }

        return explanation
