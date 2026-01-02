"""
Authentication API Routes
Handles user registration, login, logout, and token management
"""

import logging
import random
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from pydantic import BaseModel, EmailStr, validator
import sqlite3

from backend.config import settings
from backend.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    set_auth_cookies,
    clear_auth_cookies,
    get_current_user,
    require_user,
    decode_token
)
from backend.database import get_db, get_db_connection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str
    username: Optional[str] = None

    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

    @validator('username')
    def validate_username(cls, v):
        """Validate username format"""
        if v and len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """User information response"""
    id: int
    email: str
    username: Optional[str]
    role: str
    subscription_status: str
    subscriber_since: Optional[str]
    free_article_count: int
    created_at: str


# ============================================================
# STRIPE CUSTOMER CREATION (Integration with Phase 7.2)
# ============================================================

def create_stripe_customer(email: str, username: Optional[str] = None) -> Optional[str]:
    """
    Create a Stripe customer for the user

    Args:
        email: User's email address
        username: User's username (optional)

    Returns:
        Stripe customer ID or None if Stripe is not configured
    """
    # Check if Stripe is configured
    if not settings.stripe_secret_key:
        logger.warning("Stripe not configured, skipping customer creation")
        return None

    try:
        import stripe
        stripe.api_key = settings.stripe_secret_key

        # Create Stripe customer
        customer = stripe.Customer.create(
            email=email,
            name=username or email.split('@')[0],
            metadata={
                "source": "daily_worker_registration"
            }
        )

        logger.info(f"Created Stripe customer {customer.id} for {email}")
        return customer.id

    except Exception as e:
        logger.error(f"Failed to create Stripe customer for {email}: {e}")
        return None


# ============================================================
# A/B TEST ASSIGNMENT
# ============================================================

def assign_ab_test_group(user_id: int, conn: sqlite3.Connection) -> int:
    """
    Assign user to an A/B test group randomly

    Args:
        user_id: User ID
        conn: Database connection

    Returns:
        A/B test group ID
    """
    cursor = conn.cursor()

    # Get all active A/B test groups
    cursor.execute("""
        SELECT id FROM ab_test_groups WHERE is_active = 1
    """)
    groups = cursor.fetchall()

    if not groups:
        logger.warning("No active A/B test groups found")
        return None

    # Randomly assign to a group
    group_id = random.choice(groups)[0]

    # Insert assignment
    cursor.execute("""
        INSERT INTO user_ab_tests (user_id, test_group_id)
        VALUES (?, ?)
    """, (user_id, group_id))

    # Update user record
    cursor.execute("""
        UPDATE users SET ab_test_group_id = ? WHERE id = ?
    """, (group_id, user_id))

    conn.commit()

    logger.info(f"Assigned user {user_id} to A/B test group {group_id}")
    return group_id


# ============================================================
# AUTHENTICATION ENDPOINTS
# ============================================================

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, response: Response):
    """
    Register a new user

    - Creates user account with hashed password
    - Creates Stripe customer automatically
    - Assigns to A/B test group
    - Returns JWT access token and refresh token
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (request.email,))
        existing_user = cursor.fetchone()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Check if username is taken (if provided)
        if request.username:
            cursor.execute("SELECT id FROM users WHERE username = ?", (request.username,))
            existing_username = cursor.fetchone()

            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )

        # Hash password
        password_hash = get_password_hash(request.password)

        # Create Stripe customer
        stripe_customer_id = create_stripe_customer(request.email, request.username)

        # Create user
        cursor.execute("""
            INSERT INTO users (
                email, password_hash, username, role, subscription_status,
                free_article_count, stripe_customer_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.email,
            password_hash,
            request.username,
            'subscriber',
            'free',
            0,
            stripe_customer_id,
            datetime.utcnow(),
            datetime.utcnow()
        ))

        user_id = cursor.lastrowid

        # Assign to A/B test group
        ab_test_group_id = assign_ab_test_group(user_id, conn)

        conn.commit()

        logger.info(f"User registered: {request.email} (ID: {user_id})")

        # Create JWT tokens
        token_data = {
            "user_id": user_id,
            "email": request.email,
            "username": request.username,
            "role": "subscriber",
            "subscription_status": "free",
            "ab_test_group_id": ab_test_group_id
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"user_id": user_id})

        # Set cookies
        set_auth_cookies(response, access_token, refresh_token)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": request.email,
                "username": request.username,
                "role": "subscriber",
                "subscription_status": "free",
                "free_article_count": 0
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )
    finally:
        conn.close()


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, response: Response):
    """
    Login user

    - Verifies email and password
    - Returns JWT access token and refresh token
    - Sets httpOnly cookies
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get user by email
        cursor.execute("""
            SELECT id, email, password_hash, username, role, subscription_status,
                   subscriber_since, free_article_count, ab_test_group_id, created_at
            FROM users
            WHERE email = ?
        """, (request.email,))

        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Verify password
        if not verify_password(request.password, user[2]):  # password_hash is index 2
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Update last login
        cursor.execute("""
            UPDATE users SET last_login = ? WHERE id = ?
        """, (datetime.utcnow(), user[0]))
        conn.commit()

        logger.info(f"User logged in: {request.email} (ID: {user[0]})")

        # Create JWT tokens
        token_data = {
            "user_id": user[0],
            "email": user[1],
            "username": user[3],
            "role": user[4],
            "subscription_status": user[5],
            "ab_test_group_id": user[8]
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"user_id": user[0]})

        # Set cookies
        set_auth_cookies(response, access_token, refresh_token)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user[0],
                "email": user[1],
                "username": user[3],
                "role": user[4],
                "subscription_status": user[5],
                "subscriber_since": user[6],
                "free_article_count": user[7]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )
    finally:
        conn.close()


@router.post("/logout")
async def logout(response: Response, user: dict = Depends(require_user)):
    """
    Logout user

    - Clears authentication cookies
    - Invalidates session
    """
    clear_auth_cookies(response)

    logger.info(f"User logged out: {user.get('email')} (ID: {user.get('user_id')})")

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: dict = Depends(require_user)):
    """
    Get current user information

    - Returns user profile data
    - Requires authentication
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get fresh user data from database
        cursor.execute("""
            SELECT id, email, username, role, subscription_status, subscriber_since,
                   free_article_count, created_at
            FROM users
            WHERE id = ?
        """, (user['user_id'],))

        user_data = cursor.fetchone()

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return {
            "id": user_data[0],
            "email": user_data[1],
            "username": user_data[2],
            "role": user_data[3],
            "subscription_status": user_data[4],
            "subscriber_since": user_data[5],
            "free_article_count": user_data[6],
            "created_at": user_data[7]
        }

    finally:
        conn.close()


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: Request, response: Response):
    """
    Refresh access token using refresh token

    - Validates refresh token from cookie
    - Issues new access token and refresh token
    """
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )

    # Decode and validate refresh token
    try:
        payload = decode_token(refresh_token)

        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

    except HTTPException:
        raise

    # Get user from database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, email, username, role, subscription_status, ab_test_group_id
            FROM users
            WHERE id = ?
        """, (user_id,))

        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # Create new tokens
        token_data = {
            "user_id": user[0],
            "email": user[1],
            "username": user[2],
            "role": user[3],
            "subscription_status": user[4],
            "ab_test_group_id": user[5]
        }

        access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token({"user_id": user[0]})

        # Set new cookies
        set_auth_cookies(response, access_token, new_refresh_token)

        logger.info(f"Token refreshed for user {user[1]} (ID: {user[0]})")

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user[0],
                "email": user[1],
                "username": user[2],
                "role": user[3],
                "subscription_status": user[4]
            }
        }

    finally:
        conn.close()
