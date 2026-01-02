"""
The Daily Worker - Subscription Management Routes
Phase 7.5: Subscription Management
Handles cancellation, pause, reactivation, and email notifications
"""

import os
import logging
import stripe
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
import sqlite3

from backend.config import settings
from backend.database import get_db_connection
from backend.auth import require_user

logger = logging.getLogger(__name__)

# Configure Stripe API
stripe.api_key = os.getenv("STRIPE_SECRET_KEY") or "sk_test_placeholder"

router = APIRouter(prefix="/api/dashboard", tags=["subscription_management"])

# Configuration
GRACE_PERIOD_DAYS = 3  # Days before access is revoked after payment failure


# ============================================================
# MODELS & SCHEMAS
# ============================================================

class PauseSubscriptionRequest(BaseModel):
    """Request to pause subscription"""
    pause_months: int = Field(..., ge=1, le=3, description="Number of months to pause (1-3)")


class ResubscribeRequest(BaseModel):
    """Request to resubscribe after cancellation"""
    plan_id: str = Field(..., description="Subscription plan ID: 'basic' or 'premium'")


class CancellationResponse(BaseModel):
    """Response for subscription cancellation"""
    message: str
    cancel_at: Optional[int] = None
    access_until: Optional[str] = None
    canceled_at: Optional[str] = None


class PauseResponse(BaseModel):
    """Response for subscription pause"""
    message: str
    resumes_at: str
    pause_duration_months: int


class ReactivationResponse(BaseModel):
    """Response for subscription reactivation"""
    message: str
    status: str


# ============================================================
# EMAIL NOTIFICATION SERVICE
# ============================================================

def send_email(to_email: str, subject: str, body: str, template: str = "default"):
    """
    Send email notification (stub for Phase 7.6)

    In Phase 7.6, this will integrate with SendGrid or similar service
    For now, it logs the email that would be sent
    """
    logger.info(f"[EMAIL] To: {to_email}")
    logger.info(f"[EMAIL] Subject: {subject}")
    logger.info(f"[EMAIL] Template: {template}")
    logger.info(f"[EMAIL] Body: {body}")

    # TODO Phase 7.6: Implement actual email sending
    # import sendgrid
    # sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    # ...


def send_cancellation_email(user_email: str, access_until: str):
    """Send subscription cancellation confirmation email"""
    subject = "Subscription Cancellation Confirmed - The Daily Worker"
    body = f"""
    Your subscription to The Daily Worker has been scheduled for cancellation.

    You will continue to have access to all subscriber benefits until {access_until}.

    If you change your mind, you can reactivate your subscription at any time before then.

    We're sorry to see you go!

    Best regards,
    The Daily Worker Team
    """
    send_email(user_email, subject, body, template="cancellation")


def send_immediate_cancellation_email(user_email: str):
    """Send immediate cancellation confirmation email"""
    subject = "Subscription Canceled - The Daily Worker"
    body = """
    Your subscription to The Daily Worker has been canceled immediately.

    Your access to subscriber-only content has ended. You can still read up to 3 free articles per month.

    To resubscribe at any time, visit your account dashboard.

    Thank you for your support!

    Best regards,
    The Daily Worker Team
    """
    send_email(user_email, subject, body, template="immediate_cancellation")


def send_pause_email(user_email: str, resumes_at: str, pause_months: int):
    """Send subscription pause confirmation email"""
    subject = "Subscription Paused - The Daily Worker"
    body = f"""
    Your subscription to The Daily Worker has been paused for {pause_months} month(s).

    Your subscription will automatically resume on {resumes_at}.

    During the pause period, you will not be charged, and you will have access to the free tier (3 articles per month).

    You can resume your subscription early at any time from your account dashboard.

    Best regards,
    The Daily Worker Team
    """
    send_email(user_email, subject, body, template="pause")


def send_reactivation_email(user_email: str):
    """Send subscription reactivation confirmation email"""
    subject = "Subscription Reactivated - The Daily Worker"
    body = """
    Great news! Your subscription to The Daily Worker has been reactivated.

    You now have full access to all subscriber benefits again, including:
    - Unlimited articles
    - Sports coverage
    - Archive access

    Thank you for staying with us!

    Best regards,
    The Daily Worker Team
    """
    send_email(user_email, subject, body, template="reactivation")


def send_payment_failed_email(user_email: str, attempt_count: int, next_attempt_date: Optional[str]):
    """Send payment failure notification email"""
    subject = "Payment Failed - The Daily Worker"

    if attempt_count < 4:
        body = f"""
        We were unable to process your subscription payment.

        Attempt {attempt_count} of 4

        Your subscription is currently in a grace period. You still have access to all subscriber benefits.

        Next payment attempt: {next_attempt_date or 'Soon'}

        Please update your payment method to avoid service interruption:
        [Visit Account Dashboard]

        Best regards,
        The Daily Worker Team
        """
    else:
        body = """
        We were unable to process your subscription payment after multiple attempts.

        Your subscription has been canceled due to non-payment.

        To restore your access, please update your payment method and resubscribe.

        Best regards,
        The Daily Worker Team
        """

    send_email(user_email, subject, body, template="payment_failed")


def send_renewal_email(user_email: str, amount_cents: int, next_billing_date: str):
    """Send subscription renewal confirmation email"""
    subject = "Subscription Renewed - The Daily Worker"
    amount_dollars = amount_cents / 100
    body = f"""
    Your subscription to The Daily Worker has been successfully renewed.

    Amount charged: ${amount_dollars:.2f}
    Next billing date: {next_billing_date}

    Thank you for your continued support!

    Best regards,
    The Daily Worker Team
    """
    send_email(user_email, subject, body, template="renewal")


# ============================================================
# IMMEDIATE CANCELLATION
# ============================================================

@router.post("/cancel-subscription-immediately", response_model=CancellationResponse)
async def cancel_subscription_immediately(user: dict = Depends(require_user)):
    """
    Cancel subscription immediately (revoke access now)

    Unlike cancel-at-period-end, this cancels the subscription right away
    and the user loses access immediately.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        user_id = user['user_id']
        user_email = user['email']

        # Get active subscription
        cursor.execute("""
            SELECT id, stripe_subscription_id
            FROM subscriptions
            WHERE user_id = ? AND status IN ('active', 'trialing', 'past_due')
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

        # Cancel subscription in Stripe immediately
        try:
            canceled_subscription = stripe.Subscription.delete(stripe_subscription_id)

            canceled_at = datetime.utcnow()

            # Update database
            cursor.execute("""
                UPDATE subscriptions
                SET status = 'canceled',
                    canceled_at = ?,
                    cancel_at_period_end = 0,
                    updated_at = ?
                WHERE id = ?
            """, (canceled_at, canceled_at, subscription_id))

            # Update user status
            cursor.execute("""
                UPDATE users
                SET subscription_status = 'canceled',
                    updated_at = ?
                WHERE id = ?
            """, (canceled_at, user_id))

            # Log event
            cursor.execute("""
                INSERT INTO subscription_events (subscription_id, user_id, event_type, event_data_json, created_at)
                VALUES (?, ?, 'subscription_canceled_immediately', '{}', ?)
            """, (subscription_id, user_id, canceled_at))

            conn.commit()

            # Send confirmation email
            send_immediate_cancellation_email(user_email)

            logger.info(f"Immediately canceled subscription for user {user_id}")

            return CancellationResponse(
                message="Subscription canceled immediately. Your access has ended.",
                canceled_at=canceled_at.isoformat()
            )

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
        logger.error(f"Error canceling subscription immediately: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )
    finally:
        conn.close()


# ============================================================
# SUBSCRIPTION PAUSE
# ============================================================

@router.post("/pause-subscription", response_model=PauseResponse)
async def pause_subscription(
    request: PauseSubscriptionRequest,
    user: dict = Depends(require_user)
):
    """
    Pause subscription for 1-3 months

    During the pause:
    - No billing occurs
    - Access reverts to free tier
    - Subscription automatically resumes after pause period
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        user_id = user['user_id']
        user_email = user['email']

        # Validate pause duration
        if request.pause_months < 1 or request.pause_months > 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pause duration must be between 1-3 months"
            )

        # Get active subscription
        cursor.execute("""
            SELECT id, stripe_subscription_id, status
            FROM subscriptions
            WHERE user_id = ? AND status IN ('active', 'trialing')
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id,))

        result = cursor.fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active subscription found"
            )

        subscription_id, stripe_subscription_id, current_status = result

        if current_status == 'paused':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription is already paused"
            )

        # Calculate resume date
        pause_days = request.pause_months * 30
        resume_date = datetime.utcnow() + timedelta(days=pause_days)
        resume_timestamp = int(resume_date.timestamp())

        # Pause subscription in Stripe
        try:
            paused_subscription = stripe.Subscription.modify(
                stripe_subscription_id,
                pause_collection={
                    'behavior': 'void',  # Don't charge during pause
                    'resumes_at': resume_timestamp
                }
            )

            # Update database
            cursor.execute("""
                UPDATE subscriptions
                SET status = 'paused',
                    updated_at = ?
                WHERE id = ?
            """, (datetime.utcnow(), subscription_id))

            # Update user status
            cursor.execute("""
                UPDATE users
                SET subscription_status = 'paused',
                    updated_at = ?
                WHERE id = ?
            """, (datetime.utcnow(), user_id))

            # Log event
            cursor.execute("""
                INSERT INTO subscription_events (subscription_id, user_id, event_type, event_data_json, created_at)
                VALUES (?, ?, 'subscription_paused', ?, ?)
            """, (
                subscription_id,
                user_id,
                f'{{"pause_months": {request.pause_months}, "resumes_at": "{resume_date.isoformat()}"}}',
                datetime.utcnow()
            ))

            conn.commit()

            # Send confirmation email
            send_pause_email(user_email, resume_date.strftime('%Y-%m-%d'), request.pause_months)

            logger.info(f"Paused subscription for user {user_id} for {request.pause_months} months")

            return PauseResponse(
                message=f"Subscription paused for {request.pause_months} month(s)",
                resumes_at=resume_date.isoformat(),
                pause_duration_months=request.pause_months
            )

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error pausing subscription: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to pause subscription: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Error pausing subscription: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to pause subscription"
        )
    finally:
        conn.close()


# ============================================================
# SUBSCRIPTION REACTIVATION
# ============================================================

@router.post("/reactivate-subscription", response_model=ReactivationResponse)
async def reactivate_subscription(user: dict = Depends(require_user)):
    """
    Reactivate a canceled or paused subscription

    This can:
    - Resume a paused subscription
    - Undo a scheduled cancellation (cancel_at_period_end)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        user_id = user['user_id']
        user_email = user['email']

        # Get subscription
        cursor.execute("""
            SELECT id, stripe_subscription_id, status, cancel_at_period_end
            FROM subscriptions
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id,))

        result = cursor.fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No subscription found"
            )

        subscription_id, stripe_subscription_id, current_status, cancel_at_period_end = result

        # Check if subscription is already active
        if current_status == 'active' and not cancel_at_period_end:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription is already active"
            )

        try:
            # Determine what type of reactivation is needed
            if current_status == 'paused':
                # Resume paused subscription
                reactivated_subscription = stripe.Subscription.modify(
                    stripe_subscription_id,
                    pause_collection=''  # Remove pause
                )
                message = "Subscription resumed successfully"
            elif cancel_at_period_end:
                # Undo scheduled cancellation
                reactivated_subscription = stripe.Subscription.modify(
                    stripe_subscription_id,
                    cancel_at_period_end=False
                )
                message = "Scheduled cancellation has been reversed"
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot reactivate subscription with status: {current_status}"
                )

            # Update database
            cursor.execute("""
                UPDATE subscriptions
                SET status = 'active',
                    cancel_at_period_end = 0,
                    canceled_at = NULL,
                    updated_at = ?
                WHERE id = ?
            """, (datetime.utcnow(), subscription_id))

            # Update user status
            cursor.execute("""
                UPDATE users
                SET subscription_status = 'active',
                    updated_at = ?
                WHERE id = ?
            """, (datetime.utcnow(), user_id))

            # Log event
            cursor.execute("""
                INSERT INTO subscription_events (subscription_id, user_id, event_type, event_data_json, created_at)
                VALUES (?, ?, 'subscription_reactivated', '{}', ?)
            """, (subscription_id, user_id, datetime.utcnow()))

            conn.commit()

            # Send confirmation email
            send_reactivation_email(user_email)

            logger.info(f"Reactivated subscription for user {user_id}")

            return ReactivationResponse(
                message=message,
                status='active'
            )

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error reactivating subscription: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to reactivate subscription: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Error reactivating subscription: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reactivate subscription"
        )
    finally:
        conn.close()


# ============================================================
# RESUBSCRIBE (NEW SUBSCRIPTION AFTER COMPLETE CANCELLATION)
# ============================================================

@router.post("/resubscribe")
async def resubscribe(
    request: ResubscribeRequest,
    user: dict = Depends(require_user)
):
    """
    Create a new subscription after complete cancellation

    This creates a new Stripe Checkout session for users who:
    - Had a subscription that was completely canceled
    - Want to subscribe again
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        user_id = user['user_id']
        user_email = user['email']

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
                detail="No Stripe customer found. Please contact support."
            )

        stripe_customer_id = result[0]

        # Map plan_id to price
        plan_mapping = {
            "basic": {
                "price_id": "price_basic_monthly",
                "name": "Basic Plan",
                "amount": 1500
            },
            "premium": {
                "price_id": "price_premium_monthly",
                "name": "Premium Plan",
                "amount": 2500
            }
        }

        if request.plan_id not in plan_mapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid plan_id. Must be one of: {', '.join(plan_mapping.keys())}"
            )

        plan = plan_mapping[request.plan_id]

        # Create Stripe Checkout session
        base_url = settings.get_base_url().replace(
            f":{settings.backend_port}",
            f":{settings.frontend_port}"
        )
        success_url = f"{base_url}/subscription-success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{base_url}/account/subscription"

        try:
            checkout_session = stripe.checkout.Session.create(
                customer=stripe_customer_id,
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": plan["name"],
                            "description": f"Resubscription to The Daily Worker - {plan['name']}"
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
                    "customer_email": user_email,
                    "resubscription": "true"
                }
            )

            logger.info(f"Created resubscription checkout session for user {user_id}")

            return {
                "session_id": checkout_session.id,
                "session_url": checkout_session.url,
                "message": "Checkout session created. Redirecting to payment..."
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create checkout session: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating resubscription checkout: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )
    finally:
        conn.close()


# ============================================================
# ENHANCED CANCELLATION WITH EMAIL (UPDATE EXISTING ENDPOINT)
# ============================================================

@router.post("/cancel-subscription-with-email", response_model=CancellationResponse)
async def cancel_subscription_with_email(user: dict = Depends(require_user)):
    """
    Enhanced version of cancel_subscription that sends email notification

    This is the cancel-at-period-end flow with email support
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        user_id = user['user_id']
        user_email = user['email']

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

        # Cancel subscription in Stripe (at period end)
        try:
            stripe_subscription = stripe.Subscription.modify(
                stripe_subscription_id,
                cancel_at_period_end=True
            )

            access_until = datetime.fromtimestamp(stripe_subscription.current_period_end).isoformat()

            # Update database
            cursor.execute("""
                UPDATE subscriptions
                SET cancel_at_period_end = 1, updated_at = ?
                WHERE id = ?
            """, (datetime.utcnow(), subscription_id))

            # Log event
            cursor.execute("""
                INSERT INTO subscription_events (subscription_id, user_id, event_type, event_data_json, created_at)
                VALUES (?, ?, 'subscription_cancel_scheduled', ?, ?)
            """, (
                subscription_id,
                user_id,
                f'{{"access_until": "{access_until}"}}',
                datetime.utcnow()
            ))

            conn.commit()

            # Send confirmation email
            send_cancellation_email(user_email, access_until)

            logger.info(f"Scheduled cancellation for user {user_id} (subscription_id: {subscription_id})")

            return CancellationResponse(
                message="Subscription will be canceled at the end of the billing period",
                cancel_at=stripe_subscription.current_period_end,
                access_until=access_until
            )

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
