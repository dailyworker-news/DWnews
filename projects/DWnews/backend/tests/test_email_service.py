"""
Test Suite for Email Notification Service
Phase 7.6: Email Notifications & Testing
Tests for SendGrid integration and email templates
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json


# Test email service initialization
class TestEmailServiceInitialization:
    """Test email service setup and configuration"""

    def test_email_service_requires_api_key(self):
        """Email service should raise error if SENDGRID_API_KEY is not set"""
        from backend.services.email_service import EmailService

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="SENDGRID_API_KEY"):
                EmailService()

    def test_email_service_initializes_with_api_key(self):
        """Email service should initialize successfully with valid API key"""
        from backend.services.email_service import EmailService

        with patch.dict(os.environ, {"SENDGRID_API_KEY": "test_key_123"}):
            service = EmailService()
            assert service is not None
            assert service.api_key == "test_key_123"

    def test_email_service_sets_from_email(self):
        """Email service should use configured from_email"""
        from backend.services.email_service import EmailService

        with patch.dict(os.environ, {
            "SENDGRID_API_KEY": "test_key_123",
            "FROM_EMAIL": "news@dailyworker.com"
        }):
            service = EmailService()
            assert service.from_email == "news@dailyworker.com"

    def test_email_service_defaults_from_email(self):
        """Email service should use default from_email if not configured"""
        from backend.services.email_service import EmailService

        with patch.dict(os.environ, {"SENDGRID_API_KEY": "test_key_123"}):
            service = EmailService()
            assert service.from_email == "noreply@thedailyworker.com"


# Test email template rendering
class TestEmailTemplates:
    """Test email template rendering and content"""

    @pytest.fixture
    def email_service(self):
        """Create email service instance for testing"""
        from backend.services.email_service import EmailService

        with patch.dict(os.environ, {"SENDGRID_API_KEY": "test_key_123"}):
            return EmailService()

    def test_subscription_confirmation_template(self, email_service):
        """Subscription confirmation email should have correct content"""
        result = email_service.render_template(
            "subscription_confirmation",
            {
                "user_name": "John Doe",
                "plan_name": "Premium",
                "amount_dollars": "25.00",
                "next_billing_date": "2026-02-01"
            }
        )

        assert "Welcome to The Daily Worker" in result["subject"]
        assert "John Doe" in result["html"]
        assert "Premium" in result["html"]
        assert "$25.00" in result["html"]
        assert "2026-02-01" in result["html"]
        assert "subscription" in result["html"].lower()

    def test_payment_receipt_template(self, email_service):
        """Payment receipt email should have correct content"""
        result = email_service.render_template(
            "payment_receipt",
            {
                "user_name": "Jane Smith",
                "amount_dollars": "15.00",
                "payment_date": "2026-01-02",
                "next_billing_date": "2026-02-02",
                "invoice_url": "https://stripe.com/invoice/123"
            }
        )

        assert "Payment Receipt" in result["subject"] or "Payment Confirmed" in result["subject"]
        assert "Jane Smith" in result["html"]
        assert "$15.00" in result["html"]
        assert "2026-01-02" in result["html"]
        assert "2026-02-02" in result["html"]

    def test_payment_failed_template(self, email_service):
        """Payment failed email should have correct content"""
        result = email_service.render_template(
            "payment_failed",
            {
                "user_name": "Bob Johnson",
                "attempt_count": 2,
                "next_attempt_date": "2026-01-05",
                "update_payment_url": "https://example.com/update-payment"
            }
        )

        assert "Payment Failed" in result["subject"] or "Payment Issue" in result["subject"]
        assert "Bob Johnson" in result["html"]
        assert "2" in result["html"] or "second" in result["html"].lower()
        assert "2026-01-05" in result["html"]
        assert "update your payment" in result["html"].lower()

    def test_renewal_reminder_template(self, email_service):
        """Renewal reminder email should have correct content"""
        result = email_service.render_template(
            "renewal_reminder",
            {
                "user_name": "Alice Brown",
                "plan_name": "Basic",
                "amount_dollars": "15.00",
                "renewal_date": "2026-01-09",
                "days_until_renewal": 7
            }
        )

        assert "Renewal" in result["subject"] or "Reminder" in result["subject"]
        assert "Alice Brown" in result["html"]
        assert "Basic" in result["html"]
        assert "$15.00" in result["html"]
        assert "2026-01-09" in result["html"]
        assert "7" in result["html"] or "week" in result["html"].lower()

    def test_cancellation_confirmation_template(self, email_service):
        """Cancellation confirmation email should have correct content"""
        result = email_service.render_template(
            "cancellation_confirmation",
            {
                "user_name": "Charlie Davis",
                "access_until": "2026-01-31",
                "reactivate_url": "https://example.com/reactivate"
            }
        )

        assert "Cancellation" in result["subject"] or "Canceled" in result["subject"]
        assert "Charlie Davis" in result["html"]
        assert "2026-01-31" in result["html"]
        assert "reactivate" in result["html"].lower()

    def test_renewal_confirmation_template(self, email_service):
        """Renewal confirmation email should have correct content"""
        result = email_service.render_template(
            "renewal_confirmation",
            {
                "user_name": "Diana Evans",
                "amount_dollars": "25.00",
                "next_billing_date": "2026-02-02"
            }
        )

        assert "Renewed" in result["subject"] or "Renewal" in result["subject"]
        assert "Diana Evans" in result["html"]
        assert "$25.00" in result["html"]
        assert "2026-02-02" in result["html"]


# Test email sending functionality
class TestEmailSending:
    """Test actual email sending via SendGrid API"""

    @pytest.fixture
    def email_service(self):
        """Create email service instance for testing"""
        from backend.services.email_service import EmailService

        with patch.dict(os.environ, {"SENDGRID_API_KEY": "test_key_123"}):
            return EmailService()

    def test_send_email_calls_sendgrid_api(self, email_service):
        """send_email should call SendGrid API with correct parameters"""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_client = Mock()
        mock_client.send.return_value = mock_response
        email_service.client = mock_client

        result = email_service.send_email(
            to_email="test@example.com",
            subject="Test Subject",
            html_content="<p>Test Content</p>"
        )

        assert result is True
        mock_client.send.assert_called_once()

    def test_send_email_handles_api_error(self, email_service):
        """send_email should handle SendGrid API errors gracefully"""
        mock_client = Mock()
        mock_client.send.side_effect = Exception("API Error")
        email_service.client = mock_client

        result = email_service.send_email(
            to_email="test@example.com",
            subject="Test Subject",
            html_content="<p>Test Content</p>"
        )

        assert result is False

    def test_send_subscription_confirmation(self, email_service):
        """send_subscription_confirmation should send email with correct template"""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_client = Mock()
        mock_client.send.return_value = mock_response
        email_service.client = mock_client

        result = email_service.send_subscription_confirmation(
            to_email="test@example.com",
            user_name="Test User",
            plan_name="Premium",
            amount_dollars="25.00",
            next_billing_date="2026-02-01"
        )

        assert result is True
        mock_client.send.assert_called_once()

    def test_send_payment_receipt(self, email_service):
        """send_payment_receipt should send email with correct template"""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_client = Mock()
        mock_client.send.return_value = mock_response
        email_service.client = mock_client

        result = email_service.send_payment_receipt(
            to_email="test@example.com",
            user_name="Test User",
            amount_dollars="15.00",
            payment_date="2026-01-02",
            next_billing_date="2026-02-02",
            invoice_url="https://stripe.com/invoice/123"
        )

        assert result is True

    def test_send_payment_failed(self, email_service):
        """send_payment_failed should send email with correct template"""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_client = Mock()
        mock_client.send.return_value = mock_response
        email_service.client = mock_client

        result = email_service.send_payment_failed(
            to_email="test@example.com",
            user_name="Test User",
            attempt_count=2,
            next_attempt_date="2026-01-05",
            update_payment_url="https://example.com/update"
        )

        assert result is True

    def test_send_renewal_reminder(self, email_service):
        """send_renewal_reminder should send email 7 days before renewal"""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_client = Mock()
        mock_client.send.return_value = mock_response
        email_service.client = mock_client

        result = email_service.send_renewal_reminder(
            to_email="test@example.com",
            user_name="Test User",
            plan_name="Basic",
            amount_dollars="15.00",
            renewal_date="2026-01-09"
        )

        assert result is True

    def test_send_cancellation_confirmation(self, email_service):
        """send_cancellation_confirmation should send email with correct template"""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_client = Mock()
        mock_client.send.return_value = mock_response
        email_service.client = mock_client

        result = email_service.send_cancellation_confirmation(
            to_email="test@example.com",
            user_name="Test User",
            access_until="2026-01-31",
            reactivate_url="https://example.com/reactivate"
        )

        assert result is True


# Test rate limiting and quotas
class TestEmailQuotas:
    """Test email rate limiting and free tier quotas"""

    @pytest.fixture
    def email_service(self):
        """Create email service instance for testing"""
        from backend.services.email_service import EmailService

        with patch.dict(os.environ, {"SENDGRID_API_KEY": "test_key_123"}):
            return EmailService()

    def test_email_service_tracks_daily_quota(self, email_service):
        """Email service should track daily sending quota"""
        assert hasattr(email_service, 'get_daily_usage')
        usage = email_service.get_daily_usage()
        assert isinstance(usage, int)
        assert usage >= 0

    def test_email_service_enforces_daily_limit(self, email_service):
        """Email service should enforce 100 emails/day limit"""
        assert hasattr(email_service, 'daily_limit')
        assert email_service.daily_limit == 100

    def test_email_service_rejects_over_quota(self, email_service):
        """Email service should reject emails when over quota"""
        # Set usage to 100 (at limit)
        email_service._daily_usage = 100

        # Mock client to verify it's not called
        mock_client = Mock()
        email_service.client = mock_client

        result = email_service.send_email(
            to_email="test@example.com",
            subject="Test",
            html_content="<p>Test</p>"
        )

        # Should fail without calling SendGrid
        assert result is False
        mock_client.send.assert_not_called()

    def test_quota_resets_daily(self, email_service):
        """Email quota should reset at midnight UTC"""
        # This test verifies the quota reset logic exists
        assert hasattr(email_service, 'reset_daily_quota')
        email_service.reset_daily_quota()
        assert email_service.get_daily_usage() == 0


# Test error handling
class TestEmailErrorHandling:
    """Test error handling for email operations"""

    @pytest.fixture
    def email_service(self):
        """Create email service instance for testing"""
        from backend.services.email_service import EmailService

        with patch.dict(os.environ, {"SENDGRID_API_KEY": "test_key_123"}):
            return EmailService()

    def test_invalid_email_address_returns_false(self, email_service):
        """send_email should return False for invalid email address"""
        result = email_service.send_email(
            to_email="not-an-email",
            subject="Test",
            html_content="<p>Test</p>"
        )

        assert result is False

    def test_missing_template_raises_error(self, email_service):
        """render_template should raise error for non-existent template"""
        with pytest.raises(ValueError, match="Template.*not found"):
            email_service.render_template("non_existent_template", {})

    def test_missing_template_variable_raises_error(self, email_service):
        """render_template should raise error for missing required variables"""
        with pytest.raises(KeyError):
            email_service.render_template("subscription_confirmation", {})

    def test_network_error_returns_false(self, email_service):
        """send_email should return False on network error"""
        mock_client = Mock()
        mock_client.send.side_effect = ConnectionError("Network error")
        email_service.client = mock_client

        result = email_service.send_email(
            to_email="test@example.com",
            subject="Test",
            html_content="<p>Test</p>"
        )

        assert result is False
