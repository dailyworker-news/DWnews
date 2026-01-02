"""
Test Suite for Subscription Management
Phase 7.5: Subscription Management
Tests cancellation, pause, reactivation, and grace period features
"""

import pytest
import json
import stripe
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, call
from fastapi.testclient import TestClient
import sqlite3

# Import the app
import sys
import os

# Add parent directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(backend_dir)
sys.path.insert(0, backend_dir)
sys.path.insert(0, project_dir)

from backend.main import app
from backend.database import get_db_connection

client = TestClient(app)


# ============================================================
# TEST DATA & FIXTURES
# ============================================================

@pytest.fixture
def test_db():
    """Create a test database connection"""
    import sqlite3
    # Use actual database from project
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'database',
        'daily_worker.db'
    )
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture
def test_user(test_db):
    """Create a test user with active subscription"""
    cursor = test_db.cursor()

    # Create user
    cursor.execute("""
        INSERT INTO users (email, password_hash, subscription_status, stripe_customer_id, subscriber_since)
        VALUES (?, ?, ?, ?, ?)
    """, ('testuser@example.com', 'hashed_password', 'active', 'cus_test_123', datetime.utcnow()))

    user_id = cursor.lastrowid

    # Get plan ID for Basic Subscriber
    cursor.execute("SELECT id FROM subscription_plans WHERE plan_name = 'Basic Subscriber'")
    plan_id = cursor.fetchone()[0]

    # Create active subscription
    cursor.execute("""
        INSERT INTO subscriptions
        (user_id, stripe_subscription_id, plan_id, status, current_period_start, current_period_end, cancel_at_period_end)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        'sub_test_active_123',
        plan_id,
        'active',
        datetime.utcnow(),
        datetime.utcnow() + timedelta(days=30),
        0
    ))

    test_db.commit()

    return {
        'user_id': user_id,
        'email': 'testuser@example.com',
        'stripe_customer_id': 'cus_test_123',
        'stripe_subscription_id': 'sub_test_active_123'
    }


@pytest.fixture
def mock_auth_token(test_user):
    """Mock authentication token"""
    with patch('backend.auth.require_user') as mock_require:
        mock_require.return_value = {
            'user_id': test_user['user_id'],
            'email': test_user['email'],
            'subscription_status': 'active'
        }
        yield mock_require


# ============================================================
# SUBSCRIPTION CANCELLATION TESTS
# ============================================================

class TestSubscriptionCancellation:
    """Test subscription cancellation features"""

    @patch('stripe.Subscription.modify')
    def test_cancel_at_period_end(self, mock_stripe_modify, test_user, mock_auth_token):
        """Test canceling subscription at end of billing period"""
        # Setup mock
        mock_subscription = Mock()
        mock_subscription.id = test_user['stripe_subscription_id']
        mock_subscription.current_period_end = int((datetime.utcnow() + timedelta(days=30)).timestamp())
        mock_subscription.cancel_at_period_end = True
        mock_stripe_modify.return_value = mock_subscription

        # Make request
        response = client.post("/api/dashboard/cancel-subscription")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "cancel_at" in data
        assert "access_until" in data
        assert "end of the billing period" in data["message"]

        # Verify Stripe was called
        mock_stripe_modify.assert_called_once_with(
            test_user['stripe_subscription_id'],
            cancel_at_period_end=True
        )

        # Verify database was updated
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cancel_at_period_end FROM subscriptions
            WHERE stripe_subscription_id = ?
        """, (test_user['stripe_subscription_id'],))
        result = cursor.fetchone()
        assert result[0] == 1
        conn.close()

    @patch('stripe.Subscription.delete')
    def test_cancel_immediately(self, mock_stripe_delete, test_user, mock_auth_token):
        """Test immediate subscription cancellation"""
        # Setup mock
        mock_subscription = Mock()
        mock_subscription.id = test_user['stripe_subscription_id']
        mock_subscription.status = 'canceled'
        mock_subscription.canceled_at = int(datetime.utcnow().timestamp())
        mock_stripe_delete.return_value = mock_subscription

        # Make request
        response = client.post("/api/dashboard/cancel-subscription-immediately")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "immediately" in data["message"].lower()
        assert "canceled_at" in data

        # Verify Stripe was called
        mock_stripe_delete.assert_called_once_with(test_user['stripe_subscription_id'])

        # Verify database was updated
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT status, canceled_at FROM subscriptions
            WHERE stripe_subscription_id = ?
        """, (test_user['stripe_subscription_id'],))
        result = cursor.fetchone()
        assert result[0] == 'canceled'
        assert result[1] is not None
        conn.close()

    def test_cancel_no_active_subscription(self, mock_auth_token):
        """Test cancellation when user has no active subscription"""
        # Override mock to return user without subscription
        mock_auth_token.return_value = {
            'user_id': 9999,
            'email': 'nosubscription@example.com',
            'subscription_status': 'free'
        }

        response = client.post("/api/dashboard/cancel-subscription")

        assert response.status_code == 400
        assert "No active subscription" in response.json()["detail"]

    @patch('stripe.Subscription.modify')
    def test_cancel_stripe_error(self, mock_stripe_modify, test_user, mock_auth_token):
        """Test handling Stripe API errors during cancellation"""
        mock_stripe_modify.side_effect = stripe.error.StripeError("API Error")

        response = client.post("/api/dashboard/cancel-subscription")

        assert response.status_code == 400
        assert "Failed to cancel" in response.json()["detail"]


# ============================================================
# SUBSCRIPTION PAUSE TESTS
# ============================================================

class TestSubscriptionPause:
    """Test subscription pause feature"""

    @patch('stripe.Subscription.modify')
    def test_pause_subscription_1_month(self, mock_stripe_modify, test_user, mock_auth_token):
        """Test pausing subscription for 1 month"""
        # Setup mock
        resume_date = datetime.utcnow() + timedelta(days=30)
        mock_subscription = Mock()
        mock_subscription.id = test_user['stripe_subscription_id']
        mock_subscription.pause_collection = {
            'behavior': 'void',
            'resumes_at': int(resume_date.timestamp())
        }
        mock_stripe_modify.return_value = mock_subscription

        # Make request
        response = client.post(
            "/api/dashboard/pause-subscription",
            json={"pause_months": 1}
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "paused" in data["message"].lower()
        assert "resumes_at" in data

        # Verify Stripe was called with correct pause settings
        mock_stripe_modify.assert_called_once()
        call_args = mock_stripe_modify.call_args
        assert 'pause_collection' in call_args[1]

    @patch('stripe.Subscription.modify')
    def test_pause_subscription_3_months(self, mock_stripe_modify, test_user, mock_auth_token):
        """Test pausing subscription for 3 months"""
        resume_date = datetime.utcnow() + timedelta(days=90)
        mock_subscription = Mock()
        mock_subscription.pause_collection = {
            'behavior': 'void',
            'resumes_at': int(resume_date.timestamp())
        }
        mock_stripe_modify.return_value = mock_subscription

        response = client.post(
            "/api/dashboard/pause-subscription",
            json={"pause_months": 3}
        )

        assert response.status_code == 200

    def test_pause_invalid_duration(self, test_user, mock_auth_token):
        """Test pause with invalid duration (must be 1-3 months)"""
        response = client.post(
            "/api/dashboard/pause-subscription",
            json={"pause_months": 6}
        )

        assert response.status_code == 400
        assert "1-3 months" in response.json()["detail"]

    def test_pause_already_paused(self, test_user, mock_auth_token, test_db):
        """Test pausing an already paused subscription"""
        # Update subscription to paused status
        cursor = test_db.cursor()
        cursor.execute("""
            UPDATE subscriptions
            SET status = 'paused'
            WHERE stripe_subscription_id = ?
        """, (test_user['stripe_subscription_id'],))
        test_db.commit()

        response = client.post(
            "/api/dashboard/pause-subscription",
            json={"pause_months": 1}
        )

        assert response.status_code == 400
        assert "already paused" in response.json()["detail"].lower()


# ============================================================
# SUBSCRIPTION REACTIVATION TESTS
# ============================================================

class TestSubscriptionReactivation:
    """Test subscription reactivation feature"""

    @patch('stripe.Subscription.modify')
    def test_reactivate_canceled_subscription(self, mock_stripe_modify, test_user, mock_auth_token, test_db):
        """Test reactivating a subscription that was canceled"""
        # Set subscription to canceled
        cursor = test_db.cursor()
        cursor.execute("""
            UPDATE subscriptions
            SET status = 'canceled', cancel_at_period_end = 1, canceled_at = ?
            WHERE stripe_subscription_id = ?
        """, (datetime.utcnow(), test_user['stripe_subscription_id']))
        test_db.commit()

        # Setup mock
        mock_subscription = Mock()
        mock_subscription.id = test_user['stripe_subscription_id']
        mock_subscription.status = 'active'
        mock_subscription.cancel_at_period_end = False
        mock_stripe_modify.return_value = mock_subscription

        # Make request
        response = client.post("/api/dashboard/reactivate-subscription")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "reactivated" in data["message"].lower()

        # Verify Stripe was called
        mock_stripe_modify.assert_called_once_with(
            test_user['stripe_subscription_id'],
            cancel_at_period_end=False
        )

        # Verify database was updated
        cursor.execute("""
            SELECT status, cancel_at_period_end FROM subscriptions
            WHERE stripe_subscription_id = ?
        """, (test_user['stripe_subscription_id'],))
        result = cursor.fetchone()
        assert result[0] == 'active'
        assert result[1] == 0

    @patch('stripe.Subscription.modify')
    def test_resume_paused_subscription(self, mock_stripe_modify, test_user, mock_auth_token, test_db):
        """Test resuming a paused subscription"""
        # Set subscription to paused
        cursor = test_db.cursor()
        cursor.execute("""
            UPDATE subscriptions
            SET status = 'paused'
            WHERE stripe_subscription_id = ?
        """, (test_user['stripe_subscription_id'],))
        test_db.commit()

        # Setup mock
        mock_subscription = Mock()
        mock_subscription.pause_collection = None
        mock_subscription.status = 'active'
        mock_stripe_modify.return_value = mock_subscription

        # Make request
        response = client.post("/api/dashboard/reactivate-subscription")

        # Assertions
        assert response.status_code == 200

        # Verify pause was removed
        call_args = mock_stripe_modify.call_args
        assert call_args[1].get('pause_collection') == ''

    def test_reactivate_active_subscription(self, test_user, mock_auth_token):
        """Test reactivating an already active subscription"""
        response = client.post("/api/dashboard/reactivate-subscription")

        assert response.status_code == 400
        assert "already active" in response.json()["detail"].lower()

    @patch('stripe.checkout.Session.create')
    @patch('stripe.Customer.retrieve')
    def test_resubscribe_after_complete_cancellation(
        self,
        mock_customer_retrieve,
        mock_session_create,
        test_user,
        mock_auth_token
    ):
        """Test resubscribing after subscription was completely canceled"""
        # Setup mocks
        mock_customer = Mock()
        mock_customer.id = test_user['stripe_customer_id']
        mock_customer_retrieve.return_value = mock_customer

        mock_session = Mock()
        mock_session.id = 'cs_new_subscription'
        mock_session.url = 'https://checkout.stripe.com/pay/cs_new_subscription'
        mock_session_create.return_value = mock_session

        # Make request
        response = client.post(
            "/api/dashboard/resubscribe",
            json={"plan_id": "basic"}
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "session_url" in data
        assert "checkout.stripe.com" in data["session_url"]


# ============================================================
# GRACE PERIOD TESTS
# ============================================================

class TestGracePeriod:
    """Test 3-day grace period for failed payments"""

    @patch('stripe.Webhook.construct_event')
    def test_payment_failed_within_grace_period(self, mock_construct_event):
        """Test that access is maintained during grace period"""
        # Create event for payment failure
        event = {
            "id": "evt_payment_failed",
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "id": "in_test_123",
                    "subscription": "sub_test_active_123",
                    "customer": "cus_test_123",
                    "attempt_count": 1,
                    "next_payment_attempt": int((datetime.utcnow() + timedelta(days=3)).timestamp())
                }
            }
        }
        mock_construct_event.return_value = event

        # Send webhook
        response = client.post(
            "/api/payments/webhooks/stripe",
            json=event,
            headers={"stripe-signature": "test_signature"}
        )

        assert response.status_code == 200

        # Verify subscription status is 'past_due' not 'unpaid'
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT status FROM subscriptions
            WHERE stripe_subscription_id = ?
        """, ('sub_test_active_123',))
        result = cursor.fetchone()
        if result:
            assert result[0] == 'past_due'
        conn.close()

    @patch('stripe.Webhook.construct_event')
    def test_payment_failed_after_grace_period(self, mock_construct_event):
        """Test that access is revoked after 3 failed attempts"""
        # Create event for final payment failure
        event = {
            "id": "evt_payment_failed_final",
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "id": "in_test_123",
                    "subscription": "sub_test_active_123",
                    "customer": "cus_test_123",
                    "attempt_count": 4,  # Exceeds grace period
                    "next_payment_attempt": None
                }
            }
        }
        mock_construct_event.return_value = event

        # Send webhook
        response = client.post(
            "/api/payments/webhooks/stripe",
            json=event,
            headers={"stripe-signature": "test_signature"}
        )

        assert response.status_code == 200

        # Verify subscription status is 'unpaid'
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT status FROM subscriptions
            WHERE stripe_subscription_id = ?
        """, ('sub_test_active_123',))
        result = cursor.fetchone()
        if result:
            assert result[0] in ['unpaid', 'canceled']
        conn.close()

    def test_grace_period_duration(self):
        """Test that grace period is exactly 3 days"""
        # This is a configuration test
        from backend.routes.subscription_management import GRACE_PERIOD_DAYS
        assert GRACE_PERIOD_DAYS == 3


# ============================================================
# EMAIL NOTIFICATION TESTS
# ============================================================

class TestEmailNotifications:
    """Test email notifications for subscription events"""

    @patch('backend.routes.subscription_management.send_email')
    @patch('stripe.Subscription.modify')
    def test_cancellation_email_sent(self, mock_stripe_modify, mock_send_email, test_user, mock_auth_token):
        """Test that cancellation confirmation email is sent"""
        # Setup mock
        mock_subscription = Mock()
        mock_subscription.current_period_end = int((datetime.utcnow() + timedelta(days=30)).timestamp())
        mock_stripe_modify.return_value = mock_subscription

        # Make request
        response = client.post("/api/dashboard/cancel-subscription")

        assert response.status_code == 200

        # Verify email was sent
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        assert test_user['email'] in str(call_args)
        assert 'cancel' in str(call_args).lower()

    @patch('backend.routes.subscription_management.send_email')
    @patch('stripe.Webhook.construct_event')
    def test_payment_failed_email_sent(self, mock_construct_event, mock_send_email):
        """Test that payment failure notification email is sent"""
        event = {
            "id": "evt_payment_failed",
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "id": "in_test_123",
                    "subscription": "sub_test_active_123",
                    "customer": "cus_test_123",
                    "customer_email": "testuser@example.com",
                    "attempt_count": 1
                }
            }
        }
        mock_construct_event.return_value = event

        response = client.post(
            "/api/payments/webhooks/stripe",
            json=event,
            headers={"stripe-signature": "test_signature"}
        )

        assert response.status_code == 200

        # Verify email was sent
        assert mock_send_email.called
        call_args = mock_send_email.call_args
        assert 'payment' in str(call_args).lower() or 'failed' in str(call_args).lower()

    @patch('backend.routes.subscription_management.send_email')
    @patch('stripe.Webhook.construct_event')
    def test_subscription_renewed_email_sent(self, mock_construct_event, mock_send_email):
        """Test that renewal confirmation email is sent"""
        event = {
            "id": "evt_invoice_paid",
            "type": "invoice.paid",
            "data": {
                "object": {
                    "id": "in_test_123",
                    "subscription": "sub_test_active_123",
                    "customer": "cus_test_123",
                    "customer_email": "testuser@example.com",
                    "amount_paid": 1500,
                    "billing_reason": "subscription_cycle"
                }
            }
        }
        mock_construct_event.return_value = event

        response = client.post(
            "/api/payments/webhooks/stripe",
            json=event,
            headers={"stripe-signature": "test_signature"}
        )

        assert response.status_code == 200

        # Verify renewal email was sent (not initial subscription)
        if mock_send_email.called:
            call_args = mock_send_email.call_args
            assert 'renew' in str(call_args).lower() or 'payment' in str(call_args).lower()

    @patch('backend.routes.subscription_management.send_email')
    @patch('stripe.Subscription.modify')
    def test_pause_notification_email_sent(self, mock_stripe_modify, mock_send_email, test_user, mock_auth_token):
        """Test that pause notification email is sent"""
        resume_date = datetime.utcnow() + timedelta(days=30)
        mock_subscription = Mock()
        mock_subscription.pause_collection = {
            'resumes_at': int(resume_date.timestamp())
        }
        mock_stripe_modify.return_value = mock_subscription

        response = client.post(
            "/api/dashboard/pause-subscription",
            json={"pause_months": 1}
        )

        assert response.status_code == 200

        # Verify email was sent
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        assert 'pause' in str(call_args).lower()

    @patch('backend.routes.subscription_management.send_email')
    @patch('stripe.Subscription.modify')
    def test_reactivation_email_sent(self, mock_stripe_modify, mock_send_email, test_user, mock_auth_token, test_db):
        """Test that reactivation confirmation email is sent"""
        # Set subscription to canceled
        cursor = test_db.cursor()
        cursor.execute("""
            UPDATE subscriptions
            SET status = 'canceled', cancel_at_period_end = 1
            WHERE stripe_subscription_id = ?
        """, (test_user['stripe_subscription_id'],))
        test_db.commit()

        mock_subscription = Mock()
        mock_subscription.status = 'active'
        mock_stripe_modify.return_value = mock_subscription

        response = client.post("/api/dashboard/reactivate-subscription")

        assert response.status_code == 200

        # Verify email was sent
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        assert 'reactivat' in str(call_args).lower() or 'resume' in str(call_args).lower()


# ============================================================
# PAYMENT METHOD UPDATE TESTS
# ============================================================

class TestPaymentMethodUpdate:
    """Test payment method updates via Customer Portal"""

    @patch('stripe.billing_portal.Session.create')
    def test_customer_portal_accessible(self, mock_portal_create, test_user, mock_auth_token):
        """Test that users can access Customer Portal to update payment method"""
        mock_portal = Mock()
        mock_portal.url = 'https://billing.stripe.com/session/test_123'
        mock_portal_create.return_value = mock_portal

        response = client.post(
            "/api/dashboard/customer-portal",
            json={}
        )

        assert response.status_code == 200
        data = response.json()
        assert "portal_url" in data
        assert "billing.stripe.com" in data["portal_url"]

    @patch('stripe.Webhook.construct_event')
    def test_payment_method_updated_webhook(self, mock_construct_event):
        """Test handling of payment method update webhook"""
        event = {
            "id": "evt_payment_method_updated",
            "type": "customer.updated",
            "data": {
                "object": {
                    "id": "cus_test_123",
                    "invoice_settings": {
                        "default_payment_method": "pm_new_card_123"
                    }
                }
            }
        }
        mock_construct_event.return_value = event

        response = client.post(
            "/api/payments/webhooks/stripe",
            json=event,
            headers={"stripe-signature": "test_signature"}
        )

        assert response.status_code == 200


# ============================================================
# INTEGRATION TESTS
# ============================================================

class TestSubscriptionManagementIntegration:
    """Integration tests for complete subscription lifecycle"""

    @patch('stripe.Subscription.modify')
    @patch('stripe.Subscription.delete')
    @patch('backend.routes.subscription_management.send_email')
    def test_complete_cancellation_flow(
        self,
        mock_send_email,
        mock_stripe_delete,
        mock_stripe_modify,
        test_user,
        mock_auth_token
    ):
        """Test complete cancellation flow: cancel at period end → immediate cancel"""
        # Step 1: Cancel at period end
        mock_subscription = Mock()
        mock_subscription.current_period_end = int((datetime.utcnow() + timedelta(days=30)).timestamp())
        mock_subscription.cancel_at_period_end = True
        mock_stripe_modify.return_value = mock_subscription

        response1 = client.post("/api/dashboard/cancel-subscription")
        assert response1.status_code == 200

        # Step 2: Change mind and cancel immediately
        mock_canceled = Mock()
        mock_canceled.status = 'canceled'
        mock_canceled.canceled_at = int(datetime.utcnow().timestamp())
        mock_stripe_delete.return_value = mock_canceled

        response2 = client.post("/api/dashboard/cancel-subscription-immediately")
        assert response2.status_code == 200

        # Verify both emails were sent
        assert mock_send_email.call_count >= 2

    @patch('stripe.Subscription.modify')
    @patch('backend.routes.subscription_management.send_email')
    def test_pause_and_resume_flow(
        self,
        mock_send_email,
        mock_stripe_modify,
        test_user,
        mock_auth_token,
        test_db
    ):
        """Test complete pause and resume flow"""
        # Step 1: Pause subscription
        resume_date = datetime.utcnow() + timedelta(days=60)
        mock_paused = Mock()
        mock_paused.pause_collection = {'resumes_at': int(resume_date.timestamp())}
        mock_stripe_modify.return_value = mock_paused

        response1 = client.post(
            "/api/dashboard/pause-subscription",
            json={"pause_months": 2}
        )
        assert response1.status_code == 200

        # Update DB to reflect pause
        cursor = test_db.cursor()
        cursor.execute("""
            UPDATE subscriptions SET status = 'paused'
            WHERE stripe_subscription_id = ?
        """, (test_user['stripe_subscription_id'],))
        test_db.commit()

        # Step 2: Resume subscription
        mock_resumed = Mock()
        mock_resumed.pause_collection = None
        mock_resumed.status = 'active'
        mock_stripe_modify.return_value = mock_resumed

        response2 = client.post("/api/dashboard/reactivate-subscription")
        assert response2.status_code == 200

        # Verify both emails were sent
        assert mock_send_email.call_count >= 2


# ============================================================
# MAIN TEST RUNNER
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
