"""
The Daily Worker - Stripe Payment Integration Routes
Handles subscription checkout, webhooks, and payment method management
Phase 7.2: Stripe Payment Integration
"""

import os
import logging
import stripe
import json
from datetime import datetime, timezone
from typing import Optional
from enum import Enum

from fastapi import APIRouter, HTTPException, Request, Header, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db

logger = logging.getLogger(__name__)

# Configure Stripe API
stripe.api_key = os.getenv("STRIPE_SECRET_KEY") or "sk_test_placeholder"
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET") or "whsec_placeholder"
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY") or "pk_test_placeholder"

router = APIRouter()


# ============================================================
# MODELS & SCHEMAS
# ============================================================

class PlanType(str, Enum):
    """Subscription plan types"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"


class SubscriptionStatus(str, Enum):
    """Subscription status options"""
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    UNPAID = "unpaid"


class CheckoutRequest(BaseModel):
    """Request body for creating a checkout session"""
    plan_id: str = Field(..., description="Subscription plan ID: 'basic' or 'premium'")
    email: EmailStr = Field(..., description="User email address")
    success_url: Optional[str] = Field(
        default=None,
        description="URL to redirect after successful payment"
    )
    cancel_url: Optional[str] = Field(
        default=None,
        description="URL to redirect if user cancels"
    )


class CustomerPortalRequest(BaseModel):
    """Request body for creating a customer portal session"""
    customer_id: str = Field(..., description="Stripe customer ID")
    return_url: Optional[str] = Field(
        default=None,
        description="URL to return to after portal session"
    )


class CheckoutResponse(BaseModel):
    """Response from checkout session creation"""
    session_id: str
    session_url: str
    publishable_key: str


class PortalResponse(BaseModel):
    """Response from customer portal session creation"""
    portal_url: str


# ============================================================
# STRIPE CHECKOUT SESSION CREATION
# ============================================================

@router.post("/subscribe", response_model=CheckoutResponse)
async def create_checkout_session(
    request: CheckoutRequest,
    db: Session = Depends(get_db)
):
    """
    Create a Stripe Checkout session for subscription signup

    **Flow:**
    1. Validates plan_id (basic or premium)
    2. Creates or retrieves Stripe Customer by email
    3. Creates Stripe Checkout Session with subscription mode
    4. Returns session URL for redirect

    **Test Cards:**
    - Success: 4242 4242 4242 4242
    - Decline: 4000 0000 0000 0002
    - Auth Required: 4000 0025 0000 3155
    """
    # Map plan_id to Stripe Price ID
    # TODO: Replace with actual Stripe Price IDs from your Stripe Dashboard
    plan_mapping = {
        "basic": {
            "price_id": "price_basic_monthly",  # Replace with actual Stripe Price ID
            "name": "Basic Plan",
            "amount": 1500  # $15.00 in cents
        },
        "premium": {
            "price_id": "price_premium_monthly",  # Replace with actual Stripe Price ID
            "name": "Premium Plan",
            "amount": 2500  # $25.00 in cents
        }
    }

    if request.plan_id not in plan_mapping:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid plan_id. Must be one of: {', '.join(plan_mapping.keys())}"
        )

    try:

        plan = plan_mapping[request.plan_id]

        # Create or retrieve Stripe Customer
        customers = stripe.Customer.list(email=request.email, limit=1)

        if customers.data:
            customer = customers.data[0]
            logger.info(f"Found existing Stripe customer: {customer.id} for {request.email}")
        else:
            customer = stripe.Customer.create(
                email=request.email,
                metadata={
                    "source": "dailyworker_signup",
                    "plan": request.plan_id
                }
            )
            logger.info(f"Created new Stripe customer: {customer.id} for {request.email}")

        # Default URLs
        base_url = settings.get_base_url().replace(
            f":{settings.backend_port}",
            f":{settings.frontend_port}"
        )
        success_url = request.success_url or f"{base_url}/subscription-success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = request.cancel_url or f"{base_url}/subscription-cancel"

        # Create Checkout Session
        checkout_session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": plan["name"],
                        "description": f"Subscription to The Daily Worker - {plan['name']}"
                    },
                    "unit_amount": plan["amount"],
                    "recurring": {
                        "interval": "month"
                    }
                },
                "quantity": 1
            }],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "plan_id": request.plan_id,
                "customer_email": request.email
            },
            allow_promotion_codes=True,  # Allow discount codes
            billing_address_collection="auto",
            customer_update={
                "address": "auto",
                "name": "auto"
            }
        )

        logger.info(
            f"Created Stripe Checkout session {checkout_session.id} "
            f"for {request.email} ({request.plan_id} plan)"
        )

        return CheckoutResponse(
            session_id=checkout_session.id,
            session_url=checkout_session.url,
            publishable_key=STRIPE_PUBLISHABLE_KEY
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe API error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to create checkout session"
        )


# ============================================================
# CUSTOMER PORTAL SESSION
# ============================================================

@router.post("/customer-portal", response_model=PortalResponse)
async def create_customer_portal_session(
    request: CustomerPortalRequest
):
    """
    Create a Stripe Customer Portal session for managing subscription

    **Features:**
    - Update payment method
    - Cancel subscription
    - View invoice history
    - Download receipts

    **Usage:**
    Redirect user to returned portal_url
    """
    try:
        # Default return URL
        base_url = settings.get_base_url().replace(
            f":{settings.backend_port}",
            f":{settings.frontend_port}"
        )
        return_url = request.return_url or f"{base_url}/account/subscription"

        # Create portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=request.customer_id,
            return_url=return_url
        )

        logger.info(f"Created Customer Portal session for {request.customer_id}")

        return PortalResponse(portal_url=portal_session.url)

    except stripe.error.StripeError as e:
        logger.error(f"Stripe API error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating portal session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to create portal session"
        )


# ============================================================
# STRIPE WEBHOOK HANDLER
# ============================================================

@router.post("/webhooks/stripe")
async def handle_stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events

    **Events Handled:**
    - checkout.session.completed: User completed subscription signup
    - invoice.paid: Subscription payment succeeded
    - invoice.payment_failed: Payment failed
    - customer.subscription.updated: Subscription status changed
    - customer.subscription.deleted: Subscription canceled

    **Security:**
    - Verifies webhook signature using STRIPE_WEBHOOK_SECRET
    - Rejects unsigned or invalid webhooks
    """
    payload = await request.body()

    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=stripe_signature,
            secret=STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid webhook payload: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid webhook signature: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    data_object = event["data"]["object"]

    logger.info(f"Processing webhook event: {event_type} (ID: {event['id']})")

    try:
        # Handle different event types
        if event_type == "checkout.session.completed":
            await handle_checkout_completed(data_object, db)

        elif event_type == "invoice.paid":
            await handle_invoice_paid(data_object, db)

        elif event_type == "invoice.payment_failed":
            await handle_invoice_payment_failed(data_object, db)

        elif event_type == "customer.subscription.updated":
            await handle_subscription_updated(data_object, db)

        elif event_type == "customer.subscription.deleted":
            await handle_subscription_deleted(data_object, db)

        else:
            logger.info(f"Unhandled webhook event type: {event_type}")

        return JSONResponse(content={"status": "success"}, status_code=200)

    except Exception as e:
        logger.error(f"Error processing webhook {event_type}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Webhook processing failed: {str(e)}"
        )


# ============================================================
# WEBHOOK EVENT HANDLERS
# ============================================================

async def handle_checkout_completed(session: dict, db: Session):
    """Handle successful checkout completion"""
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")
    customer_email = session.get("customer_details", {}).get("email")

    logger.info(
        f"Checkout completed: customer={customer_id}, "
        f"subscription={subscription_id}, email={customer_email}"
    )

    # TODO: Update database
    # 1. Find or create user by email
    # 2. Create subscription record with stripe_subscription_id
    # 3. Update user.subscription_status = 'active'
    # 4. Log subscription_event

    # Placeholder implementation
    logger.info("Database update would happen here")


async def handle_invoice_paid(invoice: dict, db: Session):
    """Handle successful invoice payment"""
    subscription_id = invoice.get("subscription")
    customer_id = invoice.get("customer")
    customer_email = invoice.get("customer_email")
    amount_paid = invoice.get("amount_paid")
    billing_reason = invoice.get("billing_reason")  # 'subscription_cycle' for renewals

    logger.info(
        f"Invoice paid: subscription={subscription_id}, "
        f"customer={customer_id}, amount=${amount_paid/100:.2f}, reason={billing_reason}"
    )

    # Import email function
    from backend.routes.subscription_management import send_renewal_email

    # Update database
    conn = db
    cursor = conn.cursor() if hasattr(db, 'cursor') else None

    if cursor:
        try:
            # Find subscription
            cursor.execute("""
                SELECT id, user_id FROM subscriptions
                WHERE stripe_subscription_id = ?
            """, (subscription_id,))

            result = cursor.fetchone()

            if result:
                sub_id, user_id = result

                # Update subscription to active
                cursor.execute("""
                    UPDATE subscriptions
                    SET status = 'active', updated_at = ?
                    WHERE id = ?
                """, (datetime.now(timezone.utc), sub_id))

                # Update user status
                cursor.execute("""
                    UPDATE users
                    SET subscription_status = 'active', updated_at = ?
                    WHERE id = ?
                """, (datetime.now(timezone.utc), user_id))

                # Log event
                cursor.execute("""
                    INSERT INTO subscription_events
                    (subscription_id, user_id, event_type, event_data_json, created_at)
                    VALUES (?, ?, 'payment_succeeded', ?, ?)
                """, (
                    sub_id,
                    user_id,
                    json.dumps({"amount_cents": amount_paid, "billing_reason": billing_reason}),
                    datetime.now(timezone.utc)
                ))

                conn.commit()

                # Send renewal email (only for recurring payments, not initial subscription)
                if billing_reason == 'subscription_cycle' and customer_email:
                    # Get next billing date
                    next_billing = datetime.now(timezone.utc) + timedelta(days=30)
                    send_renewal_email(customer_email, amount_paid, next_billing.strftime('%Y-%m-%d'))

                logger.info(f"Updated subscription {subscription_id} payment successful")

        except Exception as e:
            logger.error(f"Error updating database for paid invoice: {e}", exc_info=True)
            conn.rollback()


async def handle_invoice_payment_failed(invoice: dict, db: Session):
    """
    Handle failed invoice payment with 3-day grace period

    Grace Period Logic:
    - Attempts 1-3: Status = 'past_due', access maintained
    - Attempt 4+: Status = 'unpaid', access revoked
    """
    subscription_id = invoice.get("subscription")
    customer_id = invoice.get("customer")
    customer_email = invoice.get("customer_email")
    attempt_count = invoice.get("attempt_count", 1)
    next_payment_attempt = invoice.get("next_payment_attempt")

    logger.warning(
        f"Invoice payment failed: subscription={subscription_id}, "
        f"customer={customer_id}, attempt={attempt_count}"
    )

    # Import email function
    from backend.routes.subscription_management import send_payment_failed_email

    # Determine status based on grace period
    if attempt_count >= 4:
        # Grace period expired - revoke access
        new_status = 'unpaid'
        logger.warning(f"Grace period expired for subscription {subscription_id}")
    else:
        # Still in grace period - maintain access
        new_status = 'past_due'
        logger.info(f"Subscription {subscription_id} in grace period (attempt {attempt_count}/3)")

    # Update database
    conn = db
    cursor = conn.cursor() if hasattr(db, 'cursor') else None

    if cursor:
        try:
            # Find subscription
            cursor.execute("""
                SELECT id, user_id FROM subscriptions
                WHERE stripe_subscription_id = ?
            """, (subscription_id,))

            result = cursor.fetchone()

            if result:
                sub_id, user_id = result

                # Update subscription status
                cursor.execute("""
                    UPDATE subscriptions
                    SET status = ?, updated_at = ?
                    WHERE id = ?
                """, (new_status, datetime.now(timezone.utc), sub_id))

                # Update user status
                cursor.execute("""
                    UPDATE users
                    SET subscription_status = ?, updated_at = ?
                    WHERE id = ?
                """, (new_status, datetime.now(timezone.utc), user_id))

                # Log event
                cursor.execute("""
                    INSERT INTO subscription_events
                    (subscription_id, user_id, event_type, event_data_json, created_at)
                    VALUES (?, ?, 'payment_failed', ?, ?)
                """, (
                    sub_id,
                    user_id,
                    json.dumps({"attempt_count": attempt_count, "status": new_status}),
                    datetime.now(timezone.utc)
                ))

                conn.commit()

                # Send notification email
                next_attempt_str = None
                if next_payment_attempt:
                    next_attempt_str = datetime.fromtimestamp(next_payment_attempt).strftime('%Y-%m-%d')

                if customer_email:
                    send_payment_failed_email(customer_email, attempt_count, next_attempt_str)

                logger.info(f"Updated subscription {subscription_id} to status: {new_status}")

        except Exception as e:
            logger.error(f"Error updating database for failed payment: {e}", exc_info=True)
            conn.rollback()


async def handle_subscription_updated(subscription: dict, db: Session):
    """Handle subscription status change"""
    subscription_id = subscription.get("id")
    status = subscription.get("status")

    logger.info(f"Subscription updated: {subscription_id} -> status={status}")

    # TODO: Update database
    # 1. Find subscription by stripe_subscription_id
    # 2. Update subscription.status
    # 3. Update subscription.current_period_start/end
    # 4. Update user.subscription_status
    # 5. Log subscription_event


async def handle_subscription_deleted(subscription: dict, db: Session):
    """Handle subscription cancellation"""
    subscription_id = subscription.get("id")
    customer_id = subscription.get("customer")

    logger.info(f"Subscription deleted: {subscription_id}, customer={customer_id}")

    # TODO: Update database
    # 1. Find subscription by stripe_subscription_id
    # 2. Update subscription.status = 'canceled'
    # 3. Update subscription.canceled_at
    # 4. Update user.subscription_status = 'canceled'
    # 5. Log subscription_event


# ============================================================
# UTILITY ENDPOINTS
# ============================================================

@router.get("/plans")
async def get_subscription_plans(db: Session = Depends(get_db)):
    """
    Get available subscription plans

    Returns plan details including pricing and features
    """
    # TODO: Query from database subscription_plans table
    # For now, return static data

    plans = [
        {
            "id": "free",
            "name": "Free",
            "price_cents": 0,
            "billing_interval": "monthly",
            "features": {
                "article_limit": 3,
                "archive_days": 5,
                "sports_leagues": 0,
                "local_news": False
            }
        },
        {
            "id": "basic",
            "name": "Basic",
            "price_cents": 1500,  # $15.00
            "billing_interval": "monthly",
            "features": {
                "article_limit": None,  # Unlimited
                "archive_days": 10,
                "sports_leagues": 1,
                "local_news": True
            }
        },
        {
            "id": "premium",
            "name": "Premium",
            "price_cents": 2500,  # $25.00
            "billing_interval": "monthly",
            "features": {
                "article_limit": None,  # Unlimited
                "archive_days": None,  # Full archive
                "sports_leagues": None,  # Unlimited
                "local_news": True
            }
        }
    ]

    return {"plans": plans}


@router.get("/config")
async def get_stripe_config():
    """
    Get Stripe publishable key for frontend

    **Security:** Only returns publishable key (safe for client-side)
    """
    return {
        "publishable_key": STRIPE_PUBLISHABLE_KEY,
        "country": "US",
        "currency": "usd"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@router.get("/health")
async def payments_health_check():
    """Health check for payment system"""
    try:
        # Test Stripe API connection
        stripe.Account.retrieve()

        return {
            "status": "healthy",
            "stripe_configured": bool(stripe.api_key),
            "webhook_configured": bool(STRIPE_WEBHOOK_SECRET)
        }
    except Exception as e:
        logger.error(f"Payment health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
