"""
Access Control API Routes
Handles article reading tracking, limits, and premium access control
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
import sqlite3

from backend.config import settings
from backend.auth import get_current_user, require_user, require_subscriber
from backend.database import get_db_connection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/access", tags=["access-control"])


# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class ArticleAccessRequest(BaseModel):
    """Request to track article read"""
    article_id: int
    read_duration_seconds: Optional[int] = 0
    session_id: Optional[str] = None


class ArticleAccessResponse(BaseModel):
    """Response for article access check"""
    can_access: bool
    reason: Optional[str] = None
    article_limit: Optional[int] = None
    articles_read_count: int
    remaining_articles: Optional[int] = None
    is_premium: bool = False
    subscription_required: bool = False
    preview_only: bool = False


class UserArticleStatsResponse(BaseModel):
    """User article consumption statistics"""
    total_articles_read: int
    articles_read_today: int
    articles_read_this_week: int
    articles_read_this_month: int
    article_limit_daily: Optional[int]
    article_limit_weekly: Optional[int]
    article_limit_monthly: Optional[int]
    limit_reset_at: Optional[str]
    subscription_status: str


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_user_ab_test_limits(user_id: int, conn: sqlite3.Connection) -> dict:
    """
    Get article limits for user based on A/B test group

    Args:
        user_id: User ID
        conn: Database connection

    Returns:
        Dict with daily, weekly, monthly limits (-1 for unlimited)
    """
    cursor = conn.cursor()

    # Get user's A/B test group and limits
    cursor.execute("""
        SELECT
            g.article_limit_daily,
            g.article_limit_weekly,
            g.article_limit_monthly,
            g.group_name
        FROM users u
        LEFT JOIN ab_test_groups g ON u.ab_test_group_id = g.id
        WHERE u.id = ?
    """, (user_id,))

    result = cursor.fetchone()

    if not result or not result[0]:
        # Default to no limit if no A/B test group assigned
        return {
            "daily": -1,
            "weekly": -1,
            "monthly": -1,
            "group_name": "no_group"
        }

    return {
        "daily": result[0],
        "weekly": result[1],
        "monthly": result[2],
        "group_name": result[3]
    }


def get_articles_read_count(user_id: int, period: str, conn: sqlite3.Connection) -> int:
    """
    Count articles read by user in a given period

    Args:
        user_id: User ID
        period: 'day', 'week', or 'month'
        conn: Database connection

    Returns:
        Number of articles read
    """
    cursor = conn.cursor()

    # Calculate time threshold
    now = datetime.utcnow()
    if period == "day":
        threshold = now - timedelta(days=1)
    elif period == "week":
        threshold = now - timedelta(weeks=1)
    elif period == "month":
        threshold = now - timedelta(days=30)
    else:
        raise ValueError(f"Invalid period: {period}")

    # Count articles read since threshold
    cursor.execute("""
        SELECT COUNT(DISTINCT article_id)
        FROM user_article_reads
        WHERE user_id = ? AND read_at >= ?
    """, (user_id, threshold))

    count = cursor.fetchone()[0]
    return count


def check_article_limit(user_id: int, subscription_status: str, conn: sqlite3.Connection) -> dict:
    """
    Check if user has reached their article limit

    Args:
        user_id: User ID
        subscription_status: User's subscription status
        conn: Database connection

    Returns:
        Dict with can_access, reason, and statistics
    """
    # Subscribers have unlimited access
    if subscription_status in ["active", "trialing"]:
        return {
            "can_access": True,
            "reason": "subscriber_unlimited_access",
            "articles_read_count": 0,
            "remaining_articles": -1
        }

    # Get user's A/B test limits
    limits = get_user_ab_test_limits(user_id, conn)

    # Count articles read
    articles_today = get_articles_read_count(user_id, "day", conn)
    articles_week = get_articles_read_count(user_id, "week", conn)
    articles_month = get_articles_read_count(user_id, "month", conn)

    # Check daily limit
    if limits["daily"] != -1 and articles_today >= limits["daily"]:
        return {
            "can_access": False,
            "reason": "daily_limit_reached",
            "article_limit": limits["daily"],
            "articles_read_count": articles_today,
            "remaining_articles": 0
        }

    # Check weekly limit
    if limits["weekly"] != -1 and articles_week >= limits["weekly"]:
        return {
            "can_access": False,
            "reason": "weekly_limit_reached",
            "article_limit": limits["weekly"],
            "articles_read_count": articles_week,
            "remaining_articles": 0
        }

    # Check monthly limit
    if limits["monthly"] != -1 and articles_month >= limits["monthly"]:
        return {
            "can_access": False,
            "reason": "monthly_limit_reached",
            "article_limit": limits["monthly"],
            "articles_read_count": articles_month,
            "remaining_articles": 0
        }

    # User has not reached limit
    # Calculate remaining articles (use most restrictive limit)
    remaining = -1  # Unlimited

    if limits["daily"] != -1:
        daily_remaining = limits["daily"] - articles_today
        remaining = daily_remaining if remaining == -1 else min(remaining, daily_remaining)

    if limits["weekly"] != -1:
        weekly_remaining = limits["weekly"] - articles_week
        remaining = weekly_remaining if remaining == -1 else min(remaining, weekly_remaining)

    if limits["monthly"] != -1:
        monthly_remaining = limits["monthly"] - articles_month
        remaining = monthly_remaining if remaining == -1 else min(remaining, monthly_remaining)

    return {
        "can_access": True,
        "reason": "limit_ok",
        "article_limit": limits.get("daily") or limits.get("weekly") or limits.get("monthly"),
        "articles_read_count": max(articles_today, articles_week, articles_month),
        "remaining_articles": remaining
    }


def is_article_premium(article_id: int, conn: sqlite3.Connection) -> bool:
    """
    Check if article is premium content

    Args:
        article_id: Article ID
        conn: Database connection

    Returns:
        True if article is premium, False otherwise
    """
    cursor = conn.cursor()

    cursor.execute("""
        SELECT is_premium FROM articles WHERE id = ?
    """, (article_id,))

    result = cursor.fetchone()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )

    return bool(result[0])


# ============================================================
# ACCESS CONTROL ENDPOINTS
# ============================================================

@router.post("/check-article/{article_id}", response_model=ArticleAccessResponse)
async def check_article_access(
    article_id: int,
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Check if user can access an article

    - For free users: Check article limits based on A/B test group
    - For subscribers: Unlimited access
    - For premium articles: Subscriber access only
    - Returns access status, reason, and statistics
    """
    conn = get_db_connection()

    try:
        # Check if article is premium
        is_premium = is_article_premium(article_id, conn)

        # Anonymous users: No access to premium, limited access to free
        if user is None:
            return {
                "can_access": not is_premium,
                "reason": "anonymous_user" if not is_premium else "login_required",
                "article_limit": None,
                "articles_read_count": 0,
                "remaining_articles": None,
                "is_premium": is_premium,
                "subscription_required": is_premium,
                "preview_only": True  # Show preview only
            }

        user_id = user.get("user_id")
        subscription_status = user.get("subscription_status", "free")

        # Premium articles require active subscription
        if is_premium and subscription_status not in ["active", "trialing"]:
            return {
                "can_access": False,
                "reason": "premium_article_subscription_required",
                "article_limit": None,
                "articles_read_count": 0,
                "remaining_articles": 0,
                "is_premium": True,
                "subscription_required": True,
                "preview_only": True
            }

        # Check article limits
        limit_check = check_article_limit(user_id, subscription_status, conn)

        return {
            "can_access": limit_check["can_access"],
            "reason": limit_check.get("reason"),
            "article_limit": limit_check.get("article_limit"),
            "articles_read_count": limit_check.get("articles_read_count", 0),
            "remaining_articles": limit_check.get("remaining_articles"),
            "is_premium": is_premium,
            "subscription_required": is_premium and subscription_status not in ["active", "trialing"],
            "preview_only": not limit_check["can_access"] or (is_premium and subscription_status not in ["active", "trialing"])
        }

    finally:
        conn.close()


@router.post("/track-read")
async def track_article_read(
    request: ArticleAccessRequest,
    user: dict = Depends(require_user)
):
    """
    Track article read by user

    - Records article consumption in user_article_reads table
    - Updates user's free_article_count
    - Prevents duplicate tracking (same user + article)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        user_id = user.get("user_id")

        # Check if article exists
        cursor.execute("SELECT id FROM articles WHERE id = ?", (request.article_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )

        # Check if user already read this article
        cursor.execute("""
            SELECT id FROM user_article_reads
            WHERE user_id = ? AND article_id = ?
        """, (user_id, request.article_id))

        existing_read = cursor.fetchone()

        if existing_read:
            # Already tracked, update read duration if provided
            if request.read_duration_seconds and request.read_duration_seconds > 0:
                cursor.execute("""
                    UPDATE user_article_reads
                    SET read_duration_seconds = ?, read_at = ?
                    WHERE id = ?
                """, (request.read_duration_seconds, datetime.utcnow(), existing_read[0]))
                conn.commit()

            return {
                "message": "Article read already tracked",
                "article_id": request.article_id,
                "already_tracked": True
            }

        # Insert new read record
        cursor.execute("""
            INSERT INTO user_article_reads (
                user_id, article_id, read_at, session_id, read_duration_seconds
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            request.article_id,
            datetime.utcnow(),
            request.session_id,
            request.read_duration_seconds or 0
        ))

        # Increment user's free_article_count if not a subscriber
        subscription_status = user.get("subscription_status", "free")
        if subscription_status not in ["active", "trialing"]:
            cursor.execute("""
                UPDATE users
                SET free_article_count = free_article_count + 1
                WHERE id = ?
            """, (user_id,))

        conn.commit()

        logger.info(f"Tracked article read: user {user_id}, article {request.article_id}")

        return {
            "message": "Article read tracked successfully",
            "article_id": request.article_id,
            "already_tracked": False
        }

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Error tracking article read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track article read"
        )
    finally:
        conn.close()


@router.get("/stats", response_model=UserArticleStatsResponse)
async def get_user_article_stats(user: dict = Depends(require_user)):
    """
    Get user's article consumption statistics

    - Total articles read
    - Articles read today/this week/this month
    - Article limits based on A/B test group
    - Next limit reset time
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        user_id = user.get("user_id")
        subscription_status = user.get("subscription_status", "free")

        # Get total articles read
        cursor.execute("""
            SELECT COUNT(DISTINCT article_id) FROM user_article_reads WHERE user_id = ?
        """, (user_id,))
        total_read = cursor.fetchone()[0]

        # Get articles read by period
        articles_today = get_articles_read_count(user_id, "day", conn)
        articles_week = get_articles_read_count(user_id, "week", conn)
        articles_month = get_articles_read_count(user_id, "month", conn)

        # Get A/B test limits
        limits = get_user_ab_test_limits(user_id, conn)

        # Calculate next reset time (daily reset at midnight UTC)
        now = datetime.utcnow()
        next_reset = datetime(now.year, now.month, now.day) + timedelta(days=1)

        return {
            "total_articles_read": total_read,
            "articles_read_today": articles_today,
            "articles_read_this_week": articles_week,
            "articles_read_this_month": articles_month,
            "article_limit_daily": limits.get("daily"),
            "article_limit_weekly": limits.get("weekly"),
            "article_limit_monthly": limits.get("monthly"),
            "limit_reset_at": next_reset.isoformat(),
            "subscription_status": subscription_status
        }

    finally:
        conn.close()


@router.get("/recent-reads")
async def get_recent_reads(
    limit: int = 10,
    user: dict = Depends(require_user)
):
    """
    Get user's recently read articles

    - Returns list of recently read articles with timestamps
    - Ordered by read_at descending (most recent first)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        user_id = user.get("user_id")

        cursor.execute("""
            SELECT
                r.article_id,
                r.read_at,
                r.read_duration_seconds,
                a.title,
                a.category,
                a.published_at
            FROM user_article_reads r
            JOIN articles a ON r.article_id = a.id
            WHERE r.user_id = ?
            ORDER BY r.read_at DESC
            LIMIT ?
        """, (user_id, limit))

        reads = cursor.fetchall()

        return {
            "recent_reads": [
                {
                    "article_id": row[0],
                    "read_at": row[1],
                    "read_duration_seconds": row[2],
                    "title": row[3],
                    "category": row[4],
                    "published_at": row[5]
                }
                for row in reads
            ]
        }

    finally:
        conn.close()
