"""
Email Notification Service
Phase 7.6: Email Notifications & Testing

Provides email sending functionality via SendGrid API
Includes templates for subscription events and quota management
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Optional
from unittest.mock import MagicMock
import re

logger = logging.getLogger(__name__)

# Try to import SendGrid (will use mock in tests)
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    logger.warning("SendGrid not installed. Email sending will be disabled.")


class EmailService:
    """
    Email notification service using SendGrid

    Features:
    - Template-based email rendering
    - SendGrid API integration
    - Daily quota tracking (100 emails/day for free tier)
    - Error handling and logging
    """

    def __init__(self):
        """Initialize email service with SendGrid API key"""
        self.api_key = os.getenv("SENDGRID_API_KEY")

        if not self.api_key:
            raise ValueError(
                "SENDGRID_API_KEY environment variable is required. "
                "Get your API key from: https://app.sendgrid.com/settings/api_keys"
            )

        self.from_email = os.getenv("FROM_EMAIL", "noreply@thedailyworker.com")
        self.from_name = os.getenv("FROM_NAME", "The Daily Worker")

        # SendGrid client (will be mocked in tests)
        if SENDGRID_AVAILABLE:
            self.client = SendGridAPIClient(self.api_key)
        else:
            self.client = None

        # Daily quota tracking
        self.daily_limit = 100  # SendGrid free tier limit
        self._daily_usage = 0
        self._quota_reset_date = datetime.now(timezone.utc).date()

    def get_daily_usage(self) -> int:
        """Get current daily email usage count"""
        self._check_quota_reset()
        return self._daily_usage

    def reset_daily_quota(self):
        """Reset daily quota (called automatically at midnight UTC)"""
        self._daily_usage = 0
        self._quota_reset_date = datetime.now(timezone.utc).date()
        logger.info("Daily email quota reset")

    def _check_quota_reset(self):
        """Check if quota needs to be reset (new day)"""
        current_date = datetime.now(timezone.utc).date()
        if current_date > self._quota_reset_date:
            self.reset_daily_quota()

    def _is_valid_email(self, email: str) -> bool:
        """Validate email address format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None
    ) -> bool:
        """
        Send email via SendGrid API

        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML email body
            plain_content: Plain text email body (optional)

        Returns:
            True if email sent successfully, False otherwise
        """
        # Validate email address
        if not self._is_valid_email(to_email):
            logger.error(f"Invalid email address: {to_email}")
            return False

        # Check daily quota
        self._check_quota_reset()
        if self._daily_usage >= self.daily_limit:
            logger.error(
                f"Daily email quota exceeded ({self._daily_usage}/{self.daily_limit}). "
                f"Email to {to_email} not sent."
            )
            return False

        # Check if SendGrid client is available
        if not self.client:
            logger.warning(f"SendGrid not available. Logging email instead: {to_email}")
            logger.info(f"[EMAIL] To: {to_email}")
            logger.info(f"[EMAIL] Subject: {subject}")
            logger.info(f"[EMAIL] Body: {html_content[:200]}...")
            return False

        try:
            # Create email message (Mail may not be available if SendGrid not installed)
            if SENDGRID_AVAILABLE:
                message = Mail(
                    from_email=(self.from_email, self.from_name),
                    to_emails=to_email,
                    subject=subject,
                    html_content=html_content,
                    plain_text_content=plain_content or self._html_to_plain(html_content)
                )
            else:
                # Create a mock message object for testing
                message = MagicMock()

            # Send email
            response = self.client.send(message)

            # Check response
            if response.status_code in [200, 201, 202]:
                self._daily_usage += 1
                logger.info(
                    f"Email sent successfully to {to_email}. "
                    f"Daily usage: {self._daily_usage}/{self.daily_limit}"
                )
                return True
            else:
                logger.error(
                    f"SendGrid returned non-success status: {response.status_code}. "
                    f"Email to {to_email} may not have been sent."
                )
                return False

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}", exc_info=True)
            return False

    def _html_to_plain(self, html: str) -> str:
        """Convert HTML to plain text (basic implementation)"""
        # Remove HTML tags
        plain = re.sub(r'<[^>]+>', '', html)
        # Decode common entities
        plain = plain.replace('&nbsp;', ' ')
        plain = plain.replace('&amp;', '&')
        plain = plain.replace('&lt;', '<')
        plain = plain.replace('&gt;', '>')
        return plain.strip()

    def render_template(self, template_name: str, context: Dict) -> Dict[str, str]:
        """
        Render email template with context variables

        Args:
            template_name: Name of template to render
            context: Dictionary of template variables

        Returns:
            Dictionary with 'subject' and 'html' keys

        Raises:
            ValueError: If template not found
            KeyError: If required context variable missing
        """
        templates = {
            "subscription_confirmation": self._render_subscription_confirmation,
            "payment_receipt": self._render_payment_receipt,
            "payment_failed": self._render_payment_failed,
            "renewal_reminder": self._render_renewal_reminder,
            "renewal_confirmation": self._render_renewal_confirmation,
            "cancellation_confirmation": self._render_cancellation_confirmation,
        }

        if template_name not in templates:
            raise ValueError(
                f"Template '{template_name}' not found. "
                f"Available templates: {', '.join(templates.keys())}"
            )

        return templates[template_name](context)

    # Template rendering methods

    def _render_subscription_confirmation(self, ctx: Dict) -> Dict[str, str]:
        """Render subscription confirmation email"""
        subject = "Welcome to The Daily Worker - Subscription Confirmed"
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #d32f2f;">Welcome to The Daily Worker!</h1>

                <p>Hi {ctx['user_name']},</p>

                <p>Thank you for subscribing to The Daily Worker! Your subscription is now active.</p>

                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Subscription Details</h3>
                    <p><strong>Plan:</strong> {ctx['plan_name']}</p>
                    <p><strong>Amount:</strong> ${ctx['amount_dollars']}/month</p>
                    <p><strong>Next Billing Date:</strong> {ctx['next_billing_date']}</p>
                </div>

                <p>You now have full access to:</p>
                <ul>
                    <li>Unlimited articles</li>
                    <li>Sports coverage</li>
                    <li>Full archive access</li>
                    <li>Local news coverage</li>
                </ul>

                <p>Start reading at: <a href="https://thedailyworker.com">thedailyworker.com</a></p>

                <p>Need help? Visit your <a href="https://thedailyworker.com/account">account dashboard</a> to manage your subscription.</p>

                <p>Thank you for supporting independent journalism!</p>

                <p style="margin-top: 30px;">
                    Best regards,<br>
                    The Daily Worker Team
                </p>
            </div>
        </body>
        </html>
        """
        return {"subject": subject, "html": html}

    def _render_payment_receipt(self, ctx: Dict) -> Dict[str, str]:
        """Render payment receipt email"""
        subject = "Payment Receipt - The Daily Worker"
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #d32f2f;">Payment Confirmed</h1>

                <p>Hi {ctx['user_name']},</p>

                <p>We've received your payment. Thank you for your continued support!</p>

                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Payment Details</h3>
                    <p><strong>Amount Paid:</strong> ${ctx['amount_dollars']}</p>
                    <p><strong>Payment Date:</strong> {ctx['payment_date']}</p>
                    <p><strong>Next Billing Date:</strong> {ctx['next_billing_date']}</p>
                </div>

                <p>
                    <a href="{ctx['invoice_url']}" style="background-color: #d32f2f; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Download Invoice
                    </a>
                </p>

                <p style="margin-top: 30px;">
                    Best regards,<br>
                    The Daily Worker Team
                </p>
            </div>
        </body>
        </html>
        """
        return {"subject": subject, "html": html}

    def _render_payment_failed(self, ctx: Dict) -> Dict[str, str]:
        """Render payment failed email"""
        subject = "Payment Issue - Action Required"

        is_final_attempt = ctx['attempt_count'] >= 4

        if is_final_attempt:
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #d32f2f;">Subscription Canceled Due to Payment Failure</h1>

                    <p>Hi {ctx['user_name']},</p>

                    <p>We were unable to process your subscription payment after multiple attempts.</p>

                    <p style="color: #d32f2f; font-weight: bold;">
                        Your subscription has been canceled and your access to subscriber-only content has ended.
                    </p>

                    <p>To restore your access:</p>
                    <ol>
                        <li>Update your payment method</li>
                        <li>Resubscribe from your account dashboard</li>
                    </ol>

                    <p>
                        <a href="{ctx['update_payment_url']}" style="background-color: #d32f2f; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            Update Payment Method
                        </a>
                    </p>

                    <p style="margin-top: 30px;">
                        Best regards,<br>
                        The Daily Worker Team
                    </p>
                </div>
            </body>
            </html>
            """
        else:
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #ff9800;">Payment Failed - Action Needed</h1>

                    <p>Hi {ctx['user_name']},</p>

                    <p>We were unable to process your subscription payment.</p>

                    <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ff9800;">
                        <p style="margin: 0;"><strong>Attempt {ctx['attempt_count']} of 4</strong></p>
                        <p style="margin: 5px 0 0 0;">Next retry: {ctx['next_attempt_date']}</p>
                    </div>

                    <p style="color: #28a745; font-weight: bold;">
                        Good news: You still have full access to all subscriber benefits during the grace period.
                    </p>

                    <p>To avoid service interruption, please update your payment method:</p>

                    <p>
                        <a href="{ctx['update_payment_url']}" style="background-color: #d32f2f; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            Update Payment Method
                        </a>
                    </p>

                    <p style="margin-top: 30px;">
                        Best regards,<br>
                        The Daily Worker Team
                    </p>
                </div>
            </body>
            </html>
            """

        return {"subject": subject, "html": html}

    def _render_renewal_reminder(self, ctx: Dict) -> Dict[str, str]:
        """Render renewal reminder email (sent 7 days before renewal)"""
        subject = "Subscription Renewal Reminder - The Daily Worker"
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #d32f2f;">Subscription Renewal Reminder</h1>

                <p>Hi {ctx['user_name']},</p>

                <p>This is a friendly reminder that your subscription will renew in {ctx['days_until_renewal']} days.</p>

                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Renewal Details</h3>
                    <p><strong>Plan:</strong> {ctx['plan_name']}</p>
                    <p><strong>Amount:</strong> ${ctx['amount_dollars']}</p>
                    <p><strong>Renewal Date:</strong> {ctx['renewal_date']}</p>
                </div>

                <p>No action is needed - we'll automatically charge your payment method on file.</p>

                <p>Want to make changes? Visit your <a href="https://thedailyworker.com/account">account dashboard</a> to:</p>
                <ul>
                    <li>Update your payment method</li>
                    <li>Change your plan</li>
                    <li>Cancel your subscription</li>
                </ul>

                <p style="margin-top: 30px;">
                    Best regards,<br>
                    The Daily Worker Team
                </p>
            </div>
        </body>
        </html>
        """
        return {"subject": subject, "html": html}

    def _render_renewal_confirmation(self, ctx: Dict) -> Dict[str, str]:
        """Render subscription renewal confirmation email"""
        subject = "Subscription Renewed - The Daily Worker"
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #28a745;">Subscription Renewed Successfully</h1>

                <p>Hi {ctx['user_name']},</p>

                <p>Your subscription to The Daily Worker has been renewed. Thank you for your continued support!</p>

                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Renewal Details</h3>
                    <p><strong>Amount Charged:</strong> ${ctx['amount_dollars']}</p>
                    <p><strong>Next Billing Date:</strong> {ctx['next_billing_date']}</p>
                </div>

                <p>Your subscription remains active with full access to all benefits.</p>

                <p style="margin-top: 30px;">
                    Best regards,<br>
                    The Daily Worker Team
                </p>
            </div>
        </body>
        </html>
        """
        return {"subject": subject, "html": html}

    def _render_cancellation_confirmation(self, ctx: Dict) -> Dict[str, str]:
        """Render subscription cancellation confirmation email"""
        subject = "Subscription Cancellation Confirmed - The Daily Worker"
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #d32f2f;">Subscription Cancellation Confirmed</h1>

                <p>Hi {ctx['user_name']},</p>

                <p>Your subscription to The Daily Worker has been scheduled for cancellation.</p>

                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Access Until:</strong> {ctx['access_until']}</p>
                    <p style="margin-bottom: 0;">You will continue to have full access to all subscriber benefits until this date.</p>
                </div>

                <p>Changed your mind? You can reactivate your subscription at any time before then:</p>

                <p>
                    <a href="{ctx['reactivate_url']}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reactivate Subscription
                    </a>
                </p>

                <p>We're sorry to see you go! If you have any feedback about your experience, we'd love to hear it.</p>

                <p style="margin-top: 30px;">
                    Best regards,<br>
                    The Daily Worker Team
                </p>
            </div>
        </body>
        </html>
        """
        return {"subject": subject, "html": html}

    # Convenience methods for sending specific email types

    def send_subscription_confirmation(
        self,
        to_email: str,
        user_name: str,
        plan_name: str,
        amount_dollars: str,
        next_billing_date: str
    ) -> bool:
        """Send subscription confirmation email"""
        template = self.render_template("subscription_confirmation", {
            "user_name": user_name,
            "plan_name": plan_name,
            "amount_dollars": amount_dollars,
            "next_billing_date": next_billing_date
        })
        return self.send_email(to_email, template["subject"], template["html"])

    def send_payment_receipt(
        self,
        to_email: str,
        user_name: str,
        amount_dollars: str,
        payment_date: str,
        next_billing_date: str,
        invoice_url: str
    ) -> bool:
        """Send payment receipt email"""
        template = self.render_template("payment_receipt", {
            "user_name": user_name,
            "amount_dollars": amount_dollars,
            "payment_date": payment_date,
            "next_billing_date": next_billing_date,
            "invoice_url": invoice_url
        })
        return self.send_email(to_email, template["subject"], template["html"])

    def send_payment_failed(
        self,
        to_email: str,
        user_name: str,
        attempt_count: int,
        next_attempt_date: str,
        update_payment_url: str
    ) -> bool:
        """Send payment failed notification email"""
        template = self.render_template("payment_failed", {
            "user_name": user_name,
            "attempt_count": attempt_count,
            "next_attempt_date": next_attempt_date,
            "update_payment_url": update_payment_url
        })
        return self.send_email(to_email, template["subject"], template["html"])

    def send_renewal_reminder(
        self,
        to_email: str,
        user_name: str,
        plan_name: str,
        amount_dollars: str,
        renewal_date: str
    ) -> bool:
        """Send renewal reminder email (7 days before renewal)"""
        template = self.render_template("renewal_reminder", {
            "user_name": user_name,
            "plan_name": plan_name,
            "amount_dollars": amount_dollars,
            "renewal_date": renewal_date,
            "days_until_renewal": 7
        })
        return self.send_email(to_email, template["subject"], template["html"])

    def send_renewal_confirmation(
        self,
        to_email: str,
        user_name: str,
        amount_dollars: str,
        next_billing_date: str
    ) -> bool:
        """Send subscription renewal confirmation email"""
        template = self.render_template("renewal_confirmation", {
            "user_name": user_name,
            "amount_dollars": amount_dollars,
            "next_billing_date": next_billing_date
        })
        return self.send_email(to_email, template["subject"], template["html"])

    def send_cancellation_confirmation(
        self,
        to_email: str,
        user_name: str,
        access_until: str,
        reactivate_url: str
    ) -> bool:
        """Send subscription cancellation confirmation email"""
        template = self.render_template("cancellation_confirmation", {
            "user_name": user_name,
            "access_until": access_until,
            "reactivate_url": reactivate_url
        })
        return self.send_email(to_email, template["subject"], template["html"])


# Singleton instance for easy import
_email_service = None

def get_email_service() -> EmailService:
    """Get or create singleton email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
