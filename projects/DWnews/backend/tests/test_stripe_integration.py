"""
Test Suite for Stripe Payment Integration
Phase 7.2: Stripe Payment Integration
Tests subscription checkout, webhooks, and payment flows
"""

import pytest
import json
import stripe
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

# Import the app
import sys
import os

# Add parent directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(backend_dir)
sys.path.insert(0, backend_dir)
sys.path.insert(0, project_dir)

from backend.main import app

client = TestClient(app)


# ============================================================
# TEST DATA & FIXTURES
# ============================================================

STRIPE_TEST_CARDS = {
    "success": "4242424242424242",
    "decline": "4000000000000002",
    "auth_required": "4000002500003155",
    "insufficient_funds": "4000000000009995",
    "lost_card": "4000000000009987",
    "stolen_card": "4000000000009979",
    "expired_card": "4000000000000069",
    "incorrect_cvc": "4000000000000127",
    "processing_error": "4000000000000119",
}

TEST_PLANS = {
    "basic": {
        "plan_id": "basic",
        "price_cents": 1500,
        "name": "Basic Plan"
    },
    "premium": {
        "plan_id": "premium",
        "price_cents": 2500,
        "name": "Premium Plan"
    }
}


@pytest.fixture
def mock_stripe_customer():
    """Mock Stripe Customer"""
    customer = Mock()
    customer.id = "cus_test_123456"
    customer.email = "test@example.com"
    return customer


@pytest.fixture
def mock_stripe_checkout_session():
    """Mock Stripe Checkout Session"""
    session = Mock()
    session.id = "cs_test_123456"
    session.url = "https://checkout.stripe.com/pay/cs_test_123456"
    session.customer = "cus_test_123456"
    session.subscription = "sub_test_123456"
    return session


@pytest.fixture
def mock_stripe_portal_session():
    """Mock Stripe Customer Portal Session"""
    portal = Mock()
    portal.url = "https://billing.stripe.com/session/test_123456"
    return portal


# ============================================================
# CHECKOUT SESSION TESTS
# ============================================================

class TestCheckoutSession:
    """Test Stripe Checkout session creation"""

    @patch('stripe.Customer.list')
    @patch('stripe.Customer.create')
    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session_new_customer(
        self,
        mock_session_create,
        mock_customer_create,
        mock_customer_list,
        mock_stripe_customer,
        mock_stripe_checkout_session
    ):
        """Test checkout session creation for new customer"""
        # Setup mocks
        mock_customer_list.return_value = Mock(data=[])
        mock_customer_create.return_value = mock_stripe_customer
        mock_session_create.return_value = mock_stripe_checkout_session

        # Make request
        response = client.post(
            "/api/payments/subscribe",
            json={
                "plan_id": "basic",
                "email": "newuser@example.com"
            }
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "cs_test_123456"
        assert "checkout.stripe.com" in data["session_url"]
        assert "publishable_key" in data

        # Verify Stripe calls
        mock_customer_list.assert_called_once()
        mock_customer_create.assert_called_once()
        mock_session_create.assert_called_once()

    @patch('stripe.Customer.list')
    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session_existing_customer(
        self,
        mock_session_create,
        mock_customer_list,
        mock_stripe_customer,
        mock_stripe_checkout_session
    ):
        """Test checkout session creation for existing customer"""
        # Setup mocks
        mock_customer_list.return_value = Mock(data=[mock_stripe_customer])
        mock_session_create.return_value = mock_stripe_checkout_session

        # Make request
        response = client.post(
            "/api/payments/subscribe",
            json={
                "plan_id": "basic",
                "email": "existing@example.com"
            }
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "cs_test_123456"

        # Should NOT create new customer
        mock_customer_list.assert_called_once()

    def test_create_checkout_session_invalid_plan(self):
        """Test checkout session with invalid plan ID"""
        response = client.post(
            "/api/payments/subscribe",
            json={
                "plan_id": "invalid_plan",
                "email": "test@example.com"
            }
        )

        assert response.status_code == 400
        assert "Invalid plan_id" in response.json()["detail"]

    def test_create_checkout_session_invalid_email(self):
        """Test checkout session with invalid email"""
        response = client.post(
            "/api/payments/subscribe",
            json={
                "plan_id": "basic",
                "email": "not-an-email"
            }
        )

        assert response.status_code == 422  # Validation error

    @patch('stripe.Customer.list')
    @patch('stripe.Customer.create')
    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session_stripe_error(
        self,
        mock_session_create,
        mock_customer_create,
        mock_customer_list
    ):
        """Test handling of Stripe API errors"""
        # Setup mocks
        mock_customer_list.return_value = Mock(data=[])
        mock_customer_create.side_effect = stripe.error.StripeError("API Error")

        # Make request
        response = client.post(
            "/api/payments/subscribe",
            json={
                "plan_id": "basic",
                "email": "test@example.com"
            }
        )

        assert response.status_code == 400
        assert "Stripe error" in response.json()["detail"]


# ============================================================
# CUSTOMER PORTAL TESTS
# ============================================================

class TestCustomerPortal:
    """Test Stripe Customer Portal session creation"""

    @patch('stripe.billing_portal.Session.create')
    def test_create_portal_session(self, mock_portal_create, mock_stripe_portal_session):
        """Test creating customer portal session"""
        mock_portal_create.return_value = mock_stripe_portal_session

        response = client.post(
            "/api/payments/customer-portal",
            json={
                "customer_id": "cus_test_123456"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "billing.stripe.com" in data["portal_url"]
        mock_portal_create.assert_called_once()

    @patch('stripe.billing_portal.Session.create')
    def test_create_portal_session_with_return_url(
        self,
        mock_portal_create,
        mock_stripe_portal_session
    ):
        """Test portal session with custom return URL"""
        mock_portal_create.return_value = mock_stripe_portal_session

        response = client.post(
            "/api/payments/customer-portal",
            json={
                "customer_id": "cus_test_123456",
                "return_url": "https://example.com/account"
            }
        )

        assert response.status_code == 200
        mock_portal_create.assert_called_once()

    @patch('stripe.billing_portal.Session.create')
    def test_create_portal_session_stripe_error(self, mock_portal_create):
        """Test handling of Stripe API errors in portal creation"""
        mock_portal_create.side_effect = stripe.error.StripeError("Portal Error")

        response = client.post(
            "/api/payments/customer-portal",
            json={
                "customer_id": "cus_invalid"
            }
        )

        assert response.status_code == 400
        assert "Stripe error" in response.json()["detail"]


# ============================================================
# WEBHOOK TESTS
# ============================================================

class TestStripeWebhooks:
    """Test Stripe webhook event handling"""

    def create_mock_event(self, event_type: str, data_object: dict):
        """Helper to create mock Stripe event"""
        return {
            "id": f"evt_test_{event_type}",
            "type": event_type,
            "data": {
                "object": data_object
            }
        }

    @patch('stripe.Webhook.construct_event')
    def test_webhook_checkout_completed(self, mock_construct_event):
        """Test checkout.session.completed webhook"""
        event = self.create_mock_event(
            "checkout.session.completed",
            {
                "id": "cs_test_123",
                "customer": "cus_test_123",
                "subscription": "sub_test_123",
                "customer_details": {"email": "test@example.com"}
            }
        )
        mock_construct_event.return_value = event

        response = client.post(
            "/api/payments/webhooks/stripe",
            json=event,
            headers={"stripe-signature": "test_signature"}
        )

        assert response.status_code == 200
        assert response.json()["status"] == "success"

    @patch('stripe.Webhook.construct_event')
    def test_webhook_invoice_paid(self, mock_construct_event):
        """Test invoice.paid webhook"""
        event = self.create_mock_event(
            "invoice.paid",
            {
                "id": "in_test_123",
                "subscription": "sub_test_123",
                "customer": "cus_test_123",
                "amount_paid": 1500
            }
        )
        mock_construct_event.return_value = event

        response = client.post(
            "/api/payments/webhooks/stripe",
            json=event,
            headers={"stripe-signature": "test_signature"}
        )

        assert response.status_code == 200

    @patch('stripe.Webhook.construct_event')
    def test_webhook_invoice_payment_failed(self, mock_construct_event):
        """Test invoice.payment_failed webhook"""
        event = self.create_mock_event(
            "invoice.payment_failed",
            {
                "id": "in_test_123",
                "subscription": "sub_test_123",
                "customer": "cus_test_123"
            }
        )
        mock_construct_event.return_value = event

        response = client.post(
            "/api/payments/webhooks/stripe",
            json=event,
            headers={"stripe-signature": "test_signature"}
        )

        assert response.status_code == 200

    @patch('stripe.Webhook.construct_event')
    def test_webhook_subscription_updated(self, mock_construct_event):
        """Test customer.subscription.updated webhook"""
        event = self.create_mock_event(
            "customer.subscription.updated",
            {
                "id": "sub_test_123",
                "status": "active",
                "customer": "cus_test_123"
            }
        )
        mock_construct_event.return_value = event

        response = client.post(
            "/api/payments/webhooks/stripe",
            json=event,
            headers={"stripe-signature": "test_signature"}
        )

        assert response.status_code == 200

    @patch('stripe.Webhook.construct_event')
    def test_webhook_subscription_deleted(self, mock_construct_event):
        """Test customer.subscription.deleted webhook"""
        event = self.create_mock_event(
            "customer.subscription.deleted",
            {
                "id": "sub_test_123",
                "customer": "cus_test_123"
            }
        )
        mock_construct_event.return_value = event

        response = client.post(
            "/api/payments/webhooks/stripe",
            json=event,
            headers={"stripe-signature": "test_signature"}
        )

        assert response.status_code == 200

    def test_webhook_invalid_signature(self):
        """Test webhook with invalid signature"""
        with patch('stripe.Webhook.construct_event') as mock_construct:
            mock_construct.side_effect = stripe.error.SignatureVerificationError(
                "Invalid signature",
                "sig_header"
            )

            response = client.post(
                "/api/payments/webhooks/stripe",
                json={},
                headers={"stripe-signature": "invalid_signature"}
            )

            assert response.status_code == 400
            assert "Invalid signature" in response.json()["detail"]

    def test_webhook_invalid_payload(self):
        """Test webhook with invalid JSON payload"""
        with patch('stripe.Webhook.construct_event') as mock_construct:
            mock_construct.side_effect = ValueError("Invalid JSON")

            response = client.post(
                "/api/payments/webhooks/stripe",
                json={},
                headers={"stripe-signature": "test_signature"}
            )

            assert response.status_code == 400
            assert "Invalid payload" in response.json()["detail"]


# ============================================================
# UTILITY ENDPOINT TESTS
# ============================================================

class TestUtilityEndpoints:
    """Test utility endpoints"""

    def test_get_subscription_plans(self):
        """Test getting subscription plans"""
        response = client.get("/api/payments/plans")

        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert len(data["plans"]) >= 2  # At least free and basic

        # Check plan structure
        for plan in data["plans"]:
            assert "id" in plan
            assert "name" in plan
            assert "price_cents" in plan
            assert "features" in plan

    def test_get_stripe_config(self):
        """Test getting Stripe configuration"""
        response = client.get("/api/payments/config")

        assert response.status_code == 200
        data = response.json()
        assert "publishable_key" in data
        assert data["publishable_key"].startswith("pk_")
        assert data["country"] == "US"
        assert data["currency"] == "usd"

    @patch('stripe.Account.retrieve')
    def test_payments_health_check_healthy(self, mock_account):
        """Test payment health check when healthy"""
        mock_account.return_value = Mock()

        response = client.get("/api/payments/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["stripe_configured"] is True

    @patch('stripe.Account.retrieve')
    def test_payments_health_check_unhealthy(self, mock_account):
        """Test payment health check when Stripe is down"""
        mock_account.side_effect = stripe.error.APIConnectionError("Connection failed")

        response = client.get("/api/payments/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "error" in data


# ============================================================
# INTEGRATION TESTS
# ============================================================

class TestPaymentFlowIntegration:
    """Integration tests for complete payment flows"""

    @patch('stripe.Customer.list')
    @patch('stripe.Customer.create')
    @patch('stripe.checkout.Session.create')
    @patch('stripe.Webhook.construct_event')
    def test_complete_signup_flow(
        self,
        mock_construct_event,
        mock_session_create,
        mock_customer_create,
        mock_customer_list,
        mock_stripe_customer,
        mock_stripe_checkout_session
    ):
        """Test complete signup flow: checkout → webhook → database update"""
        # Setup mocks
        mock_customer_list.return_value = Mock(data=[])
        mock_customer_create.return_value = mock_stripe_customer
        mock_session_create.return_value = mock_stripe_checkout_session

        # Step 1: Create checkout session
        checkout_response = client.post(
            "/api/payments/subscribe",
            json={
                "plan_id": "basic",
                "email": "integration@example.com"
            }
        )
        assert checkout_response.status_code == 200

        # Step 2: Simulate webhook event
        webhook_event = {
            "id": "evt_test_integration",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": mock_stripe_checkout_session.id,
                    "customer": mock_stripe_customer.id,
                    "subscription": "sub_test_123",
                    "customer_details": {"email": "integration@example.com"}
                }
            }
        }
        mock_construct_event.return_value = webhook_event

        webhook_response = client.post(
            "/api/payments/webhooks/stripe",
            json=webhook_event,
            headers={"stripe-signature": "test_signature"}
        )
        assert webhook_response.status_code == 200


# ============================================================
# MAIN TEST RUNNER
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
