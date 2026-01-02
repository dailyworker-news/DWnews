"""
Readability Checker Module - Flesch-Kincaid Reading Level Validation
Validates article reading level for working-class accessibility
"""

import re
from typing import Dict, Any, Optional


class ReadabilityChecker:
    """
    Validates article reading level using Flesch-Kincaid Grade Level.
    Target: 7.5-8.5 (high school freshman, accessible to working class)
    """

    TARGET_MIN = 7.5
    TARGET_MAX = 8.5

    def __init__(self):
        """Initialize readability checker"""
        self.textstat_available = False
        try:
            import textstat
            self.textstat = textstat
            self.textstat_available = True
        except ImportError:
            # Fallback to manual calculation if textstat not available
            pass

    def check_reading_level(self, article_text: str) -> float:
        """
        Calculate Flesch-Kincaid Grade Level for article.

        Args:
            article_text: Full article text

        Returns:
            float: Flesch-Kincaid grade level score
        """
        if self.textstat_available:
            return self._check_with_textstat(article_text)
        else:
            return self._check_manual(article_text)

    def _check_with_textstat(self, article_text: str) -> float:
        """Use textstat library for accurate calculation"""
        return self.textstat.flesch_kincaid_grade(article_text)

    def _check_manual(self, article_text: str) -> float:
        """
        Manual Flesch-Kincaid calculation when textstat unavailable.

        Formula:
        0.39 * (total words / total sentences) + 11.8 * (total syllables / total words) - 15.59
        """
        # Count sentences
        sentences = self._count_sentences(article_text)

        # Count words
        words = self._count_words(article_text)

        # Count syllables
        syllables = self._count_syllables(article_text)

        if sentences == 0 or words == 0:
            return 0.0

        # Flesch-Kincaid Grade Level formula
        score = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59

        return round(score, 1)

    def _count_sentences(self, text: str) -> int:
        """Count sentences in text"""
        # Split on sentence-ending punctuation
        sentences = re.split(r'[.!?]+', text)
        # Filter empty strings
        sentences = [s.strip() for s in sentences if s.strip()]
        return len(sentences)

    def _count_words(self, text: str) -> int:
        """Count words in text"""
        # Remove punctuation and split on whitespace
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        return len(words)

    def _count_syllables(self, text: str) -> int:
        """Count syllables in text (approximate)"""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

        total_syllables = 0
        for word in words:
            syllables = self._count_syllables_in_word(word)
            total_syllables += syllables

        return total_syllables

    def _count_syllables_in_word(self, word: str) -> int:
        """
        Count syllables in a single word (approximate).
        Uses simple vowel-counting heuristic.
        """
        word = word.lower()

        # Count vowel groups
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent 'e' at end
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1

        # Ensure at least 1 syllable
        if syllable_count == 0:
            syllable_count = 1

        return syllable_count

    def is_within_target_range(self, score: float) -> bool:
        """Check if score is within target range (7.5-8.5)"""
        return self.TARGET_MIN <= score <= self.TARGET_MAX

    def get_reading_level_description(self, score: float) -> str:
        """Get human-readable description of reading level"""
        if score < 6:
            return "Elementary school level"
        elif score < 7:
            return "6th-7th grade level"
        elif 7.5 <= score <= 8.5:
            return "Target level: High school freshman (accessible to working class)"
        elif score < 9:
            return "8th-9th grade level"
        elif score < 10:
            return "High school sophomore level"
        elif score < 12:
            return "High school junior-senior level"
        elif score < 14:
            return "College level"
        else:
            return "Graduate school level"

    def get_adjustment_suggestion(self, score: float) -> Optional[str]:
        """Get suggestion for adjusting reading level to target range"""
        if self.is_within_target_range(score):
            return None

        if score < self.TARGET_MIN:
            return (
                "Reading level too simple. "
                "Consider: longer sentences, more complex vocabulary, "
                "more sophisticated phrasing while maintaining clarity."
            )
        else:
            return (
                "Reading level too complex. "
                "Consider: shorter sentences, simpler vocabulary, "
                "breaking complex ideas into smaller chunks."
            )

    def analyze_article(self, article_text: str) -> Dict[str, Any]:
        """
        Comprehensive readability analysis.

        Returns:
            Dict with score, description, within_target, and suggestion
        """
        score = self.check_reading_level(article_text)
        within_target = self.is_within_target_range(score)
        description = self.get_reading_level_description(score)
        suggestion = self.get_adjustment_suggestion(score)

        return {
            "score": score,
            "description": description,
            "within_target": within_target,
            "target_range": f"{self.TARGET_MIN}-{self.TARGET_MAX}",
            "suggestion": suggestion
        }
