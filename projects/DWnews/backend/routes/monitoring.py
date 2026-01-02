"""
Monitoring API Routes

API endpoints for post-publication monitoring system:
- Social mention tracking
- Correction workflow
- Source reliability data
"""

from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict

from database import get_session
from database.models import Article, Correction, SourceReliabilityLog
from backend.agents.monitoring_agent import MonitoringAgent
from backend.agents.correction_workflow import CorrectionWorkflow
from backend.agents.source_reliability import SourceReliabilityScorer
from backend.auth import require_auth
from backend.logging_config import get_logger

logger = get_logger(__name__)

# Create Blueprint
monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')


@monitoring_bp.route('/mentions/<int:article_id>', methods=['GET'])
def get_article_mentions(article_id: int):
    """
    Get social media mentions for an article

    GET /api/monitoring/mentions/<article_id>

    Returns:
        JSON with list of mentions (Twitter, Reddit)
    """
    try:
        session = get_session()
        agent = MonitoringAgent(session)

        # Get article
        article = session.query(Article).filter(
            Article.id == article_id
        ).first()

        if not article:
            return jsonify({'error': 'Article not found'}), 404

        # Check social mentions
        mentions = agent.check_social_mentions(article)

        return jsonify({
            'article_id': article_id,
            'article_title': article.title,
            'total_mentions': len(mentions),
            'mentions': mentions
        })

    except Exception as e:
        logger.error(f"Error getting mentions for article {article_id}: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        session.close()


@monitoring_bp.route('/corrections/pending', methods=['GET'])
@require_auth
def get_pending_corrections():
    """
    Get all pending corrections awaiting review

    GET /api/monitoring/corrections/pending

    Requires authentication.

    Returns:
        JSON with list of pending corrections
    """
    try:
        session = get_session()
        workflow = CorrectionWorkflow(session)

        pending = workflow.get_pending_corrections()

        corrections_data = []
        for correction in pending:
            corrections_data.append({
                'id': correction.id,
                'article_id': correction.article_id,
                'article_title': correction.article.title,
                'correction_type': correction.correction_type,
                'severity': correction.severity,
                'incorrect_text': correction.incorrect_text,
                'correct_text': correction.correct_text,
                'description': correction.description,
                'section_affected': correction.section_affected,
                'reported_by': correction.reported_by,
                'reported_at': correction.reported_at.isoformat(),
                'status': correction.status
            })

        return jsonify({
            'total': len(corrections_data),
            'corrections': corrections_data
        })

    except Exception as e:
        logger.error(f"Error getting pending corrections: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        session.close()


@monitoring_bp.route('/corrections/<int:correction_id>', methods=['GET'])
@require_auth
def get_correction(correction_id: int):
    """
    Get details for a specific correction

    GET /api/monitoring/corrections/<correction_id>

    Requires authentication.

    Returns:
        JSON with correction details
    """
    try:
        session = get_session()

        correction = session.query(Correction).filter(
            Correction.id == correction_id
        ).first()

        if not correction:
            return jsonify({'error': 'Correction not found'}), 404

        return jsonify({
            'id': correction.id,
            'article_id': correction.article_id,
            'article_title': correction.article.title,
            'correction_type': correction.correction_type,
            'severity': correction.severity,
            'incorrect_text': correction.incorrect_text,
            'correct_text': correction.correct_text,
            'description': correction.description,
            'section_affected': correction.section_affected,
            'reported_by': correction.reported_by,
            'reported_at': correction.reported_at.isoformat(),
            'corrected_by': correction.corrected_by,
            'corrected_at': correction.corrected_at.isoformat() if correction.corrected_at else None,
            'public_notice': correction.public_notice,
            'status': correction.status,
            'is_published': correction.is_published
        })

    except Exception as e:
        logger.error(f"Error getting correction {correction_id}: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        session.close()


@monitoring_bp.route('/corrections/<int:correction_id>/review', methods=['POST'])
@require_auth
def review_correction(correction_id: int):
    """
    Review and approve/reject a correction

    POST /api/monitoring/corrections/<correction_id>/review
    {
        "action": "approve" or "reject",
        "reviewer": "editor_username",
        "notes": "Review notes (optional)"
    }

    Requires authentication.

    Returns:
        JSON with success status
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body required'}), 400

        action = data.get('action')
        reviewer = data.get('reviewer')
        notes = data.get('notes')

        if not action or action not in ['approve', 'reject']:
            return jsonify({'error': 'Invalid action (must be "approve" or "reject")'}), 400

        if not reviewer:
            return jsonify({'error': 'Reviewer required'}), 400

        session = get_session()
        workflow = CorrectionWorkflow(session)

        success = workflow.review_correction(
            correction_id=correction_id,
            action=action,
            reviewer=reviewer,
            notes=notes
        )

        if success:
            return jsonify({
                'success': True,
                'message': f"Correction {action}d successfully"
            })
        else:
            return jsonify({'error': 'Failed to review correction'}), 500

    except Exception as e:
        logger.error(f"Error reviewing correction {correction_id}: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        session.close()


@monitoring_bp.route('/corrections/<int:correction_id>/publish', methods=['POST'])
@require_auth
def publish_correction(correction_id: int):
    """
    Publish a verified correction

    POST /api/monitoring/corrections/<correction_id>/publish
    {
        "public_notice": "Public-facing correction notice",
        "editor": "editor_username",
        "update_content": true (optional)
    }

    Requires authentication.

    Returns:
        JSON with success status
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body required'}), 400

        public_notice = data.get('public_notice')
        editor = data.get('editor')
        update_content = data.get('update_content', False)

        if not public_notice:
            return jsonify({'error': 'Public notice required'}), 400

        if not editor:
            return jsonify({'error': 'Editor required'}), 400

        session = get_session()
        workflow = CorrectionWorkflow(session)

        # Publish correction
        success = workflow.publish_correction(
            correction_id=correction_id,
            public_notice=public_notice,
            editor=editor
        )

        if not success:
            return jsonify({'error': 'Failed to publish correction'}), 500

        # Optionally apply correction to article content
        if update_content:
            workflow.apply_correction_to_article(
                correction_id=correction_id,
                update_content=True
            )

        return jsonify({
            'success': True,
            'message': 'Correction published successfully'
        })

    except Exception as e:
        logger.error(f"Error publishing correction {correction_id}: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        session.close()


@monitoring_bp.route('/corrections/flag', methods=['POST'])
@require_auth
def flag_correction():
    """
    Flag a new correction for review

    POST /api/monitoring/corrections/flag
    {
        "article_id": 123,
        "correction_type": "factual_error",
        "incorrect_text": "Original text",
        "correct_text": "Corrected text",
        "description": "Explanation of error",
        "severity": "moderate",
        "section_affected": "body",
        "reported_by": "username"
    }

    Requires authentication.

    Returns:
        JSON with created correction ID
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body required'}), 400

        # Validate required fields
        required_fields = ['article_id', 'correction_type', 'incorrect_text', 'correct_text', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        session = get_session()
        workflow = CorrectionWorkflow(session)

        correction = workflow.flag_correction(
            article_id=data['article_id'],
            correction_type=data['correction_type'],
            incorrect_text=data['incorrect_text'],
            correct_text=data['correct_text'],
            description=data['description'],
            severity=data.get('severity', 'moderate'),
            section_affected=data.get('section_affected'),
            reported_by=data.get('reported_by', 'manual_report')
        )

        if correction:
            return jsonify({
                'success': True,
                'correction_id': correction.id,
                'message': 'Correction flagged successfully'
            }), 201
        else:
            return jsonify({'error': 'Failed to flag correction'}), 500

    except Exception as e:
        logger.error(f"Error flagging correction: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        session.close()


@monitoring_bp.route('/sources/<int:source_id>/stats', methods=['GET'])
def get_source_stats(source_id: int):
    """
    Get reliability statistics for a source

    GET /api/monitoring/sources/<source_id>/stats

    Returns:
        JSON with source reliability stats
    """
    try:
        session = get_session()
        scorer = SourceReliabilityScorer(session)

        stats = scorer.get_source_stats(source_id)

        if not stats:
            return jsonify({'error': 'Source not found'}), 404

        return jsonify(stats)

    except Exception as e:
        logger.error(f"Error getting source stats for {source_id}: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        session.close()


@monitoring_bp.route('/sources/<int:source_id>/history', methods=['GET'])
def get_source_history(source_id: int):
    """
    Get reliability log history for a source

    GET /api/monitoring/sources/<source_id>/history?limit=50

    Returns:
        JSON with source reliability log history
    """
    try:
        limit = request.args.get('limit', 50, type=int)

        session = get_session()
        scorer = SourceReliabilityScorer(session)

        history = scorer.get_source_history(source_id, limit=limit)

        history_data = []
        for entry in history:
            history_data.append({
                'id': entry.id,
                'event_type': entry.event_type,
                'reliability_delta': entry.reliability_delta,
                'previous_score': entry.previous_score,
                'new_score': entry.new_score,
                'article_id': entry.article_id,
                'notes': entry.notes,
                'automated': entry.automated_adjustment,
                'logged_at': entry.logged_at.isoformat()
            })

        return jsonify({
            'source_id': source_id,
            'total_events': len(history_data),
            'history': history_data
        })

    except Exception as e:
        logger.error(f"Error getting source history for {source_id}: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        session.close()


@monitoring_bp.route('/sources/trends', methods=['GET'])
def get_reliability_trends():
    """
    Get overall reliability trends across all sources

    GET /api/monitoring/sources/trends

    Returns:
        JSON with reliability trends
    """
    try:
        session = get_session()
        scorer = SourceReliabilityScorer(session)

        trends = scorer.get_reliability_trends()

        return jsonify(trends)

    except Exception as e:
        logger.error(f"Error getting reliability trends: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        session.close()


@monitoring_bp.route('/stats', methods=['GET'])
@require_auth
def get_monitoring_stats():
    """
    Get overall monitoring statistics

    GET /api/monitoring/stats

    Requires authentication.

    Returns:
        JSON with monitoring stats
    """
    try:
        session = get_session()
        workflow = CorrectionWorkflow(session)

        correction_stats = workflow.get_correction_stats()

        return jsonify({
            'corrections': correction_stats
        })

    except Exception as e:
        logger.error(f"Error getting monitoring stats: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        session.close()
