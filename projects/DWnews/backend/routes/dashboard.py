"""
The Daily Worker - Subscriber Dashboard API Routes
Handles subscription management, billing info, and user preferences
Phase 7.4: Subscriber Dashboard & User Preferences
"""

import os
import logging
import stripe
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
import sqlite3

from backend.config import settings
from backend.database import get_db_connection
from backend.auth import require_user

logger = logging.getLogger(__name__)

# Configure Stripe API
stripe.api_key = os.getenv("STRIPE_SECRET_KEY") or "sk_test_placeholder"

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


# ============================================================
# MODELS & SCHEMAS
# ============================================================

class SubscriptionDetails(BaseModel):
    """User subscription details response"""
    status: str  # free, active, canceled, past_due, trialing
    plan_name: str  # Free, Basic, Premium
    plan_id: str  # free, basic, premium
    price_cents: int
    billing_interval: Optional[str] = None  # monthly, yearly
    next_billing_date: Optional[str] = None
    next_billing_amount: Optional[int] = None
    payment_method_brand: Optional[str] = None  # visa, mastercard, etc.
    payment_method_last4: Optional[str] = None
    subscription_start_date: Optional[str] = None
    renewal_date: Optional[str] = None
    cancel_at_period_end: bool = False
    canceled_at: Optional[str] = None
    stripe_customer_id: Optional[str] = None


class Invoice(BaseModel):
    """Invoice information"""
    id: str
    amount_cents: int
    status: str
    created_at: str
    paid_at: Optional[str] = None
    invoice_url: Optional[str] = None
    invoice_pdf: Optional[str] = None


class InvoicesResponse(BaseModel):
    """List of user invoices"""
    invoices: List[Invoice]


class CustomerPortalRequest(BaseModel):
    """Request to generate Customer Portal session"""
    return_url: Optional[str] = None


class CustomerPortalResponse(BaseModel):
    """Customer Portal session URL"""
    portal_url: str


class UserPreferences(BaseModel):
    """User preferences response"""
    sports_leagues: List[int]  # List of league IDs
    local_region: Optional[str] = None


class UpdatePreferencesRequest(BaseModel):
    """Update user preferences request"""
    sports_leagues: Optional[List[int]] = None
    local_region: Optional[str] = None


class SportsLeague(BaseModel):
    """Sports league information"""
    id: int
    league_code: str
    name: str
    country: Optional[str] = None
    tier_requirement: str  # free, basic, premium


class SportsLeaguesResponse(BaseModel):
    """List of available sports leagues"""
    leagues: List[SportsLeague]


# ============================================================
# SUBSCRIPTION STATUS ENDPOINT
# ============================================================

@router.get("/subscription", response_model=SubscriptionDetails)
async def get_subscription_status(user: dict = Depends(require_user)):
    """
    Get user's subscription details

    Returns:
    - Current subscription status (free, active, canceled, past_due, trialing)
    - Plan details (name, price, billing interval)
    - Billing information (next billing date, amount, payment method)
    - Subscription dates (start date, renewal date)
    - Cancellation status
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        user_id = user['user_id']

        # Get user subscription status
        cursor.execute("""
            SELECT subscription_status, stripe_customer_id, subscriber_since
            FROM users
            WHERE id = ?
        """, (user_id,))

        user_data = cursor.fetchone()

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        subscription_status, stripe_customer_id, subscriber_since = user_data

        # Default response for free tier users
        if subscription_status == 'free' or not stripe_customer_id:
            return SubscriptionDetails(
                status='free',
                plan_name='Free',
                plan_id='free',
                price_cents=0,
                billing_interval=None,
                next_billing_date=None,
                next_billing_amount=None,
                payment_method_brand=None,
                payment_method_last4=None,
                subscription_start_date=None,
                renewal_date=None,
                cancel_at_period_end=False,
                canceled_at=None,
                stripe_customer_id=None
            )

        # Get active subscription from database
        cursor.execute("""
            SELECT
                s.id, s.stripe_subscription_id, s.status, s.current_period_start,
                s.current_period_end, s.cancel_at_period_end, s.canceled_at,
                sp.plan_name, sp.price_cents, sp.billing_interval
            FROM subscriptions s
            JOIN subscription_plans sp ON s.plan_id = sp.id
            WHERE s.user_id = ? AND s.status IN ('active', 'trialing', 'past_due', 'canceled')
            ORDER BY s.created_at DESC
            LIMIT 1
        """, (user_id,))

        subscription = cursor.fetchone()

        if not subscription:
            # User has stripe_customer_id but no active subscription
            return SubscriptionDetails(
                status='free',
                plan_name='Free',
                plan_id='free',
                price_cents=0,
                billing_interval=None,
                next_billing_date=None,
                next_billing_amount=None,
                payment_method_brand=None,
                payment_method_last4=None,
                subscription_start_date=None,
                renewal_date=None,
                cancel_at_period_end=False,
                canceled_at=None,
                stripe_customer_id=stripe_customer_id
            )

        (
            sub_id, stripe_sub_id, sub_status, period_start, period_end,
            cancel_at_period_end, canceled_at, plan_name, price_cents, billing_interval
        ) = subscription

        # Get payment method from Stripe
        payment_method_brand = None
        payment_method_last4 = None

        try:
            # Fetch default payment method from Stripe
            customer = stripe.Customer.retrieve(stripe_customer_id)

            if customer.invoice_settings and customer.invoice_settings.default_payment_method:
                payment_method_id = customer.invoice_settings.default_payment_method
                payment_method = stripe.PaymentMethod.retrieve(payment_method_id)

                if payment_method.card:
                    payment_method_brand = payment_method.card.brand
                    payment_method_last4 = payment_method.card.last4

        except stripe.error.StripeError as e:
            logger.warning(f"Failed to fetch payment method for customer {stripe_customer_id}: {e}")

        # Determine plan_id from plan_name
        plan_id_mapping = {
            'Free Tier': 'free',
            'Basic Subscriber': 'basic',
            'Premium Subscriber': 'premium'
        }
        plan_id = plan_id_mapping.get(plan_name, 'free')

        return SubscriptionDetails(
            status=sub_status,
            plan_name=plan_name,
            plan_id=plan_id,
            price_cents=price_cents,
            billing_interval=billing_interval,
            next_billing_date=period_end,
            next_billing_amount=price_cents if sub_status == 'active' else None,
            payment_method_brand=payment_method_brand,
            payment_method_last4=payment_method_last4,
            subscription_start_date=period_start,
            renewal_date=period_end,
            cancel_at_period_end=bool(cancel_at_period_end),
            canceled_at=canceled_at,
            stripe_customer_id=stripe_customer_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching subscription status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscription status"
        )
    finally:
        conn.close()


# ============================================================
# INVOICES ENDPOINT
# ============================================================

@router.get("/invoices", response_model=InvoicesResponse)
async def get_invoices(user: dict = Depends(require_user)):
    """
    Get user's invoice history from Stripe

    Returns list of invoices with download URLs
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        user_id = user['user_id']

        # Get user's Stripe customer ID
        cursor.execute("""
            SELECT stripe_customer_id
            FROM users
            WHERE id = ?
        """, (user_id,))

        result = cursor.fetchone()

        if not result or not result[0]:
            # No Stripe customer ID - return empty list
            return InvoicesResponse(invoices=[])

        stripe_customer_id = result[0]

        # Fetch invoices from Stripe
        try:
            stripe_invoices = stripe.Invoice.list(
                customer=stripe_customer_id,
                limit=100
            )

            invoices = []

            for inv in stripe_invoices.data:
                invoices.append(Invoice(
                    id=inv.id,
                    amount_cents=inv.amount_paid,
                    status=inv.status,
                    created_at=datetime.fromtimestamp(inv.created).isoformat(),
                    paid_at=datetime.fromtimestamp(inv.status_transitions.paid_at).isoformat() if inv.status_transitions.paid_at else None,
                    invoice_url=inv.hosted_invoice_url,
                    invoice_pdf=inv.invoice_pdf
                ))

            return InvoicesResponse(invoices=invoices)

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error fetching invoices: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to fetch invoices: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching invoices: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch invoices"
        )
    finally:
        conn.close()


# ============================================================
# CUSTOMER PORTAL ENDPOINT
# ============================================================

@router.post("/customer-portal", response_model=CustomerPortalResponse)
async def generate_customer_portal(
    request: CustomerPortalRequest,
    user: dict = Depends(require_user)
):
    """
    Generate Stripe Customer Portal session URL

    Allows users to:
    - Update payment method
    - View billing history
    - Download invoices
    - Cancel subscription (managed by Stripe)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        user_id = user['user_id']

        # Get user's Stripe customer ID
        cursor.execute("""
            SELECT stripe_customer_id
            FROM users
            WHERE id = ?
        """, (user_id,))

        result = cursor.fetchone()

        if not result or not result[0]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No Stripe customer found. Please subscribe first."
            )

        stripe_customer_id = result[0]

        # Default return URL
        base_url = settings.get_base_url().replace(
            f":{settings.backend_port}",
            f":{settings.frontend_port}"
        )
        return_url = request.return_url or f"{base_url}/account/subscription"

        # Create Customer Portal session
        try:
            portal_session = stripe.billing_portal.Session.create(
                customer=stripe_customer_id,
                return_url=return_url
            )

            logger.info(f"Created Customer Portal session for user {user_id}")

            return CustomerPortalResponse(portal_url=portal_session.url)

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating portal session: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create portal session: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating portal session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create portal session"
        )
    finally:
        conn.close()


# ============================================================
# USER PREFERENCES ENDPOINTS
# ============================================================

@router.get("/preferences", response_model=UserPreferences)
async def get_user_preferences(user: dict = Depends(require_user)):
    """
    Get user's preferences (sports leagues, local news region)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        user_id = user['user_id']

        # Get local region preference
        cursor.execute("""
            SELECT local_region
            FROM users
            WHERE id = ?
        """, (user_id,))

        result = cursor.fetchone()
        local_region = result[0] if result and result[0] else None

        # Get sports league preferences
        cursor.execute("""
            SELECT league_id
            FROM user_sports_preferences
            WHERE user_id = ? AND enabled = 1
        """, (user_id,))

        sports_leagues = [row[0] for row in cursor.fetchall()]

        return UserPreferences(
            sports_leagues=sports_leagues,
            local_region=local_region
        )

    except Exception as e:
        logger.error(f"Error fetching user preferences: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user preferences"
        )
    finally:
        conn.close()


@router.put("/preferences")
async def update_user_preferences(
    request: UpdatePreferencesRequest,
    user: dict = Depends(require_user)
):
    """
    Update user's preferences (sports leagues, local news region)

    Sports league restrictions:
    - Free tier: Cannot select any leagues
    - Basic tier: Can select 1 league
    - Premium tier: Unlimited leagues
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        user_id = user['user_id']
        subscription_status = user.get('subscription_status', 'free')

        # Update local region if provided
        if request.local_region is not None:
            cursor.execute("""
                UPDATE users
                SET local_region = ?, updated_at = ?
                WHERE id = ?
            """, (request.local_region, datetime.utcnow(), user_id))

        # Update sports leagues if provided
        if request.sports_leagues is not None:
            # Validate tier restrictions
            num_leagues = len(request.sports_leagues)

            if subscription_status == 'free' and num_leagues > 0:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Free tier users cannot select sports leagues. Please upgrade to Basic or Premium."
                )

            # Get user's actual subscription from database to check plan type
            cursor.execute("""
                SELECT sp.plan_name
                FROM subscriptions s
                JOIN subscription_plans sp ON s.plan_id = sp.id
                WHERE s.user_id = ? AND s.status = 'active'
                ORDER BY s.created_at DESC
                LIMIT 1
            """, (user_id,))

            plan_result = cursor.fetchone()
            plan_name = plan_result[0] if plan_result else 'Free Tier'

            # Basic tier: max 1 league
            if plan_name == 'Basic Subscriber' and num_leagues > 1:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Basic tier users can only select 1 sports league. Upgrade to Premium for unlimited leagues."
                )

            # Delete existing preferences
            cursor.execute("""
                DELETE FROM user_sports_preferences
                WHERE user_id = ?
            """, (user_id,))

            # Insert new preferences
            for league_id in request.sports_leagues:
                # Verify league exists
                cursor.execute("""
                    SELECT id FROM sports_leagues WHERE id = ?
                """, (league_id,))

                if not cursor.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid league ID: {league_id}"
                    )

                cursor.execute("""
                    INSERT INTO user_sports_preferences (user_id, league_id, enabled, created_at, updated_at)
                    VALUES (?, ?, 1, ?, ?)
                """, (user_id, league_id, datetime.utcnow(), datetime.utcnow()))

        conn.commit()

        logger.info(f"Updated preferences for user {user_id}")

        return {
            "message": "Preferences updated successfully",
            "sports_leagues": request.sports_leagues if request.sports_leagues is not None else [],
            "local_region": request.local_region
        }

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating user preferences: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user preferences"
        )
    finally:
        conn.close()


# ============================================================
# SPORTS LEAGUES ENDPOINT
# ============================================================

@router.get("/sports-leagues", response_model=SportsLeaguesResponse)
async def get_sports_leagues():
    """
    Get list of available sports leagues with tier requirements
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, league_code, name, country, tier_requirement
            FROM sports_leagues
            WHERE is_active = 1
            ORDER BY tier_requirement, name
        """)

        leagues = []

        for row in cursor.fetchall():
            leagues.append(SportsLeague(
                id=row[0],
                league_code=row[1],
                name=row[2],
                country=row[3],
                tier_requirement=row[4]
            ))

        return SportsLeaguesResponse(leagues=leagues)

    except Exception as e:
        logger.error(f"Error fetching sports leagues: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch sports leagues"
        )
    finally:
        conn.close()


# ============================================================
# SUBSCRIPTION CANCELLATION
# ============================================================

@router.post("/cancel-subscription")
async def cancel_subscription(user: dict = Depends(require_user)):
    """
    Cancel user's subscription (cancel at period end)

    The subscription will remain active until the end of the current billing period.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        user_id = user['user_id']

        # Get active subscription
        cursor.execute("""
            SELECT id, stripe_subscription_id
            FROM subscriptions
            WHERE user_id = ? AND status = 'active'
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id,))

        result = cursor.fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active subscription found"
            )

        subscription_id, stripe_subscription_id = result

        # Cancel subscription in Stripe
        try:
            stripe_subscription = stripe.Subscription.modify(
                stripe_subscription_id,
                cancel_at_period_end=True
            )

            # Update database
            cursor.execute("""
                UPDATE subscriptions
                SET cancel_at_period_end = 1, updated_at = ?
                WHERE id = ?
            """, (datetime.utcnow(), subscription_id))

            conn.commit()

            logger.info(f"Canceled subscription for user {user_id} (subscription_id: {subscription_id})")

            return {
                "message": "Subscription will be canceled at the end of the billing period",
                "cancel_at": stripe_subscription.current_period_end,
                "access_until": datetime.fromtimestamp(stripe_subscription.current_period_end).isoformat()
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error canceling subscription: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to cancel subscription: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Error canceling subscription: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )
    finally:
        conn.close()


# ============================================================
# HEALTH CHECK
# ============================================================

@router.get("/health")
async def dashboard_health_check():
    """Health check for dashboard API"""
    return {
        "status": "healthy",
        "service": "dashboard",
        "endpoints": [
            "/subscription",
            "/invoices",
            "/customer-portal",
            "/preferences",
            "/sports-leagues",
            "/cancel-subscription"
        ]
    }
