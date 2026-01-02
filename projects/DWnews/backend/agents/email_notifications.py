"""
Email notification system for editorial workflow

Supports:
- SendGrid integration (production)
- Test mode (local development, logs emails to console)
- SMTP fallback (optional)

Configuration via environment variables:
- EMAIL_MODE: 'sendgrid', 'test', or 'smtp'
- SENDGRID_API_KEY: API key for SendGrid
- SMTP_* variables for SMTP configuration
"""

import os
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# Configuration
EMAIL_MODE = os.getenv('EMAIL_MODE', 'test')  # Default to test mode
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'editorial@dailyworker.news')
ADMIN_URL = os.getenv('ADMIN_URL', 'http://localhost:3000/admin')

# Initialize SendGrid client if available
sg_client = None
if EMAIL_MODE == 'sendgrid' and SENDGRID_API_KEY:
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        sg_client = SendGridAPIClient(SENDGRID_API_KEY)
        logger.info("SendGrid client initialized")
    except ImportError:
        logger.warning("SendGrid library not installed, falling back to test mode")
        EMAIL_MODE = 'test'
    except Exception as e:
        logger.error(f"Error initializing SendGrid: {e}")
        EMAIL_MODE = 'test'


def send_assignment_email(editor_email: str, article) -> bool:
    """
    Send article assignment email to editor

    Args:
        editor_email: Editor's email address
        article: Article object with title, category, deadline, etc.

    Returns:
        True if email sent successfully
    """
    try:
        category_name = article.category.name if article.category else 'Uncategorized'
        deadline_str = article.review_deadline.strftime('%B %d, %Y at %I:%M %p') if article.review_deadline else 'ASAP'

        subject = f"New article for review: {article.title}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #d32f2f; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .metadata {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #d32f2f; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #d32f2f; color: white; text-decoration: none; border-radius: 4px; margin: 15px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #777; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>The Daily Worker</h1>
                    <p>New Article Assignment</p>
                </div>
                <div class="content">
                    <h2>Article Ready for Review</h2>
                    <p>A new article has been assigned to you for editorial review.</p>

                    <div class="metadata">
                        <p><strong>Title:</strong> {article.title}</p>
                        <p><strong>Category:</strong> {category_name}</p>
                        <p><strong>Word Count:</strong> {article.word_count or 'Unknown'} words</p>
                        <p><strong>Reading Level:</strong> {f"{article.reading_level:.1f}" if article.reading_level else 'N/A'}</p>
                        <p><strong>Review Deadline:</strong> {deadline_str}</p>
                        <p><strong>Self-Audit Status:</strong> {'✓ Passed' if article.self_audit_passed else '✗ Failed'}</p>
                    </div>

                    <p>Please review this article and take one of the following actions:</p>
                    <ul>
                        <li><strong>Approve:</strong> Article is ready for publication</li>
                        <li><strong>Request Revision:</strong> Provide specific feedback for the AI journalist to address</li>
                        <li><strong>Reject:</strong> Article does not meet standards</li>
                    </ul>

                    <a href="{ADMIN_URL}/review/{article.id}" class="button">Review Article</a>
                </div>
                <div class="footer">
                    <p>The Daily Worker Editorial System</p>
                    <p>This is an automated message. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return _send_email(editor_email, subject, html_content)

    except Exception as e:
        logger.error(f"Error sending assignment email: {e}")
        return False


def send_revision_complete_email(editor_email: str, article) -> bool:
    """
    Send notification that article revision is complete

    Args:
        editor_email: Editor's email address
        article: Article object

    Returns:
        True if email sent successfully
    """
    try:
        category_name = article.category.name if article.category else 'Uncategorized'

        subject = f"Revision complete: {article.title}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2e7d32; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .metadata {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #2e7d32; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #2e7d32; color: white; text-decoration: none; border-radius: 4px; margin: 15px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #777; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>The Daily Worker</h1>
                    <p>Article Revision Complete</p>
                </div>
                <div class="content">
                    <h2>Revised Article Ready for Review</h2>
                    <p>The AI journalist has completed revisions based on your editorial notes.</p>

                    <div class="metadata">
                        <p><strong>Title:</strong> {article.title}</p>
                        <p><strong>Category:</strong> {category_name}</p>
                        <p><strong>Reading Level:</strong> {f"{article.reading_level:.1f}" if article.reading_level else 'N/A'}</p>
                        <p><strong>Your Notes:</strong> {article.editorial_notes[:200] if article.editorial_notes else 'None'}...</p>
                    </div>

                    <p>Please review the revised article to see if your feedback has been addressed.</p>

                    <a href="{ADMIN_URL}/review/{article.id}" class="button">Review Revision</a>
                </div>
                <div class="footer">
                    <p>The Daily Worker Editorial System</p>
                    <p>This is an automated message. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return _send_email(editor_email, subject, html_content)

    except Exception as e:
        logger.error(f"Error sending revision complete email: {e}")
        return False


def send_overdue_alert_email(editor_email: str, article) -> bool:
    """
    Send alert for overdue article review

    Args:
        editor_email: Editor's email address
        article: Article object

    Returns:
        True if email sent successfully
    """
    try:
        category_name = article.category.name if article.category else 'Uncategorized'
        deadline_str = article.review_deadline.strftime('%B %d, %Y at %I:%M %p') if article.review_deadline else 'Unknown'

        # Calculate how overdue
        if article.review_deadline:
            hours_overdue = (datetime.utcnow() - article.review_deadline).total_seconds() / 3600
            overdue_str = f"{int(hours_overdue)} hours"
        else:
            overdue_str = "Unknown"

        subject = f"⚠️ OVERDUE: Review needed for {article.title}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f57c00; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .metadata {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #f57c00; }}
                .alert {{ background-color: #fff3e0; padding: 15px; margin: 15px 0; border: 1px solid #f57c00; border-radius: 4px; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #f57c00; color: white; text-decoration: none; border-radius: 4px; margin: 15px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #777; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Review Overdue</h1>
                    <p>The Daily Worker</p>
                </div>
                <div class="content">
                    <div class="alert">
                        <strong>⚠️ This article review is overdue by {overdue_str}</strong>
                    </div>

                    <h2>Urgent: Article Needs Review</h2>
                    <p>The following article is past its review deadline and needs your attention.</p>

                    <div class="metadata">
                        <p><strong>Title:</strong> {article.title}</p>
                        <p><strong>Category:</strong> {category_name}</p>
                        <p><strong>Original Deadline:</strong> {deadline_str}</p>
                        <p><strong>Hours Overdue:</strong> {overdue_str}</p>
                    </div>

                    <p>Please review this article as soon as possible to keep our publication schedule on track.</p>

                    <a href="{ADMIN_URL}/review/{article.id}" class="button">Review Now</a>
                </div>
                <div class="footer">
                    <p>The Daily Worker Editorial System</p>
                    <p>This is an automated message. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return _send_email(editor_email, subject, html_content)

    except Exception as e:
        logger.error(f"Error sending overdue alert email: {e}")
        return False


def _send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Internal function to send email via configured method

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email body

    Returns:
        True if sent successfully
    """
    if EMAIL_MODE == 'test':
        # Test mode: log email to console
        logger.info("=" * 80)
        logger.info(f"TEST EMAIL")
        logger.info(f"To: {to_email}")
        logger.info(f"From: {FROM_EMAIL}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body (first 200 chars): {html_content[:200]}...")
        logger.info("=" * 80)
        return True

    elif EMAIL_MODE == 'sendgrid' and sg_client:
        try:
            from sendgrid.helpers.mail import Mail

            message = Mail(
                from_email=FROM_EMAIL,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )

            response = sg_client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"SendGrid email sent to {to_email}, status: {response.status_code}")
                return True
            else:
                logger.warning(f"SendGrid returned status {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"SendGrid error: {e}")
            return False

    elif EMAIL_MODE == 'smtp':
        # SMTP fallback
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            smtp_server = os.getenv('SMTP_SERVER', 'localhost')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER', '')
            smtp_password = os.getenv('SMTP_PASSWORD', '')

            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = FROM_EMAIL
            msg['To'] = to_email

            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                if smtp_user and smtp_password:
                    server.login(smtp_user, smtp_password)
                server.send_message(msg)

            logger.info(f"SMTP email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return False

    else:
        logger.error(f"Invalid EMAIL_MODE: {EMAIL_MODE}")
        return False
