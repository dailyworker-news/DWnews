"""
Tests for text utility functions
"""

import pytest
from scripts.utils.text_utils import (
    clean_text,
    extract_keywords,
    text_similarity,
    generate_text_hash,
    find_duplicates,
    truncate_text,
    contains_keywords,
    categorize_by_keywords
)


class TestTextCleaning:
    """Test text cleaning functions"""

    def test_clean_text_basic(self):
        """Test basic text cleaning"""
        text = "  Hello   World  "
        result = clean_text(text)
        assert result == "Hello World"

    def test_clean_text_special_chars(self):
        """Test special character removal"""
        text = "Hello @#$ World!!!"
        result = clean_text(text)
        assert "@#$" not in result
        assert "Hello" in result
        assert "World" in result

    def test_clean_text_empty(self):
        """Test cleaning empty text"""
        assert clean_text("") == ""
        assert clean_text(None) == ""

    def test_clean_text_preserves_punctuation(self):
        """Test that basic punctuation is preserved"""
        text = "Hello, World! How are you?"
        result = clean_text(text)
        assert "," in result
        assert "!" in result
        assert "?" in result


class TestKeywordExtraction:
    """Test keyword extraction"""

    def test_extract_keywords_basic(self):
        """Test basic keyword extraction"""
        text = "Amazon workers union victory strike"
        keywords = extract_keywords(text)

        assert "amazon" in keywords
        assert "workers" in keywords
        assert "union" in keywords
        assert "victory" in keywords

    def test_extract_keywords_filters_stopwords(self):
        """Test that stopwords are filtered"""
        text = "the workers and the union"
        keywords = extract_keywords(text)

        assert "the" not in keywords
        assert "and" not in keywords
        assert "workers" in keywords
        assert "union" in keywords

    def test_extract_keywords_limit(self):
        """Test keyword count limit"""
        text = "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11"
        keywords = extract_keywords(text, max_keywords=5)

        assert len(keywords) <= 5

    def test_extract_keywords_frequency(self):
        """Test that most frequent words are returned first"""
        text = "union union union workers workers strike"
        keywords = extract_keywords(text, max_keywords=3)

        assert keywords[0] == "union"  # Most frequent


class TestTextSimilarity:
    """Test text similarity detection"""

    def test_similarity_identical(self):
        """Test similarity of identical texts"""
        text1 = "Amazon workers win union vote"
        text2 = "Amazon workers win union vote"
        similarity = text_similarity(text1, text2)

        assert similarity >= 0.95

    def test_similarity_similar(self):
        """Test similarity of similar texts"""
        text1 = "Amazon workers win union vote"
        text2 = "Amazon employees secure union victory"
        similarity = text_similarity(text1, text2)

        assert 0.3 <= similarity <= 0.8

    def test_similarity_different(self):
        """Test similarity of different texts"""
        text1 = "Amazon workers win union vote"
        text2 = "Climate change affects polar bears"
        similarity = text_similarity(text1, text2)

        assert similarity < 0.3

    def test_similarity_empty(self):
        """Test similarity with empty texts"""
        assert text_similarity("", "") == 0.0
        assert text_similarity("text", "") == 0.0


class TestTextHashing:
    """Test text hashing for deduplication"""

    def test_generate_hash_consistency(self):
        """Test that same text produces same hash"""
        text = "Amazon workers union"
        hash1 = generate_text_hash(text)
        hash2 = generate_text_hash(text)

        assert hash1 == hash2

    def test_generate_hash_case_insensitive(self):
        """Test that hash is case-insensitive"""
        hash1 = generate_text_hash("Amazon Workers")
        hash2 = generate_text_hash("amazon workers")

        assert hash1 == hash2

    def test_generate_hash_different_texts(self):
        """Test that different texts produce different hashes"""
        hash1 = generate_text_hash("Amazon workers")
        hash2 = generate_text_hash("Tesla employees")

        assert hash1 != hash2


class TestDuplicateDetection:
    """Test duplicate detection"""

    def test_find_duplicates_exact(self):
        """Test finding exact duplicates"""
        texts = [
            "Amazon workers win union vote",
            "Tesla announces new factory",
            "Amazon workers win union vote"
        ]
        duplicates = find_duplicates(texts, threshold=0.95)

        assert len(duplicates) == 1
        assert {0, 2} in duplicates

    def test_find_duplicates_similar(self):
        """Test finding similar texts"""
        texts = [
            "Amazon workers win union vote",
            "Amazon employees secure union victory",
            "Tesla factory opens"
        ]
        duplicates = find_duplicates(texts, threshold=0.5)

        # Should find indices 0 and 1 as similar
        assert len(duplicates) >= 1


class TestTextTruncation:
    """Test text truncation"""

    def test_truncate_text_short(self):
        """Test truncating short text (no truncation needed)"""
        text = "Short text"
        result = truncate_text(text, max_length=100)
        assert result == "Short text"

    def test_truncate_text_long(self):
        """Test truncating long text"""
        text = "This is a very long text " * 20
        result = truncate_text(text, max_length=50)

        assert len(result) <= 53  # 50 + "..."
        assert result.endswith("...")

    def test_truncate_at_word_boundary(self):
        """Test that truncation happens at word boundaries"""
        text = "Amazon workers win union vote in historic victory"
        result = truncate_text(text, max_length=25)

        # Should truncate at word boundary
        assert not result.endswith("wor...")  # Shouldn't cut word in half


class TestKeywordMatching:
    """Test keyword matching"""

    def test_contains_keywords_any(self):
        """Test matching any keyword"""
        text = "Amazon workers win union vote"
        keywords = ["union", "strike", "workers"]

        assert contains_keywords(text, keywords, match_any=True)

    def test_contains_keywords_all(self):
        """Test matching all keywords"""
        text = "Amazon workers win union vote"
        keywords = ["workers", "union"]

        assert contains_keywords(text, keywords, match_any=False)

    def test_contains_keywords_missing(self):
        """Test when keywords are missing"""
        text = "Amazon workers win union vote"
        keywords = ["strike", "layoff"]

        assert not contains_keywords(text, keywords, match_any=True)


class TestCategorization:
    """Test automatic categorization"""

    def test_categorize_labor(self):
        """Test labor categorization"""
        text = "Amazon workers strike for better wages and union recognition"
        category = categorize_by_keywords(text)
        assert category == "labor"

    def test_categorize_tech(self):
        """Test tech categorization"""
        text = "New AI technology transforms software development"
        category = categorize_by_keywords(text)
        assert category == "tech"

    def test_categorize_politics(self):
        """Test politics categorization"""
        text = "Congress votes on new legislation affecting workers"
        category = categorize_by_keywords(text)
        assert category == "politics"

    def test_categorize_economics(self):
        """Test economics categorization"""
        text = "Inflation rises as Federal Reserve considers rate hikes"
        category = categorize_by_keywords(text)
        assert category == "economics"

    def test_categorize_default(self):
        """Test default category for uncategorizable text"""
        text = "Random text with no specific category keywords"
        category = categorize_by_keywords(text)
        assert category == "current-affairs"
