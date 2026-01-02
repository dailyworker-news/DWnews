# Stripe Payment Integration Documentation

**Phase 7.2: Stripe Payment Integration**
**Date:** 2026-01-01
**Status:** Complete

---

## Overview

The Daily Worker uses Stripe for subscription payment processing. This document covers API endpoints, webhook handling, testing procedures, and deployment configuration.

**Business Model:**
- **Free Tier:** 3 articles/month, 5-day archive
- **Basic Plan:** $15/month - Unlimited articles, 10-day archive, 1 sports league
- **Premium Plan:** $25/month - Unlimited articles, full archive, unlimited sports leagues

**Stripe Integration Features:**
- Subscription checkout via Stripe Checkout
- Webhook event processing (automated subscription updates)
- Customer Portal for self-service billing management
- Test mode support for development
- Production-ready error handling and logging

---

## API Endpoints

### Base URL
- **Local Development:** `http://localhost:8000/api/payments`
- **Production:** `https://dailyworker.com/api/payments`

---

### 1. Create Subscription Checkout Session

**Endpoint:** `POST /api/payments/subscribe`

**Description:** Creates a Stripe Checkout session for subscription signup

**Request Body:**
```json
{
  "plan_id": "basic",
  "email": "user@example.com",
  "success_url": "https://dailyworker.com/subscription-success?session_id={CHECKOUT_SESSION_ID}",
  "cancel_url": "https://dailyworker.com/subscription-cancel"
}
```

**Parameters:**
- `plan_id` (required): `"basic"` or `"premium"`
- `email` (required): Valid email address
- `success_url` (optional): Redirect URL after successful payment (default: `/subscription-success`)
- `cancel_url` (optional): Redirect URL if user cancels (default: `/subscription-cancel`)

**Response (200 OK):**
```json
{
  "session_id": "cs_test_a1b2c3d4e5f6...",
  "session_url": "https://checkout.stripe.com/pay/cs_test_...",
  "publishable_key": "pk_test_51Sl2gK..."
}
```

**Usage:**
```javascript
// Frontend example
const response = await fetch('/api/payments/subscribe', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    plan_id: 'basic',
    email: 'user@example.com'
  })
});

const { session_url } = await response.json();
window.location.href = session_url;  // Redirect to Stripe Checkout
```

**Error Responses:**
- `400 Bad Request`: Invalid plan_id or Stripe API error
- `422 Unprocessable Entity`: Invalid email format
- `500 Internal Server Error`: Server error

---

### 2. Create Customer Portal Session

**Endpoint:** `POST /api/payments/customer-portal`

**Description:** Creates a Stripe Customer Portal session for managing subscription

**Request Body:**
```json
{
  "customer_id": "cus_NffrFeUfNV2Hib",
  "return_url": "https://dailyworker.com/account/subscription"
}
```

**Parameters:**
- `customer_id` (required): Stripe customer ID
- `return_url` (optional): URL to return to after portal session (default: `/account/subscription`)

**Response (200 OK):**
```json
{
  "portal_url": "https://billing.stripe.com/session/test_..."
}
```

**Usage:**
```javascript
// Frontend example
const response = await fetch('/api/payments/customer-portal', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    customer_id: user.stripe_customer_id
  })
});

const { portal_url } = await response.json();
window.location.href = portal_url;  // Redirect to Stripe Customer Portal
```

**Customer Portal Features:**
- Update payment method
- Cancel subscription
- View invoice history
- Download receipts

---

### 3. Stripe Webhook Handler

**Endpoint:** `POST /api/payments/webhooks/stripe`

**Description:** Receives and processes Stripe webhook events

**Headers:**
- `stripe-signature`: Webhook signature (required for verification)

**Webhook Events Handled:**
1. `checkout.session.completed` - User completed subscription signup
2. `invoice.paid` - Subscription payment succeeded
3. `invoice.payment_failed` - Payment failed
4. `customer.subscription.updated` - Subscription status changed
5. `customer.subscription.deleted` - Subscription canceled

**Security:**
- Verifies webhook signature using `STRIPE_WEBHOOK_SECRET`
- Rejects unsigned or invalid webhooks (400 Bad Request)

**Configuration:**
Set up webhook endpoint in Stripe Dashboard:
```
URL: https://dailyworker.com/api/payments/webhooks/stripe
Events to send: All subscription and invoice events
```

**Testing Webhooks Locally:**
Use Stripe CLI to forward webhooks to localhost:
```bash
stripe listen --forward-to localhost:8000/api/payments/webhooks/stripe
```

---

### 4. Get Subscription Plans

**Endpoint:** `GET /api/payments/plans`

**Description:** Returns available subscription plans with pricing and features

**Response (200 OK):**
```json
{
  "plans": [
    {
      "id": "free",
      "name": "Free",
      "price_cents": 0,
      "billing_interval": "monthly",
      "features": {
        "article_limit": 3,
        "archive_days": 5,
        "sports_leagues": 0,
        "local_news": false
      }
    },
    {
      "id": "basic",
      "name": "Basic",
      "price_cents": 1500,
      "billing_interval": "monthly",
      "features": {
        "article_limit": null,
        "archive_days": 10,
        "sports_leagues": 1,
        "local_news": true
      }
    },
    {
      "id": "premium",
      "name": "Premium",
      "price_cents": 2500,
      "billing_interval": "monthly",
      "features": {
        "article_limit": null,
        "archive_days": null,
        "sports_leagues": null,
        "local_news": true
      }
    }
  ]
}
```

---

### 5. Get Stripe Configuration

**Endpoint:** `GET /api/payments/config`

**Description:** Returns Stripe publishable key for frontend (safe for client-side)

**Response (200 OK):**
```json
{
  "publishable_key": "pk_test_51Sl2gK...",
  "country": "US",
  "currency": "usd"
}
```

---

### 6. Payment Health Check

**Endpoint:** `GET /api/payments/health`

**Description:** Health check for payment system

**Response (200 OK):**
```json
{
  "status": "healthy",
  "stripe_configured": true,
  "webhook_configured": true
}
```

---

## Webhook Event Processing

### Event Flow

```
User Action → Stripe → Webhook Event → Database Update
```

**Example: Successful Subscription Signup**

1. User completes checkout → Stripe sends `checkout.session.completed` event
2. Webhook handler processes event:
   - Extracts customer_id, subscription_id, email
   - Creates/updates user record
   - Creates subscription record
   - Logs subscription_event
3. User status updated to `active`

---

### Webhook Event Handlers

#### 1. `checkout.session.completed`
**Triggered:** User completes subscription checkout

**Actions:**
- Find or create user by email
- Create subscription record with `stripe_subscription_id`
- Update `user.subscription_status = 'active'`
- Log subscription event

**Event Data:**
```json
{
  "customer": "cus_...",
  "subscription": "sub_...",
  "customer_details": { "email": "user@example.com" }
}
```

---

#### 2. `invoice.paid`
**Triggered:** Subscription payment succeeded (monthly renewal)

**Actions:**
- Find subscription by `stripe_subscription_id`
- Update `subscription.current_period_end`
- Create invoice record
- Update `user.subscription_status = 'active'`
- Log subscription event

**Event Data:**
```json
{
  "subscription": "sub_...",
  "customer": "cus_...",
  "amount_paid": 1500
}
```

---

#### 3. `invoice.payment_failed`
**Triggered:** Payment failed (expired card, insufficient funds)

**Actions:**
- Find subscription by `stripe_subscription_id`
- Update `subscription.status = 'past_due'`
- Update `user.subscription_status = 'past_due'`
- Log subscription event
- Send notification email (future enhancement)

**Event Data:**
```json
{
  "subscription": "sub_...",
  "customer": "cus_..."
}
```

**Grace Period:**
- User retains access for 3 days
- Stripe automatically retries payment
- If payment succeeds during grace period, status returns to `active`

---

#### 4. `customer.subscription.updated`
**Triggered:** Subscription status changed (upgraded, downgraded, canceled)

**Actions:**
- Find subscription by `stripe_subscription_id`
- Update `subscription.status`
- Update `subscription.current_period_start/end`
- Update `user.subscription_status`
- Log subscription event

**Event Data:**
```json
{
  "id": "sub_...",
  "status": "active",
  "current_period_start": 1672531200,
  "current_period_end": 1675209600
}
```

---

#### 5. `customer.subscription.deleted`
**Triggered:** Subscription canceled (immediate or at period end)

**Actions:**
- Find subscription by `stripe_subscription_id`
- Update `subscription.status = 'canceled'`
- Update `subscription.canceled_at`
- Update `user.subscription_status = 'canceled'`
- Log subscription event

**Event Data:**
```json
{
  "id": "sub_...",
  "customer": "cus_..."
}
```

---

## Testing

### Test Cards

Use these test card numbers in Stripe test mode:

| Scenario | Card Number | Description |
|----------|-------------|-------------|
| **Success** | `4242 4242 4242 4242` | Payment succeeds |
| **Decline** | `4000 0000 0000 0002` | Card declined |
| **Auth Required** | `4000 0025 0000 3155` | Requires authentication |
| **Insufficient Funds** | `4000 0000 0000 9995` | Insufficient funds |
| **Expired Card** | `4000 0000 0000 0069` | Expired card |
| **Incorrect CVC** | `4000 0000 0000 0127` | Incorrect CVC |
| **Processing Error** | `4000 0000 0000 0119` | Generic processing error |

**Test Card Details:**
- **Expiration:** Any future date (e.g., 12/34)
- **CVC:** Any 3 digits (e.g., 123)
- **ZIP:** Any 5 digits (e.g., 12345)

---

### Running Tests

**Unit Tests:**
```bash
cd /Users/home/sandbox/daily_worker/projects/DWnews/backend
python -m pytest tests/test_stripe_integration.py -v
```

**Test Coverage:**
- ✅ Checkout session creation (new customer)
- ✅ Checkout session creation (existing customer)
- ✅ Invalid plan ID validation
- ✅ Invalid email validation
- ✅ Stripe API error handling
- ✅ Customer Portal session creation
- ✅ All webhook event handlers
- ✅ Webhook signature verification
- ✅ Invalid payload/signature handling
- ✅ Utility endpoints (plans, config, health)
- ✅ Complete signup flow integration

**Test Results:**
```
test_stripe_integration.py::TestCheckoutSession::test_create_checkout_session_new_customer PASSED
test_stripe_integration.py::TestCheckoutSession::test_create_checkout_session_existing_customer PASSED
test_stripe_integration.py::TestCheckoutSession::test_create_checkout_session_invalid_plan PASSED
test_stripe_integration.py::TestCheckoutSession::test_create_checkout_session_invalid_email PASSED
test_stripe_integration.py::TestCheckoutSession::test_create_checkout_session_stripe_error PASSED
test_stripe_integration.py::TestCustomerPortal::test_create_portal_session PASSED
test_stripe_integration.py::TestCustomerPortal::test_create_portal_session_with_return_url PASSED
test_stripe_integration.py::TestCustomerPortal::test_create_portal_session_stripe_error PASSED
test_stripe_integration.py::TestStripeWebhooks::test_webhook_checkout_completed PASSED
test_stripe_integration.py::TestStripeWebhooks::test_webhook_invoice_paid PASSED
test_stripe_integration.py::TestStripeWebhooks::test_webhook_invoice_payment_failed PASSED
test_stripe_integration.py::TestStripeWebhooks::test_webhook_subscription_updated PASSED
test_stripe_integration.py::TestStripeWebhooks::test_webhook_subscription_deleted PASSED
test_stripe_integration.py::TestStripeWebhooks::test_webhook_invalid_signature PASSED
test_stripe_integration.py::TestStripeWebhooks::test_webhook_invalid_payload PASSED
test_stripe_integration.py::TestUtilityEndpoints::test_get_subscription_plans PASSED
test_stripe_integration.py::TestUtilityEndpoints::test_get_stripe_config PASSED
test_stripe_integration.py::TestUtilityEndpoints::test_payments_health_check_healthy PASSED
test_stripe_integration.py::TestUtilityEndpoints::test_payments_health_check_unhealthy PASSED
test_stripe_integration.py::TestPaymentFlowIntegration::test_complete_signup_flow PASSED

20 tests PASSED
```

---

### Manual Testing Workflow

**1. Test Successful Subscription:**
```bash
# Start backend
cd /Users/home/sandbox/daily_worker/projects/DWnews/backend
python main.py

# In another terminal, test checkout endpoint
curl -X POST http://localhost:8000/api/payments/subscribe \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "basic", "email": "test@example.com"}'

# Response will contain session_url - open in browser
# Use test card: 4242 4242 4242 4242
# Complete checkout
```

**2. Test Customer Portal:**
```bash
# Get customer_id from Stripe Dashboard or previous checkout
curl -X POST http://localhost:8000/api/payments/customer-portal \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "cus_..."}'

# Open portal_url in browser
# Update payment method, cancel subscription, etc.
```

**3. Test Webhook Events:**
```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login to Stripe
stripe login

# Forward webhooks to localhost
stripe listen --forward-to localhost:8000/api/payments/webhooks/stripe

# Trigger test webhook
stripe trigger checkout.session.completed
```

---

## Environment Configuration

### Required Environment Variables

**`.env` file:**
```bash
# Stripe API Keys (Sandbox/Test Mode)
STRIPE_PUBLISHABLE_KEY=pk_test_51Sl2gKGkPAPOHrjL...
STRIPE_SECRET_KEY=sk_test_51Sl2gKGkPAPOHrjL...
STRIPE_WEBHOOK_SECRET=whsec_...

# Server Configuration
BACKEND_HOST=localhost
BACKEND_PORT=8000
FRONTEND_HOST=localhost
FRONTEND_PORT=3000
```

**Getting Stripe Keys:**
1. Create Stripe account: https://dashboard.stripe.com/register
2. Activate account (may require business details)
3. Navigate to: Developers → API Keys
4. Copy **Publishable key** and **Secret key**
5. For webhook secret:
   - Go to: Developers → Webhooks
   - Add endpoint: `https://yourdomain.com/api/payments/webhooks/stripe`
   - Select events: All subscription and invoice events
   - Copy **Signing secret**

**Production vs. Test Mode:**
- Test mode keys start with: `pk_test_...` and `sk_test_...`
- Production keys start with: `pk_live_...` and `sk_live_...`
- Always use test mode for development/staging
- Only use production keys in production environment

---

## Error Handling & Logging

### Error Scenarios

**1. Stripe API Errors:**
```python
except stripe.error.StripeError as e:
    logger.error(f"Stripe API error: {str(e)}", exc_info=True)
    raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
```

**2. Webhook Signature Verification Errors:**
```python
except stripe.error.SignatureVerificationError as e:
    logger.error(f"Invalid webhook signature: {str(e)}")
    raise HTTPException(status_code=400, detail="Invalid signature")
```

**3. Database Errors:**
```python
except Exception as e:
    logger.error(f"Database error: {str(e)}", exc_info=True)
    raise HTTPException(status_code=500, detail="Database error")
```

### Logging

**Log Levels:**
- `INFO`: Successful operations (checkout created, webhook processed)
- `WARNING`: Non-critical issues (payment failed, subscription canceled)
- `ERROR`: Critical errors (Stripe API failure, database error, webhook signature failure)

**Log Examples:**
```
INFO: Created Stripe Checkout session cs_test_123 for test@example.com (basic plan)
INFO: Processing webhook event: invoice.paid (ID: evt_123)
WARNING: Invoice payment failed: subscription=sub_123, customer=cus_123
ERROR: Stripe API error: Invalid API key provided
```

**Log Storage:**
- Local: `./logs/dwnews.log`
- Production: Cloud Logging (GCP Stackdriver)

---

## Security Best Practices

### 1. API Key Security
- ✅ Store keys in environment variables (`.env`)
- ✅ Never commit API keys to git
- ✅ Use test keys in development
- ✅ Rotate keys if compromised
- ✅ Use GCP Secret Manager in production

### 2. Webhook Security
- ✅ Verify webhook signatures (prevents spoofing)
- ✅ Use HTTPS in production (required by Stripe)
- ✅ Implement idempotency (handle duplicate events)
- ✅ Log all webhook events for audit trail

### 3. PCI Compliance
- ✅ Never store card numbers (Stripe handles this)
- ✅ Use Stripe Checkout (PCI-compliant hosted page)
- ✅ Use Customer Portal (PCI-compliant self-service)
- ❌ Never request CVV/CVC on your own forms

### 4. Data Protection
- ✅ Store only Stripe IDs (customer_id, subscription_id)
- ✅ Encrypt database in production
- ✅ Use HTTPS for all API calls
- ✅ Implement rate limiting on payment endpoints

---

## Deployment Checklist

### Pre-Production
- [ ] Replace test Stripe keys with production keys
- [ ] Generate webhook secret for production endpoint
- [ ] Configure webhook endpoint in Stripe Dashboard
- [ ] Test webhook delivery to production URL
- [ ] Enable HTTPS/SSL (required by Stripe)
- [ ] Set up monitoring and alerting
- [ ] Configure error tracking (Sentry, Rollbar)
- [ ] Review and update pricing in Stripe Dashboard
- [ ] Test complete signup flow in production

### Production Environment Variables
```bash
STRIPE_PUBLISHABLE_KEY=pk_live_...  # Production publishable key
STRIPE_SECRET_KEY=sk_live_...       # Production secret key
STRIPE_WEBHOOK_SECRET=whsec_...     # Production webhook secret
```

### Post-Deployment
- [ ] Monitor webhook event delivery (Stripe Dashboard)
- [ ] Monitor error logs for payment failures
- [ ] Set up billing alerts (revenue, failed payments)
- [ ] Test subscription cancellation flow
- [ ] Test payment method update flow
- [ ] Verify email notifications (future enhancement)

---

## Troubleshooting

### Issue: Webhook events not received

**Symptoms:** Subscriptions created in Stripe but not reflected in database

**Solutions:**
1. Check webhook endpoint URL in Stripe Dashboard
2. Verify webhook secret matches `.env` file
3. Check webhook event logs in Stripe Dashboard
4. Test webhook signature verification locally
5. Ensure HTTPS is enabled (production)

**Debug:**
```bash
# Check webhook logs in Stripe Dashboard
# Events → View logs → Filter by endpoint

# Test webhook locally
stripe listen --forward-to localhost:8000/api/payments/webhooks/stripe
stripe trigger checkout.session.completed
```

---

### Issue: Checkout session creation fails

**Symptoms:** 400 Bad Request when calling `/api/payments/subscribe`

**Solutions:**
1. Verify Stripe API keys are correct
2. Check plan_id is valid (`basic` or `premium`)
3. Verify email format is valid
4. Check Stripe API status (status.stripe.com)

**Debug:**
```bash
# Check Stripe API logs
# Developers → Logs → Filter by API request

# Test API key
curl https://api.stripe.com/v1/customers \
  -u sk_test_YOUR_SECRET_KEY: \
  -d "email=test@example.com"
```

---

### Issue: Customer Portal session fails

**Symptoms:** 400 Bad Request when calling `/api/payments/customer-portal`

**Solutions:**
1. Verify customer_id exists in Stripe
2. Ensure customer has active subscription
3. Check Stripe API key permissions

**Debug:**
```bash
# List customers
stripe customers list --limit 10

# Retrieve specific customer
stripe customers retrieve cus_...
```

---

## Future Enhancements

### Phase 7.3+: Additional Features
- [ ] Email notifications (subscription confirmation, payment failed, renewal reminder)
- [ ] Grace period for failed payments (3-day access retention)
- [ ] Subscription pause/resume functionality
- [ ] Annual billing option (discount for annual plans)
- [ ] Promotional codes and discounts
- [ ] Refund handling
- [ ] Invoice PDF generation
- [ ] Subscription analytics dashboard

---

## Support & Resources

**Stripe Documentation:**
- API Reference: https://stripe.com/docs/api
- Checkout: https://stripe.com/docs/payments/checkout
- Webhooks: https://stripe.com/docs/webhooks
- Customer Portal: https://stripe.com/docs/billing/subscriptions/customer-portal
- Testing: https://stripe.com/docs/testing

**The Daily Worker Resources:**
- Backend code: `/backend/routes/payments.py`
- Test suite: `/backend/tests/test_stripe_integration.py`
- Database schema: `/database/migrations/003_subscription_schema.sql`
- Roadmap: `/plans/roadmap.md` (Phase 7.2)

**Contact:**
- Development Issues: GitHub Issues
- Payment Issues: Check Stripe Dashboard first
- Emergency: Rollback deployment, investigate logs

---

**Document Version:** 1.0
**Last Updated:** 2026-01-01
**Phase:** 7.2 Complete
**Status:** Production-Ready
