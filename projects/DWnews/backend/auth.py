"""
Authentication and Authorization for The Daily Worker
Supports JWT-based authentication for subscriber access control
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
import secrets

from backend.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Basic Auth (for admin dashboard)
security_basic = HTTPBasic()

# Bearer token auth (for JWT)
security_bearer = HTTPBearer(auto_error=False)

# JWT Configuration
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
JWT_REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 days


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token

    Args:
        data: Payload to encode in the token (user_id, email, subscription_status, etc.)
        expires_delta: Token expiration time (default: 7 days)

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=JWT_ALGORITHM)

    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create JWT refresh token

    Args:
        data: Payload to encode (typically just user_id)

    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=JWT_ALGORITHM)

    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_from_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
) -> Optional[Dict[str, Any]]:
    """
    Get current user from JWT token in Authorization header

    Args:
        credentials: Bearer token from request

    Returns:
        User data from token or None if no token
    """
    if credentials is None:
        return None

    token = credentials.credentials
    payload = decode_token(token)

    # Verify it's an access token
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def get_current_user_from_cookie(request: Request) -> Optional[Dict[str, Any]]:
    """
    Get current user from JWT token in httpOnly cookie

    Args:
        request: FastAPI request object

    Returns:
        User data from token or None if no token
    """
    token = request.cookies.get("access_token")

    if not token:
        return None

    # Remove "Bearer " prefix if present
    if token.startswith("Bearer "):
        token = token[7:]

    payload = decode_token(token)

    # Verify it's an access token
    if payload.get("type") != "access":
        return None

    return payload


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    request: Request = None
) -> Optional[Dict[str, Any]]:
    """
    Get current user from either Authorization header or cookie

    Tries both methods:
    1. Authorization: Bearer <token> header
    2. access_token cookie

    Returns:
        User data or None if not authenticated
    """
    # Try bearer token first
    if credentials:
        return get_current_user_from_token(credentials)

    # Fall back to cookie
    if request:
        return get_current_user_from_cookie(request)

    return None


def require_user(
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Require authenticated user (raise exception if not authenticated)

    Args:
        user: User data from get_current_user

    Returns:
        User data

    Raises:
        HTTPException: If not authenticated
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_subscriber(
    user: Dict[str, Any] = Depends(require_user)
) -> Dict[str, Any]:
    """
    Require active subscriber (raise exception if not subscribed)

    Args:
        user: User data from require_user

    Returns:
        User data

    Raises:
        HTTPException: If not an active subscriber
    """
    subscription_status = user.get("subscription_status", "free")

    if subscription_status not in ["active", "trialing"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active subscription required",
        )

    return user


def require_admin(
    user: Dict[str, Any] = Depends(require_user)
) -> Dict[str, Any]:
    """
    Require admin role (raise exception if not admin)

    Args:
        user: User data from require_user

    Returns:
        User data

    Raises:
        HTTPException: If not an admin
    """
    role = user.get("role", "subscriber")

    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return user


def authenticate_admin(credentials: HTTPBasicCredentials = Depends(security_basic)) -> str:
    """Authenticate admin user (HTTP Basic Auth for admin dashboard)"""

    # For local development, use simple username/password check
    # In production, this would check against a database
    correct_username = settings.admin_username
    correct_password = settings.admin_password

    if credentials.username != correct_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    # For local dev, use simple password check
    # In production, use verify_password with hashed password
    if settings.environment == "local":
        if credentials.password != correct_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )
    else:
        # Production: verify against hashed password
        if not verify_password(credentials.password, correct_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )

    return credentials.username


def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """
    Set JWT tokens as httpOnly cookies

    Args:
        response: FastAPI response object
        access_token: JWT access token
        refresh_token: JWT refresh token
    """
    # Set access token cookie (7 days)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,  # Prevent JavaScript access
        secure=settings.environment != "local",  # HTTPS only in production
        samesite="lax",  # CSRF protection
        max_age=JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
    )

    # Set refresh token cookie (30 days)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.environment != "local",
        samesite="lax",
        max_age=JWT_REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )


def clear_auth_cookies(response: Response):
    """
    Clear authentication cookies (logout)

    Args:
        response: FastAPI response object
    """
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
