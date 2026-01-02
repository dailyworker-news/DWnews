"""
The Daily Worker - Sports Preferences Routes
Phase 7.7: Sports Subscription Configuration
Handles sports league preferences and tier-based access control
"""

import logging
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
import sqlite3

from backend.config import settings
from backend.database import get_db_connection
from backend.auth import require_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sports", tags=["sports"])
admin_router = APIRouter(prefix="/api/admin/sports", tags=["sports_admin"])


# ============================================================
# MODELS & SCHEMAS
# ============================================================

class SportsLeagueResponse(BaseModel):
    """Response model for sports league"""
    id: int
    league_code: str
    name: str
    country: Optional[str] = None
    tier_requirement: str
    is_active: bool


class UserSportsPreferenceResponse(BaseModel):
    """Response model for user sports preference"""
    league_id: int
    league_code: str
    league_name: str
    enabled: bool


class UpdateSportsPreferencesRequest(BaseModel):
    """Request to update user's sports preferences"""
    league_ids: List[int] = Field(..., description="List of league IDs to enable")


class LeagueAccessCheckResponse(BaseModel):
    """Response for checking league access"""
    has_access: bool
    requires_upgrade: bool = False
    current_tier: str
    required_tier: Optional[str] = None


class CreateLeagueRequest(BaseModel):
    """Request to create a new sports league"""
    league_code: str = Field(..., min_length=2, max_length=20)
    name: str = Field(..., min_length=3, max_length=100)
    country: Optional[str] = None
    tier_requirement: str = Field(..., pattern="^(free|basic|premium)$")


class UpdateLeagueRequest(BaseModel):
    """Request to update a sports league"""
    name: Optional[str] = None
    country: Optional[str] = None
    tier_requirement: Optional[str] = Field(None, pattern="^(free|basic|premium)$")
    is_active: Optional[bool] = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_user_subscription_tier(user_id: int, conn: sqlite3.Connection) -> str:
    """Get user's subscription tier (free, basic, premium)"""
    cursor = conn.cursor()

    # Check if user has active subscription
    cursor.execute("""
        SELECT sp.features_json, u.subscription_status
        FROM users u
        LEFT JOIN subscriptions s ON s.user_id = u.id AND s.status = 'active'
        LEFT JOIN subscription_plans sp ON sp.id = s.plan_id
        WHERE u.id = ?
        LIMIT 1
    """, (user_id,))

    row = cursor.fetchone()

    if not row or not row[0]:
        return "free"

    features_json, subscription_status = row

    if subscription_status != 'active':
        return "free"

    # Parse features_json to determine tier
    try:
        features = json.loads(features_json)
        sports_access = features.get('sports_access', 'none')

        if sports_access == 'none':
            return "free"
        elif sports_access == 'one_league':
            return "basic"
        elif sports_access == 'unlimited':
            return "premium"
        else:
            return "free"
    except (json.JSONDecodeError, KeyError):
        return "free"


def can_access_league(user_tier: str, league_tier: str) -> bool:
    """Check if user tier can access league tier"""
    tier_hierarchy = {
        'free': 0,
        'basic': 1,
        'premium': 2
    }

    user_level = tier_hierarchy.get(user_tier, 0)
    league_level = tier_hierarchy.get(league_tier, 0)

    return user_level >= league_level


def get_max_league_selections(user_tier: str) -> int:
    """Get maximum number of league selections for user tier"""
    if user_tier == 'free':
        return 0
    elif user_tier == 'basic':
        return 1
    elif user_tier == 'premium':
        return 999  # Unlimited
    else:
        return 0


# ============================================================
# PUBLIC ENDPOINTS
# ============================================================

@router.get("/leagues", response_model=List[SportsLeagueResponse])
async def get_all_leagues():
    """Get all active sports leagues"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, league_code, name, country, tier_requirement, is_active
            FROM sports_leagues
            WHERE is_active = 1
            ORDER BY tier_requirement, name
        """)

        leagues = []
        for row in cursor.fetchall():
            leagues.append(SportsLeagueResponse(
                id=row[0],
                league_code=row[1],
                name=row[2],
                country=row[3],
                tier_requirement=row[4],
                is_active=bool(row[5])
            ))

        return leagues

    finally:
        conn.close()


@router.get("/preferences", response_model=List[UserSportsPreferenceResponse])
async def get_user_sports_preferences(current_user: dict = Depends(require_user)):
    """Get current user's sports preferences"""
    user_id = current_user['id']
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check user tier
        user_tier = get_user_subscription_tier(user_id, conn)

        if user_tier == 'free':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sports preferences require a Basic or Premium subscription"
            )

        # Get user's preferences
        cursor.execute("""
            SELECT
                usp.league_id,
                sl.league_code,
                sl.name,
                usp.enabled
            FROM user_sports_preferences usp
            JOIN sports_leagues sl ON sl.id = usp.league_id
            WHERE usp.user_id = ? AND sl.is_active = 1
            ORDER BY sl.name
        """, (user_id,))

        preferences = []
        for row in cursor.fetchall():
            preferences.append(UserSportsPreferenceResponse(
                league_id=row[0],
                league_code=row[1],
                league_name=row[2],
                enabled=bool(row[3])
            ))

        return preferences

    finally:
        conn.close()


@router.post("/preferences", status_code=status.HTTP_200_OK)
async def update_sports_preferences(
    request: UpdateSportsPreferencesRequest,
    current_user: dict = Depends(require_user)
):
    """Update user's sports preferences"""
    user_id = current_user['id']
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check user tier
        user_tier = get_user_subscription_tier(user_id, conn)

        if user_tier == 'free':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sports preferences require a Basic or Premium subscription"
            )

        # Check league selection limits
        max_selections = get_max_league_selections(user_tier)

        if len(request.league_ids) > max_selections:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{user_tier.capitalize()} tier allows selection of {max_selections} league(s). " +
                       f"Upgrade to Premium for unlimited leagues."
            )

        # Verify all leagues exist and are accessible
        if request.league_ids:
            placeholders = ','.join('?' * len(request.league_ids))
            cursor.execute(f"""
                SELECT id, league_code, tier_requirement
                FROM sports_leagues
                WHERE id IN ({placeholders}) AND is_active = 1
            """, request.league_ids)

            leagues = cursor.fetchall()

            if len(leagues) != len(request.league_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more invalid league IDs provided"
                )

            # Check access to each league
            for league in leagues:
                league_tier = league[2]
                if not can_access_league(user_tier, league_tier):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"League '{league[1]}' requires {league_tier} tier. " +
                               f"Your current tier: {user_tier}"
                    )

        # Delete existing preferences
        cursor.execute("DELETE FROM user_sports_preferences WHERE user_id = ?", (user_id,))

        # Insert new preferences
        for league_id in request.league_ids:
            cursor.execute("""
                INSERT INTO user_sports_preferences (user_id, league_id, enabled, created_at, updated_at)
                VALUES (?, ?, 1, ?, ?)
            """, (user_id, league_id, datetime.utcnow(), datetime.utcnow()))

        conn.commit()

        return {
            "message": "Sports preferences updated successfully",
            "selected_leagues": len(request.league_ids),
            "user_tier": user_tier
        }

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating sports preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update sports preferences"
        )
    finally:
        conn.close()


@router.get("/accessible", response_model=List[SportsLeagueResponse])
async def get_accessible_leagues(current_user: dict = Depends(require_user)):
    """Get leagues accessible to current user based on their tier"""
    user_id = current_user['id']
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        user_tier = get_user_subscription_tier(user_id, conn)

        if user_tier == 'free':
            # Free tier has no sports access
            return []

        # Get accessible leagues based on tier
        if user_tier == 'basic':
            # Basic tier: only basic leagues
            cursor.execute("""
                SELECT id, league_code, name, country, tier_requirement, is_active
                FROM sports_leagues
                WHERE tier_requirement = 'basic' AND is_active = 1
                ORDER BY name
            """)
        else:  # premium
            # Premium tier: all leagues
            cursor.execute("""
                SELECT id, league_code, name, country, tier_requirement, is_active
                FROM sports_leagues
                WHERE is_active = 1
                ORDER BY tier_requirement, name
            """)

        leagues = []
        for row in cursor.fetchall():
            leagues.append(SportsLeagueResponse(
                id=row[0],
                league_code=row[1],
                name=row[2],
                country=row[3],
                tier_requirement=row[4],
                is_active=bool(row[5])
            ))

        return leagues

    finally:
        conn.close()


@router.get("/check-access/{league_code}", response_model=LeagueAccessCheckResponse)
async def check_league_access(league_code: str, current_user: dict = Depends(require_user)):
    """Check if user has access to a specific league"""
    user_id = current_user['id']
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get league info
        cursor.execute("""
            SELECT tier_requirement
            FROM sports_leagues
            WHERE league_code = ? AND is_active = 1
        """, (league_code,))

        row = cursor.fetchone()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"League '{league_code}' not found"
            )

        league_tier = row[0]
        user_tier = get_user_subscription_tier(user_id, conn)
        has_access = can_access_league(user_tier, league_tier)

        return LeagueAccessCheckResponse(
            has_access=has_access,
            requires_upgrade=(not has_access),
            current_tier=user_tier,
            required_tier=league_tier if not has_access else None
        )

    finally:
        conn.close()


# ============================================================
# ADMIN ENDPOINTS
# ============================================================

@admin_router.post("/leagues", status_code=status.HTTP_201_CREATED, response_model=SportsLeagueResponse)
async def create_sports_league(request: CreateLeagueRequest, current_user: dict = Depends(require_user)):
    """Create a new sports league (admin only)"""
    if current_user.get('role') not in ['admin', 'editor']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or editor access required"
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO sports_leagues (league_code, name, country, tier_requirement, is_active, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
        """, (request.league_code, request.name, request.country, request.tier_requirement, datetime.utcnow()))

        league_id = cursor.lastrowid
        conn.commit()

        return SportsLeagueResponse(
            id=league_id,
            league_code=request.league_code,
            name=request.name,
            country=request.country,
            tier_requirement=request.tier_requirement,
            is_active=True
        )

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"League with code '{request.league_code}' already exists"
        )
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating sports league: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create sports league"
        )
    finally:
        conn.close()


@admin_router.put("/leagues/{league_id}", response_model=SportsLeagueResponse)
async def update_sports_league(
    league_id: int,
    request: UpdateLeagueRequest,
    current_user: dict = Depends(require_user)
):
    """Update a sports league (admin only)"""
    if current_user.get('role') not in ['admin', 'editor']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or editor access required"
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Build dynamic update query
        update_fields = []
        params = []

        if request.name is not None:
            update_fields.append("name = ?")
            params.append(request.name)

        if request.country is not None:
            update_fields.append("country = ?")
            params.append(request.country)

        if request.tier_requirement is not None:
            update_fields.append("tier_requirement = ?")
            params.append(request.tier_requirement)

        if request.is_active is not None:
            update_fields.append("is_active = ?")
            params.append(1 if request.is_active else 0)

        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        params.append(league_id)

        cursor.execute(f"""
            UPDATE sports_leagues
            SET {', '.join(update_fields)}
            WHERE id = ?
        """, params)

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"League with ID {league_id} not found"
            )

        conn.commit()

        # Fetch updated league
        cursor.execute("""
            SELECT id, league_code, name, country, tier_requirement, is_active
            FROM sports_leagues
            WHERE id = ?
        """, (league_id,))

        row = cursor.fetchone()

        return SportsLeagueResponse(
            id=row[0],
            league_code=row[1],
            name=row[2],
            country=row[3],
            tier_requirement=row[4],
            is_active=bool(row[5])
        )

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating sports league: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update sports league"
        )
    finally:
        conn.close()


@admin_router.delete("/leagues/{league_id}", status_code=status.HTTP_200_OK)
async def deactivate_sports_league(league_id: int, current_user: dict = Depends(require_user)):
    """Deactivate a sports league (soft delete, admin only)"""
    if current_user.get('role') not in ['admin', 'editor']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or editor access required"
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE sports_leagues
            SET is_active = 0
            WHERE id = ?
        """, (league_id,))

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"League with ID {league_id} not found"
            )

        conn.commit()

        return {"message": f"League {league_id} deactivated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deactivating sports league: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate sports league"
        )
    finally:
        conn.close()


@admin_router.get("/leagues", response_model=List[SportsLeagueResponse])
async def list_all_leagues_admin(current_user: dict = Depends(require_user)):
    """List all sports leagues including inactive (admin only)"""
    if current_user.get('role') not in ['admin', 'editor']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or editor access required"
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, league_code, name, country, tier_requirement, is_active
            FROM sports_leagues
            ORDER BY tier_requirement, name
        """)

        leagues = []
        for row in cursor.fetchall():
            leagues.append(SportsLeagueResponse(
                id=row[0],
                league_code=row[1],
                name=row[2],
                country=row[3],
                tier_requirement=row[4],
                is_active=bool(row[5])
            ))

        return leagues

    finally:
        conn.close()
