# Subscription Workflows & Email Notifications

**Phase 7.6: Complete Documentation**

This document describes all subscription workflows, email notifications, and customer support procedures for The Daily Worker subscription system.

## Table of Contents
1. [Email Notification System](#email-notification-system)
2. [Subscription Flows](#subscription-flows)
3. [Email Templates](#email-templates)
4. [Customer Support Guide](#customer-support-guide)
5. [Technical Details](#technical-details)

---

## Email Notification System

### Overview
- **Service**: SendGrid API
- **Free Tier Limit**: 100 emails/day
- **Quota Reset**: Midnight UTC
- **From Address**: noreply@thedailyworker.com
- **Templates**: 6 HTML email templates

### Email Types

| Event | Template | Trigger | Recipient |
|-------|----------|---------|-----------|
| Subscription Created | `subscription_confirmation` | checkout.session.completed | New subscriber |
| Payment Receipt | `payment_receipt` | invoice.paid (initial) | Subscriber |
| Payment Failed | `payment_failed` | invoice.payment_failed | Subscriber |
| Renewal Reminder | `renewal_reminder` | 7 days before renewal | Subscriber |
| Renewal Confirmation | `renewal_confirmation` | invoice.paid (recurring) | Subscriber |
| Cancellation | `cancellation_confirmation` | subscription canceled | Former subscriber |

---

## Subscription Flows

### 1. New Subscription Flow

**User Journey:**
```
1. User visits pricing page
2. Selects plan (Basic $15/mo or Premium $25/mo)
3. Redirected to Stripe Checkout
4. Enters payment information
5. Completes payment
   ↓
6. Stripe webhook: checkout.session.completed
7. Database: Create subscription record
8. Email: Subscription Confirmation sent
   ↓
9. User redirected to success page
10. User gains immediate access to content
```

**Email Sent:** Subscription Confirmation
- Subject: "Welcome to The Daily Worker - Subscription Confirmed"
- Content: Plan details, billing info, access instructions
- CTA: "Start Reading"

---

### 2. Renewal Flow (Monthly)

**Automatic Process:**
```
1. 7 days before renewal:
   ↓
   Email: Renewal Reminder sent
   - Amount to be charged
   - Renewal date
   - Link to update payment method

2. On renewal date:
   ↓
   Stripe attempts payment

   SUCCESS:
   ↓
   3a. Stripe webhook: invoice.paid
   4a. Database: Update subscription status
   5a. Email: Renewal Confirmation sent
   6a. Access continues uninterrupted

   FAILURE:
   ↓
   3b. Stripe webhook: invoice.payment_failed
   4b. Enter Grace Period Flow (see below)
```

**Emails Sent:**
- **Renewal Reminder** (T-7 days)
  - Subject: "Subscription Renewal Reminder - The Daily Worker"
  - Content: Renewal date, amount, payment method on file

- **Renewal Confirmation** (on success)
  - Subject: "Subscription Renewed - The Daily Worker"
  - Content: Charge amount, next billing date

---

### 3. Payment Failure & Grace Period Flow

**Grace Period:** 3 payment retry attempts over ~10 days

**Process:**
```
Attempt 1 (Day 0):
↓
Email: Payment Failed (Attempt 1/4)
- Status: past_due
- Access: MAINTAINED
- Message: "We'll retry soon"

Attempt 2 (Day ~3):
↓
Email: Payment Failed (Attempt 2/4)
- Status: past_due
- Access: MAINTAINED
- Message: "Please update payment method"

Attempt 3 (Day ~6):
↓
Email: Payment Failed (Attempt 3/4)
- Status: past_due
- Access: MAINTAINED
- Message: "URGENT: Update payment method"

Attempt 4 (Day ~9):
↓
FINAL ATTEMPT FAILS
↓
Email: Payment Failed (Final)
- Status: unpaid
- Access: REVOKED
- Message: "Subscription canceled. Resubscribe to restore access."
```

**Customer Support Notes:**
- Users maintain access during attempts 1-3
- After attempt 4, access is immediately revoked
- User must resubscribe (not just update payment method)
- No refunds for period when access was revoked

---

### 4. Cancellation Flows

#### 4a. Cancel at Period End (Recommended)

**User Journey:**
```
1. User clicks "Cancel Subscription" in dashboard
2. Modal: "Cancel at end of period or immediately?"
3. User selects "At period end"
   ↓
4. API: POST /api/dashboard/cancel-subscription-with-email
5. Stripe: Set cancel_at_period_end = True
6. Database: Update subscription.cancel_at_period_end = 1
7. Email: Cancellation Confirmation sent
   ↓
8. User continues to have access until period end
9. At period end: Subscription canceled
10. Access revoked
```

**Email Sent:** Cancellation Confirmation
- Subject: "Subscription Cancellation Confirmed"
- Content: Access until date, reactivation link
- CTA: "Reactivate Subscription" (if user changes mind)

#### 4b. Cancel Immediately

**User Journey:**
```
1. User selects "Cancel immediately" option
   ↓
2. API: POST /api/dashboard/cancel-subscription-immediately
3. Stripe: Delete subscription
4. Database: Update status = 'canceled'
5. Email: Immediate Cancellation sent
   ↓
6. Access revoked immediately
7. User reverts to free tier (3 articles/month)
```

**Email Sent:** Immediate Cancellation
- Subject: "Subscription Canceled - The Daily Worker"
- Content: Access ended, free tier limits, resubscribe link
- CTA: "Resubscribe"

---

### 5. Reactivation Flow

**User Journey:**
```
1. User clicks "Reactivate" in dashboard
   OR clicks link in cancellation email
   ↓
2. API: POST /api/dashboard/reactivate-subscription
3. Stripe: Cancel the scheduled cancellation
4. Database: Update cancel_at_period_end = 0
5. Email: Reactivation Confirmation sent (placeholder)
   ↓
6. Subscription continues
7. Next billing date unchanged
```

**Note:** No email template for reactivation yet (Phase 7.6 scope)

---

### 6. Pause Flow (1-3 months)

**User Journey:**
```
1. User clicks "Pause Subscription" in dashboard
2. Selects pause duration (1-3 months)
   ↓
3. API: POST /api/dashboard/pause-subscription
4. Stripe: Set pause_collection with resumes_at date
5. Database: Update status = 'paused'
6. Email: Pause Confirmation sent (placeholder)
   ↓
7. No billing during pause period
8. Access reverts to free tier
9. At resume date: Subscription automatically resumes
```

**Note:** No email template for pause yet (Phase 7.6 scope)

---

## Email Templates

### Template: Subscription Confirmation

**File:** `backend/services/email_service.py::_render_subscription_confirmation`

**Variables:**
- `user_name`: User's name or email
- `plan_name`: "Basic Plan" or "Premium Plan"
- `amount_dollars`: "$15.00" or "$25.00"
- `next_billing_date`: "2026-02-01"

**Content Highlights:**
- Welcome message
- Plan details box (plan, amount, next billing)
- Benefits list (unlimited articles, sports, archive, local news)
- Link to start reading
- Link to account dashboard

---

### Template: Payment Receipt

**File:** `backend/services/email_service.py::_render_payment_receipt`

**Variables:**
- `user_name`
- `amount_dollars`
- `payment_date`
- `next_billing_date`
- `invoice_url`: Link to Stripe invoice

**Content Highlights:**
- Payment confirmation
- Payment details box
- Download invoice button
- Thank you message

---

### Template: Payment Failed

**File:** `backend/services/email_service.py::_render_payment_failed`

**Variables:**
- `user_name`
- `attempt_count`: 1-4
- `next_attempt_date`
- `update_payment_url`

**Content Highlights:**
- **Attempts 1-3**: Grace period message, retry info, green "access maintained" notice
- **Attempt 4+**: Canceled message, red "access revoked" notice, resubscribe instructions
- Prominent "Update Payment Method" button

---

### Template: Renewal Reminder

**File:** `backend/services/email_service.py::_render_renewal_reminder`

**Variables:**
- `user_name`
- `plan_name`
- `amount_dollars`
- `renewal_date`
- `days_until_renewal`: Always 7

**Content Highlights:**
- "Renewing in 7 days" message
- Renewal details box
- "No action needed" reassurance
- Links to update payment method, change plan, or cancel

---

### Template: Renewal Confirmation

**File:** `backend/services/email_service.py::_render_renewal_confirmation`

**Variables:**
- `user_name`
- `amount_dollars`
- `next_billing_date`

**Content Highlights:**
- Success message with green header
- Amount charged and next billing date
- Thank you for continued support

---

### Template: Cancellation Confirmation

**File:** `backend/services/email_service.py::_render_cancellation_confirmation`

**Variables:**
- `user_name`
- `access_until`: "2026-01-31"
- `reactivate_url`

**Content Highlights:**
- Cancellation confirmed
- Access until date in highlighted box
- Large green "Reactivate" button
- "Sorry to see you go" message
- Feedback invitation

---

## Customer Support Guide

### Common Support Scenarios

#### Scenario 1: "I didn't receive my confirmation email"

**Troubleshooting:**
1. Check spam/junk folder
2. Verify email address in account settings
3. Check SendGrid dashboard for delivery status
4. Resend email manually:
   ```bash
   # Access backend
   python -c "from backend.services.email_service import get_email_service; \
              service = get_email_service(); \
              service.send_subscription_confirmation(...)"
   ```

#### Scenario 2: "My payment failed but I have access - why?"

**Explanation:**
- Grace period: 3 retry attempts
- Access maintained during grace period
- Update payment method to avoid cancellation
- After 4th failed attempt, access will be revoked

**Action:**
- Direct user to account dashboard → Update Payment Method
- Verify payment method is valid
- Wait for next retry (automatic)

#### Scenario 3: "I canceled but still being charged"

**Investigation:**
1. Check subscription status in database:
   ```sql
   SELECT * FROM subscriptions WHERE user_id = ?;
   ```
2. Check Stripe subscription:
   - Look for `cancel_at_period_end` flag
   - Check if cancellation processed
3. Verify cancellation email was sent
4. Check if user reactivated (accidentally clicked link)

**Resolution:**
- If not canceled: Cancel via Stripe dashboard
- If wrongly charged: Process refund via Stripe
- Update database to match Stripe state

#### Scenario 4: "I want to change my plan"

**Process:**
- Cancel current subscription (at period end)
- At period end, resubscribe to new plan
- OR: Manually upgrade/downgrade in Stripe dashboard

**Note:** Plan changes not automated (Phase 7.6 scope)

#### Scenario 5: "Email quota exceeded"

**Symptoms:**
- Emails not sending
- Logs show: "Daily email quota exceeded"

**Resolution:**
1. Check current usage:
   ```python
   from backend.services.email_service import get_email_service
   service = get_email_service()
   print(f"Usage: {service.get_daily_usage()}/{service.daily_limit}")
   ```
2. If at limit (100 emails), wait until midnight UTC for reset
3. For urgent emails, upgrade SendGrid plan temporarily
4. Consider upgrading to paid SendGrid plan if quota frequently hit

---

## Technical Details

### Configuration

**Environment Variables:**
```bash
# Required
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxx

# Optional
FROM_EMAIL=noreply@thedailyworker.com
FROM_NAME="The Daily Worker"
```

### Getting SendGrid API Key

1. Sign up at https://sendgrid.com (free tier: 100 emails/day)
2. Go to Settings → API Keys
3. Create new API key with "Full Access"
4. Copy key and add to `.env` file
5. Verify sender email address in SendGrid dashboard

### Email Sending Workflow

```
User Action → Webhook Trigger → Database Update → Email Service
                                                         ↓
                                        1. Check quota (100/day)
                                        2. Validate email address
                                        3. Render template with context
                                        4. Create SendGrid Mail object
                                        5. Send via SendGrid API
                                        6. Log result + increment quota
```

### Quota Management

**Daily Reset:**
- Occurs at midnight UTC
- Automatic (no cron job needed)
- Tracked in-memory per EmailService instance

**Monitoring:**
```python
from backend.services.email_service import get_email_service

service = get_email_service()
print(service.get_daily_usage())  # Current count
print(service.daily_limit)         # 100
```

**Over Quota Behavior:**
- Email rejected before SendGrid API call
- Returns `False` from `send_email()`
- Logged as error: "Daily email quota exceeded"

### Testing Email System

**Unit Tests:**
```bash
cd backend
PYTHONPATH=/path/to/DWnews python3 -m pytest tests/test_email_service.py -v
```

**Manual Testing (without SendGrid):**
```python
# Emails will be logged instead of sent when SENDGRID_API_KEY not set
from backend.services.email_service import EmailService
import os

# Remove API key to test logging
del os.environ['SENDGRID_API_KEY']

# This will raise ValueError - expected
try:
    service = EmailService()
except ValueError as e:
    print(f"Expected error: {e}")
```

**Manual Testing (with SendGrid):**
```python
from backend.services.email_service import get_email_service

service = get_email_service()

# Test subscription confirmation
service.send_subscription_confirmation(
    to_email="your-test-email@example.com",
    user_name="Test User",
    plan_name="Basic Plan",
    amount_dollars="15.00",
    next_billing_date="2026-02-01"
)

# Check your inbox!
```

### Webhook Integration

**Stripe Webhooks → Email Triggers:**

| Webhook Event | Handler | Email Sent |
|---------------|---------|------------|
| `checkout.session.completed` | `handle_checkout_completed()` | Subscription Confirmation |
| `invoice.paid` (initial) | `handle_invoice_paid()` | Payment Receipt |
| `invoice.paid` (recurring) | `handle_invoice_paid()` | Renewal Confirmation |
| `invoice.payment_failed` | `handle_invoice_payment_failed()` | Payment Failed |

**File:** `backend/routes/payments.py`

**Example Flow:**
```python
async def handle_checkout_completed(session: dict, db: Session):
    # 1. Extract data from Stripe session
    # 2. Update database
    # 3. Send confirmation email
    email_service = get_email_service()
    email_service.send_subscription_confirmation(...)
```

---

## Maintenance & Monitoring

### Daily Checks

1. **Email Quota Usage**
   ```bash
   # Check logs for quota warnings
   grep "quota exceeded" backend/logs/app.log
   ```

2. **Failed Emails**
   ```bash
   # Check logs for send failures
   grep "Failed to send email" backend/logs/app.log
   ```

3. **SendGrid Dashboard**
   - Visit https://app.sendgrid.com/statistics
   - Monitor delivery rate, bounces, spam reports

### Weekly Checks

1. **Bounce Rate** (should be <5%)
2. **Spam Report Rate** (should be <0.1%)
3. **Email Deliverability Score**

### Monthly Checks

1. **Review quota usage trends**
2. **Evaluate need for paid SendGrid plan**
3. **Test all email templates with real data**
4. **Update email content if needed**

---

## Troubleshooting

### Issue: Emails not sending

**Diagnosis:**
1. Check SENDGRID_API_KEY is set: `echo $SENDGRID_API_KEY`
2. Check SendGrid API key is valid (test in SendGrid dashboard)
3. Check daily quota: `service.get_daily_usage()`
4. Check logs: `tail -f backend/logs/app.log`

**Resolution:**
- Invalid API key: Regenerate in SendGrid dashboard
- Over quota: Wait for reset or upgrade plan
- Network error: Check internet connection, firewall

### Issue: Emails going to spam

**Diagnosis:**
1. Check SPF/DKIM records configured in SendGrid
2. Verify sender domain authentication
3. Check email content for spam triggers

**Resolution:**
- Authenticate sender domain (thedailyworker.com)
- Add SPF and DKIM records to DNS
- Review email content for spam keywords
- Enable link tracking in SendGrid

### Issue: Template rendering errors

**Diagnosis:**
```python
# Test template rendering
service = get_email_service()
try:
    result = service.render_template("subscription_confirmation", {
        "user_name": "Test",
        "plan_name": "Basic",
        "amount_dollars": "15.00",
        "next_billing_date": "2026-02-01"
    })
    print(result)
except Exception as e:
    print(f"Error: {e}")
```

**Resolution:**
- Missing variable: Add to context dict
- Invalid template: Check template exists in `render_template()` mapping
- Syntax error: Review template HTML in `_render_*()` methods

---

## Future Enhancements (Post Phase 7.6)

1. **Additional Templates:**
   - Pause confirmation
   - Resume confirmation
   - Reactivation confirmation
   - Plan upgrade/downgrade

2. **Email Features:**
   - Personalized recommendations
   - Weekly digest emails
   - Breaking news alerts
   - Custom user preferences (opt-in/opt-out)

3. **Advanced Functionality:**
   - A/B testing email templates
   - Email analytics (open rates, click rates)
   - Automated drip campaigns
   - Welcome email series for new subscribers

4. **SendGrid Advanced Features:**
   - Transactional email templates (stored in SendGrid)
   - Email scheduling
   - Unsubscribe management
   - Suppression lists

---

## Related Documentation

- [Stripe Payment Integration](../PHASE_7.2_COMPLETION_SUMMARY.md)
- [Subscription Management](../DASHBOARD_TESTING.md)
- [API Endpoints](../backend/routes/payments.py)
- [Email Service Code](../backend/services/email_service.py)

---

**Document Version:** 1.0
**Last Updated:** 2026-01-02
**Phase:** 7.6 - Email Notifications & Testing
**Author:** TDD Development Agent
