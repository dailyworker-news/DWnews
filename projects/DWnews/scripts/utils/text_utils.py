"""
The Daily Worker - Text Utilities
Helper functions for text processing and analysis
"""

import re
import hashlib
from typing import List, Set
from difflib import SequenceMatcher


def generate_hash(text: str) -> str:
    """Generate MD5 hash from text for deduplication"""
    if not text:
        return ""
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-\']', '', text)

    return text.strip()


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text (simple frequency-based)"""
    if not text:
        return []

    # Simple stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
        'those', 'it', 'its', 'they', 'their', 'them', 'we', 'our', 'us'
    }

    # Extract words
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())

    # Filter stop words and count frequency
    word_freq = {}
    for word in words:
        if word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1

    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:max_keywords]]


def text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts (0.0 to 1.0)"""
    if not text1 or not text2:
        return 0.0

    # Normalize texts
    t1 = clean_text(text1.lower())
    t2 = clean_text(text2.lower())

    # Use SequenceMatcher for similarity
    return SequenceMatcher(None, t1, t2).ratio()


def generate_text_hash(text: str) -> str:
    """Generate a hash for text deduplication"""
    if not text:
        return ""

    # Normalize text
    normalized = clean_text(text.lower())

    # Generate hash
    return hashlib.md5(normalized.encode()).hexdigest()


def find_duplicates(texts: List[str], threshold: float = 0.85) -> List[Set[int]]:
    """Find duplicate texts based on similarity threshold

    Returns list of sets, where each set contains indices of similar texts
    """
    duplicates = []
    processed = set()

    for i in range(len(texts)):
        if i in processed:
            continue

        similar = {i}
        for j in range(i + 1, len(texts)):
            if j in processed:
                continue

            if text_similarity(texts[i], texts[j]) >= threshold:
                similar.add(j)
                processed.add(j)

        if len(similar) > 1:
            duplicates.append(similar)
            processed.add(i)

    return duplicates


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to max length"""
    if not text or len(text) <= max_length:
        return text

    # Find last space before max_length
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')

    if last_space > 0:
        truncated = truncated[:last_space]

    return truncated + suffix


def contains_keywords(text: str, keywords: List[str], match_any: bool = True) -> bool:
    """Check if text contains specified keywords

    Args:
        text: Text to search
        keywords: List of keywords to find
        match_any: If True, match any keyword. If False, match all keywords.
    """
    if not text or not keywords:
        return False

    text_lower = text.lower()

    if match_any:
        return any(keyword.lower() in text_lower for keyword in keywords)
    else:
        return all(keyword.lower() in text_lower for keyword in keywords)


def categorize_by_keywords(text: str) -> str:
    """Categorize text based on keywords (simple heuristic)"""
    text_lower = text.lower()

    # Category keyword mapping
    category_keywords = {
        'labor': ['union', 'strike', 'worker', 'wage', 'labor', 'employment', 'job', 'workplace', 'overtime', 'benefits'],
        'tech': ['technology', 'software', 'ai', 'artificial intelligence', 'crypto', 'tech', 'digital', 'algorithm', 'data'],
        'politics': ['election', 'vote', 'congress', 'senate', 'president', 'legislation', 'policy', 'government', 'campaign'],
        'economics': ['economy', 'inflation', 'recession', 'federal reserve', 'market', 'price', 'cost', 'budget', 'debt', 'gdp'],
        'environment': ['climate', 'environment', 'pollution', 'renewable', 'carbon', 'emissions', 'energy', 'sustainability'],
        'art-culture': ['art', 'music', 'film', 'culture', 'book', 'artist', 'museum', 'theater', 'entertainment'],
        'sport': ['sport', 'football', 'baseball', 'basketball', 'soccer', 'nfl', 'nba', 'mlb', 'athlete', 'game'],
        'good-news': ['victory', 'win', 'success', 'achievement', 'positive', 'improvement', 'breakthrough', 'celebration']
    }

    # Score each category
    scores = {}
    for category, keywords in category_keywords.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            scores[category] = score

    # Return category with highest score, or 'current-affairs' as default
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    return 'current-affairs'


if __name__ == "__main__":
    # Test utilities
    print("Testing text utilities...")

    text1 = "Amazon workers win union vote in historic victory"
    text2 = "Amazon employees secure union victory in historical win"

    print(f"\nSimilarity: {text_similarity(text1, text2):.2f}")
    print(f"Keywords: {extract_keywords(text1)}")
    print(f"Category: {categorize_by_keywords(text1)}")
    print(f"Hash: {generate_text_hash(text1)}")
