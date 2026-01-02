# Phase 7.3: Authentication & Access Control API Documentation

**Date:** 2026-01-02
**Status:** Complete
**Version:** 1.0

---

## Overview

Phase 7.3 implements JWT-based authentication, subscriber access control, A/B testing for article limits, and article preview mode. This document provides complete API reference for all authentication and access control endpoints.

---

## Authentication Endpoints

### POST /api/auth/register

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "username": "optional_username"
}
```

**Validation Rules:**
- `email`: Valid email format (required)
- `password`: Minimum 8 characters (required)
- `username`: Minimum 3 characters, alphanumeric + hyphens/underscores (optional)

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "optional_username",
    "role": "subscriber",
    "subscription_status": "free",
    "free_article_count": 0
  }
}
```

**Cookies Set:**
- `access_token`: JWT access token (httpOnly, 7-day expiry)
- `refresh_token`: JWT refresh token (httpOnly, 30-day expiry)

**Side Effects:**
1. Creates user in database with hashed password (bcrypt)
2. Creates Stripe customer (if Stripe configured)
3. Assigns user to random A/B test group
4. Stores assignment in `user_ab_tests` table

**Error Responses:**
- `400 Bad Request`: Email already registered or username taken
- `422 Validation Error`: Invalid email format or weak password

---

### POST /api/auth/login

Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "optional_username",
    "role": "subscriber",
    "subscription_status": "active",
    "subscriber_since": "2026-01-01T00:00:00",
    "free_article_count": 5
  }
}
```

**Side Effects:**
- Updates `last_login` timestamp in database

**Error Responses:**
- `401 Unauthorized`: Incorrect email or password

---

### POST /api/auth/logout

Logout user and clear authentication cookies.

**Authentication:** Required (Bearer token or cookie)

**Response (200 OK):**
```json
{
  "message": "Logged out successfully"
}
```

**Side Effects:**
- Deletes `access_token` and `refresh_token` cookies

**Error Responses:**
- `401 Unauthorized`: Not authenticated

---

### GET /api/auth/me

Get current authenticated user's information.

**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "testuser",
  "role": "subscriber",
  "subscription_status": "active",
  "subscriber_since": "2026-01-01T00:00:00",
  "free_article_count": 5,
  "created_at": "2026-01-01T00:00:00"
}
```

**Error Responses:**
- `401 Unauthorized`: Not authenticated
- `404 Not Found`: User record not found

---

### POST /api/auth/refresh

Refresh access token using refresh token from cookie.

**Authentication:** Refresh token required (from cookie)

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "testuser",
    "role": "subscriber",
    "subscription_status": "active"
  }
}
```

**Side Effects:**
- Issues new access_token and refresh_token
- Sets new cookies

**Error Responses:**
- `401 Unauthorized`: Invalid or expired refresh token

---

## Access Control Endpoints

### POST /api/access/check-article/{article_id}

Check if user can access an article.

**Authentication:** Optional (supports both authenticated and anonymous users)

**Path Parameters:**
- `article_id` (integer): Article ID to check

**Response (200 OK) - Subscriber:**
```json
{
  "can_access": true,
  "reason": "subscriber_unlimited_access",
  "article_limit": null,
  "articles_read_count": 0,
  "remaining_articles": -1,
  "is_premium": false,
  "subscription_required": false,
  "preview_only": false
}
```

**Response (200 OK) - Free User Within Limit:**
```json
{
  "can_access": true,
  "reason": "limit_ok",
  "article_limit": 2,
  "articles_read_count": 1,
  "remaining_articles": 1,
  "is_premium": false,
  "subscription_required": false,
  "preview_only": false
}
```

**Response (200 OK) - Free User Limit Reached:**
```json
{
  "can_access": false,
  "reason": "daily_limit_reached",
  "article_limit": 2,
  "articles_read_count": 2,
  "remaining_articles": 0,
  "is_premium": false,
  "subscription_required": false,
  "preview_only": true
}
```

**Response (200 OK) - Premium Article, Free User:**
```json
{
  "can_access": false,
  "reason": "premium_article_subscription_required",
  "article_limit": null,
  "articles_read_count": 0,
  "remaining_articles": 0,
  "is_premium": true,
  "subscription_required": true,
  "preview_only": true
}
```

**Response (200 OK) - Anonymous User:**
```json
{
  "can_access": true,
  "reason": "anonymous_user",
  "article_limit": null,
  "articles_read_count": 0,
  "remaining_articles": null,
  "is_premium": false,
  "subscription_required": false,
  "preview_only": true
}
```

**Error Responses:**
- `404 Not Found`: Article not found

---

### POST /api/access/track-read

Track article read by authenticated user.

**Authentication:** Required

**Request Body:**
```json
{
  "article_id": 123,
  "read_duration_seconds": 45,
  "session_id": "optional-session-uuid"
}
```

**Response (200 OK) - First Read:**
```json
{
  "message": "Article read tracked successfully",
  "article_id": 123,
  "already_tracked": false
}
```

**Response (200 OK) - Already Tracked:**
```json
{
  "message": "Article read already tracked",
  "article_id": 123,
  "already_tracked": true
}
```

**Side Effects:**
1. Inserts record in `user_article_reads` table (prevents duplicates with UNIQUE constraint)
2. Increments `free_article_count` for free users
3. Updates `read_duration_seconds` if article already tracked

**Error Responses:**
- `401 Unauthorized`: Not authenticated
- `404 Not Found`: Article not found
- `500 Internal Server Error`: Database error

---

### GET /api/access/stats

Get user's article consumption statistics.

**Authentication:** Required

**Response (200 OK):**
```json
{
  "total_articles_read": 15,
  "articles_read_today": 2,
  "articles_read_this_week": 8,
  "articles_read_this_month": 15,
  "article_limit_daily": 2,
  "article_limit_weekly": null,
  "article_limit_monthly": null,
  "limit_reset_at": "2026-01-03T00:00:00",
  "subscription_status": "free"
}
```

**Note:** Limits are based on user's A/B test group assignment.

**Error Responses:**
- `401 Unauthorized`: Not authenticated

---

### GET /api/access/recent-reads

Get user's recently read articles.

**Authentication:** Required

**Query Parameters:**
- `limit` (integer, default=10): Maximum number of articles to return

**Response (200 OK):**
```json
{
  "recent_reads": [
    {
      "article_id": 123,
      "read_at": "2026-01-02T14:30:00",
      "read_duration_seconds": 45,
      "title": "Article Title",
      "category": "Labor Issues",
      "published_at": "2026-01-02T10:00:00"
    }
  ]
}
```

**Error Responses:**
- `401 Unauthorized`: Not authenticated

---

## Modified Article Endpoints

### GET /api/articles/{article_id}

Get article with access control and preview mode support.

**Authentication:** Optional

**Path Parameters:**
- `article_id` (integer): Article ID

**Response (200 OK) - Subscriber:**
```json
{
  "id": 123,
  "title": "Article Title",
  "slug": "article-title",
  "body": "Full article content...",
  "summary": "Article summary",
  "is_premium": false,
  "preview_only": false,
  ... (other article fields)
}
```

**Response (200 OK) - Free User, Premium Article:**
```json
{
  "id": 123,
  "title": "Premium Article Title",
  "slug": "premium-article",
  "body": "First paragraph...\n\nSecond paragraph...\n\n[Content preview - Subscribe to read more]",
  "summary": "Article summary",
  "is_premium": true,
  "preview_only": true,
  ... (other article fields)
}
```

**Preview Mode Behavior:**
- If `preview_only=true`, body truncated to first 2 paragraphs
- Appends "[Content preview - Subscribe to read more]" to truncated body

**Error Responses:**
- `404 Not Found`: Article not found

---

## A/B Test Groups

### Default Groups (Seeded in Migration 004)

| Group Name | Daily Limit | Weekly Limit | Monthly Limit | Description |
|---|---|---|---|---|
| `control_no_limit` | Unlimited | Unlimited | Unlimited | Control group for baseline metrics |
| `test_2_per_day` | 2 | Unlimited | Unlimited | Test 2 articles/day limit |
| `test_5_per_day` | 5 | Unlimited | Unlimited | Test 5 articles/day limit |
| `test_3_per_week` | Unlimited | 3 | Unlimited | Test 3 articles/week limit |

**Assignment:**
- New users randomly assigned to one of the 4 active groups
- Assignment stored in `user_ab_tests` table
- User's group ID stored in `users.ab_test_group_id`

---

## JWT Token Format

### Access Token Payload

```json
{
  "user_id": 1,
  "email": "user@example.com",
  "username": "testuser",
  "role": "subscriber",
  "subscription_status": "active",
  "ab_test_group_id": 2,
  "type": "access",
  "exp": 1735862400
}
```

**Expiration:** 7 days (604800 seconds)

### Refresh Token Payload

```json
{
  "user_id": 1,
  "type": "refresh",
  "exp": 1738540800
}
```

**Expiration:** 30 days (2592000 seconds)

---

## Authentication Methods

Clients can authenticate using **either**:

1. **Authorization Header:**
   ```
   Authorization: Bearer <access_token>
   ```

2. **HttpOnly Cookie:**
   ```
   Cookie: access_token=Bearer <access_token>
   ```

**Recommendation:** Use cookies for web applications (automatic, more secure).

---

## Security Features

1. **Password Hashing:** Bcrypt with salt
2. **JWT Signing:** HS256 algorithm with SECRET_KEY
3. **HttpOnly Cookies:** Prevents JavaScript access (XSS protection)
4. **Secure Cookie Flag:** HTTPS-only in production
5. **SameSite Cookie Attribute:** CSRF protection
6. **Token Expiration:** Automatic invalidation after 7/30 days

---

## Error Response Format

All endpoints return errors in this format:

```json
{
  "detail": "Error message"
}
```

**Common HTTP Status Codes:**
- `200 OK`: Success
- `201 Created`: Resource created (registration)
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Authentication required or failed
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Validation Error`: Request validation failed
- `500 Internal Server Error`: Server error

---

## Database Schema

### user_article_reads
Tracks article consumption per authenticated user.

| Column | Type | Description |
|---|---|---|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to users |
| article_id | INTEGER | Foreign key to articles |
| read_at | TIMESTAMP | When article was read |
| session_id | TEXT | Optional session ID |
| read_duration_seconds | INTEGER | Time spent reading |

**Constraints:**
- UNIQUE(user_id, article_id) - Prevents duplicate reads

### ab_test_groups
A/B test configuration.

| Column | Type | Description |
|---|---|---|
| id | INTEGER | Primary key |
| group_name | TEXT | Unique group name |
| description | TEXT | Group description |
| article_limit_daily | INTEGER | Daily article limit (-1 = unlimited) |
| article_limit_weekly | INTEGER | Weekly article limit |
| article_limit_monthly | INTEGER | Monthly article limit |
| is_active | BOOLEAN | Group active status |

### user_ab_tests
User A/B test assignments.

| Column | Type | Description |
|---|---|---|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to users |
| test_group_id | INTEGER | Foreign key to ab_test_groups |
| assigned_at | TIMESTAMP | Assignment timestamp |
| converted_to_paid | BOOLEAN | Conversion status |
| converted_at | TIMESTAMP | Conversion timestamp |

**Constraints:**
- UNIQUE(user_id) - One group per user

---

## Testing

Run test suite:
```bash
pytest backend/tests/test_auth_access_control.py -v
```

**Test Coverage:**
- User authentication (registration, login, logout)
- JWT token generation and validation
- Access control and article limits
- A/B test assignment
- Article preview mode
- Stripe integration

---

## Frontend Integration

### Example: Registration Flow

```javascript
// Register new user
const response = await fetch('/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'securepass123',
    username: 'newuser'
  }),
  credentials: 'include' // Important: Include cookies
});

const data = await response.json();
// Cookies automatically set by browser
// data.access_token available for header-based auth if needed
```

### Example: Check Article Access

```javascript
// Check if user can access article
const response = await fetch('/api/access/check-article/123', {
  method: 'POST',
  credentials: 'include' // Include auth cookies
});

const access = await response.json();

if (!access.can_access) {
  // Show upgrade prompt
  showPaywall(access.reason);
} else {
  // Load full article
  loadArticle(123);
}
```

---

## Production Deployment Checklist

- [ ] Set secure `SECRET_KEY` in environment (not default)
- [ ] Configure `STRIPE_SECRET_KEY` for customer creation
- [ ] Enable HTTPS for secure cookies
- [ ] Set `ENVIRONMENT=production` for password validation
- [ ] Configure CORS to restrict allowed origins
- [ ] Set up database backups
- [ ] Monitor JWT token usage and expiration
- [ ] Test A/B test metrics collection

---

**End of Documentation**
