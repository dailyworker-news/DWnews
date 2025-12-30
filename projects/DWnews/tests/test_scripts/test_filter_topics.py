"""
Tests for topic filtering
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.content.filter_topics import TopicFilter
from database.models import Topic, Category


class TestTopicFilter:
    """Test topic filtering logic"""

    def test_worker_relevance_high(self, db_session, sample_category):
        """Test high worker relevance detection"""
        topic = Topic(
            title="Amazon Workers Strike for Better Wages and Union Recognition",
            description="Workers demand better pay and working conditions",
            keywords="amazon,workers,strike,union,wages",
            category_id=sample_category.id,
            status="discovered"
        )
        db_session.add(topic)
        db_session.commit()

        filter_service = TopicFilter(db_session)
        result = filter_service.check_worker_relevance(topic)

        assert result['passed'] is True
        assert result['score'] > 0.5
        assert len(result['matched_keywords']) > 0

    def test_worker_relevance_low(self, db_session, sample_category):
        """Test low worker relevance detection"""
        topic = Topic(
            title="Celebrity News: Star Buys New Mansion",
            description="Hollywood star purchases luxury estate",
            keywords="celebrity,mansion,luxury",
            category_id=sample_category.id,
            status="discovered"
        )
        db_session.add(topic)
        db_session.commit()

        filter_service = TopicFilter(db_session)
        result = filter_service.check_worker_relevance(topic)

        assert result['passed'] is False
        assert result['score'] < 0.3

    def test_credibility_check_investigative(self, db_session, sample_category):
        """Test credibility for investigative sources"""
        topic = Topic(
            title="Corporate Misconduct Revealed",
            description="Investigation uncovers wrongdoing",
            discovered_from="RSS:ProPublica",
            category_id=sample_category.id,
            status="discovered"
        )
        db_session.add(topic)
        db_session.commit()

        filter_service = TopicFilter(db_session)
        result = filter_service.check_source_credibility(topic)

        assert result['score'] > 0.5

    def test_credibility_check_academic(self, db_session, sample_category):
        """Test credibility for academic content"""
        topic = Topic(
            title="University Study Shows Worker Exploitation",
            description="Research from Harvard University reveals...",
            keywords="study,research,university,data",
            category_id=sample_category.id,
            status="discovered"
        )
        db_session.add(topic)
        db_session.commit()

        filter_service = TopicFilter(db_session)
        result = filter_service.check_source_credibility(topic)

        assert result['academic_count'] > 0
        assert result['score'] > 0.5

    def test_engagement_potential_high(self, db_session, sample_category):
        """Test high engagement potential"""
        topic = Topic(
            title="Breaking: Major Labor Victory",
            description="Historic union win",
            engagement_score=8.5,
            category_id=sample_category.id,
            status="discovered"
        )
        db_session.add(topic)
        db_session.commit()

        filter_service = TopicFilter(db_session)
        result = filter_service.check_engagement_potential(topic)

        assert result['passed'] is True
        assert result['score'] > 0.3

    def test_filter_topic_pass(self, db_session, sample_category):
        """Test topic that should pass all filters"""
        topic = Topic(
            title="Amazon Workers Win Historic Union Vote After Three-Year Struggle",
            description="Workers at Amazon warehouse vote to unionize despite corporate opposition. Study shows widespread support.",
            keywords="amazon,workers,union,strike,labor,victory",
            discovered_from="RSS:ProPublica",
            engagement_score=7.0,
            category_id=sample_category.id,
            status="discovered"
        )
        db_session.add(topic)
        db_session.commit()

        filter_service = TopicFilter(db_session)
        passed = filter_service.filter_topic(topic, verbose=False)

        assert passed is True
        assert topic.status == "filtered"
        assert topic.worker_relevance_score > 0

    def test_filter_topic_reject(self, db_session, sample_category):
        """Test topic that should be rejected"""
        topic = Topic(
            title="Celebrity Gossip News",
            description="Latest celebrity news",
            keywords="celebrity,gossip",
            discovered_from="Social",
            engagement_score=1.0,
            category_id=sample_category.id,
            status="discovered"
        )
        db_session.add(topic)
        db_session.commit()

        filter_service = TopicFilter(db_session)
        passed = filter_service.filter_topic(topic, verbose=False)

        assert passed is False
        assert topic.status == "rejected"
        assert topic.rejection_reason is not None
