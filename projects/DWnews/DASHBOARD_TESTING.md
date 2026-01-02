# Dashboard Testing Guide
Phase 7.4: Subscriber Dashboard & User Preferences

## Overview
This document provides comprehensive testing instructions for the subscriber dashboard and user preferences features.

## Backend API Endpoints

### 1. GET /api/dashboard/subscription
**Purpose:** Get user's subscription details

**Authentication:** Required (JWT token in cookie)

**Test Cases:**

#### Free Tier User
```bash
# Register a free tier user first
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test-free@example.com",
    "password": "password123",
    "username": "test_free"
  }' \
  -c cookies.txt

# Get subscription status
curl -X GET http://localhost:8000/api/dashboard/subscription \
  -b cookies.txt

# Expected Response:
{
  "status": "free",
  "plan_name": "Free",
  "plan_id": "free",
  "price_cents": 0,
  "billing_interval": null,
  "next_billing_date": null,
  ...
}
```

#### Basic Tier User
```bash
# Create a Basic tier subscription via Stripe checkout first
# Then test the endpoint
curl -X GET http://localhost:8000/api/dashboard/subscription \
  -b cookies-basic.txt

# Expected Response:
{
  "status": "active",
  "plan_name": "Basic Subscriber",
  "plan_id": "basic",
  "price_cents": 1500,
  "billing_interval": "monthly",
  "next_billing_date": "2026-02-01T00:00:00",
  "payment_method_brand": "visa",
  "payment_method_last4": "4242",
  ...
}
```

#### Premium Tier User
```bash
# Create a Premium tier subscription via Stripe checkout first
curl -X GET http://localhost:8000/api/dashboard/subscription \
  -b cookies-premium.txt

# Expected Response:
{
  "status": "active",
  "plan_name": "Premium Subscriber",
  "plan_id": "premium",
  "price_cents": 2500,
  ...
}
```

### 2. GET /api/dashboard/invoices
**Purpose:** Get user's invoice history

**Test:**
```bash
curl -X GET http://localhost:8000/api/dashboard/invoices \
  -b cookies.txt

# Expected Response:
{
  "invoices": [
    {
      "id": "in_1234567890",
      "amount_cents": 1500,
      "status": "paid",
      "created_at": "2026-01-01T00:00:00",
      "paid_at": "2026-01-01T00:05:00",
      "invoice_url": "https://invoice.stripe.com/...",
      "invoice_pdf": "https://invoice.stripe.com/.../pdf"
    }
  ]
}
```

### 3. POST /api/dashboard/customer-portal
**Purpose:** Generate Stripe Customer Portal session

**Test:**
```bash
curl -X POST http://localhost:8000/api/dashboard/customer-portal \
  -H "Content-Type: application/json" \
  -d '{
    "return_url": "http://localhost:8080/dashboard.html"
  }' \
  -b cookies.txt

# Expected Response:
{
  "portal_url": "https://billing.stripe.com/session/..."
}
```

### 4. GET /api/dashboard/preferences
**Purpose:** Get user's preferences

**Test:**
```bash
curl -X GET http://localhost:8000/api/dashboard/preferences \
  -b cookies.txt

# Expected Response:
{
  "sports_leagues": [1, 3, 5],
  "local_region": "New York, NY"
}
```

### 5. PUT /api/dashboard/preferences
**Purpose:** Update user's preferences

**Test Cases:**

#### Free Tier (Should Fail for Sports)
```bash
curl -X PUT http://localhost:8000/api/dashboard/preferences \
  -H "Content-Type: application/json" \
  -d '{
    "sports_leagues": [1],
    "local_region": "Chicago, IL"
  }' \
  -b cookies-free.txt

# Expected Response (403 Forbidden):
{
  "detail": "Free tier users cannot select sports leagues. Please upgrade to Basic or Premium."
}
```

#### Basic Tier (Max 1 League)
```bash
# Valid: 1 league
curl -X PUT http://localhost:8000/api/dashboard/preferences \
  -H "Content-Type: application/json" \
  -d '{
    "sports_leagues": [2],
    "local_region": "Los Angeles, CA"
  }' \
  -b cookies-basic.txt

# Expected Response (200 OK):
{
  "message": "Preferences updated successfully",
  "sports_leagues": [2],
  "local_region": "Los Angeles, CA"
}

# Invalid: 2 leagues
curl -X PUT http://localhost:8000/api/dashboard/preferences \
  -H "Content-Type: application/json" \
  -d '{
    "sports_leagues": [1, 2],
    "local_region": "Los Angeles, CA"
  }' \
  -b cookies-basic.txt

# Expected Response (403 Forbidden):
{
  "detail": "Basic tier users can only select 1 sports league. Upgrade to Premium for unlimited leagues."
}
```

#### Premium Tier (Unlimited Leagues)
```bash
curl -X PUT http://localhost:8000/api/dashboard/preferences \
  -H "Content-Type: application/json" \
  -d '{
    "sports_leagues": [1, 2, 3, 4, 5, 7, 8, 9, 10],
    "local_region": "Boston, MA"
  }' \
  -b cookies-premium.txt

# Expected Response (200 OK):
{
  "message": "Preferences updated successfully",
  "sports_leagues": [1, 2, 3, 4, 5, 7, 8, 9, 10],
  "local_region": "Boston, MA"
}
```

### 6. GET /api/dashboard/sports-leagues
**Purpose:** List all available sports leagues

**Test:**
```bash
curl -X GET http://localhost:8000/api/dashboard/sports-leagues

# Expected Response:
{
  "leagues": [
    {
      "id": 1,
      "league_code": "EPL",
      "name": "English Premier League",
      "country": "England",
      "tier_requirement": "basic"
    },
    {
      "id": 2,
      "league_code": "NBA",
      "name": "National Basketball Association",
      "country": "USA",
      "tier_requirement": "basic"
    },
    ...
  ]
}
```

### 7. POST /api/dashboard/cancel-subscription
**Purpose:** Cancel user's subscription (at period end)

**Test:**
```bash
curl -X POST http://localhost:8000/api/dashboard/cancel-subscription \
  -b cookies-basic.txt

# Expected Response:
{
  "message": "Subscription will be canceled at the end of the billing period",
  "cancel_at": 1738454400,
  "access_until": "2026-02-01T00:00:00"
}
```

## Frontend Testing

### Dashboard Page Access

1. **Navigate to Dashboard:**
   - Open browser: http://localhost:8080/dashboard.html
   - If not authenticated, should redirect to /login.html

2. **Free Tier User Dashboard:**
   - Login as free tier user
   - Navigate to /dashboard.html
   - **Verify:**
     - Plan badge shows "Free"
     - Status shows "Free Account" (gray dot)
     - Subscription details show "5 days of articles"
     - Upgrade buttons visible (Basic and Premium)
     - Billing section is hidden
     - Sports leagues section shows upgrade notice
     - Local region input is editable

3. **Basic Tier User Dashboard:**
   - Login as Basic tier user
   - **Verify:**
     - Plan badge shows "Basic Subscriber" (blue)
     - Status shows "Active" (green dot)
     - Price shows "$15.00/monthly"
     - Next billing date is displayed
     - Payment method shows card brand and last 4 digits
     - Cancel subscription button visible
     - Invoice history table populated
     - Sports leagues: Radio buttons (select 1 league only)
     - Premium-only leagues are disabled with "Premium Only" badge
     - Local region input is editable

4. **Premium Tier User Dashboard:**
   - Login as Premium tier user
   - **Verify:**
     - Plan badge shows "Premium Subscriber" (gold)
     - Status shows "Active" (green dot)
     - Price shows "$25.00/monthly"
     - Sports leagues: Checkboxes (select unlimited)
     - All leagues are enabled (including premium-only)
     - Can select multiple leagues

### User Preference Updates

#### Test 1: Save Sports Preferences (Basic Tier)
1. Login as Basic tier user
2. Select 1 sports league (e.g., NBA)
3. Click "Save Preferences"
4. **Verify:**
   - Success message appears: "✓ Preferences saved successfully!"
   - Page does not reload
   - Selected league remains checked

#### Test 2: Attempt Multiple Leagues (Basic Tier)
1. Try to select 2 leagues (if using radio buttons, this should be prevented)
2. If using checkboxes in error, click Save
3. **Verify:**
   - Error message appears: "Basic tier users can only select 1 sports league..."

#### Test 3: Save Sports Preferences (Premium Tier)
1. Login as Premium tier user
2. Select multiple leagues (e.g., NBA, NFL, EPL, Champions League)
3. Enter local region: "Seattle, WA"
4. Click "Save Preferences"
5. **Verify:**
   - Success message appears
   - All selections preserved

#### Test 4: Update Local Region Only
1. Leave sports leagues unchanged
2. Update local region to "Portland, OR"
3. Click "Save Preferences"
4. **Verify:**
   - Success message appears
   - Local region updated

### Payment Method Management

#### Test 1: Update Payment Method
1. Login as subscribed user (Basic or Premium)
2. Click "Update Payment Method" button
3. **Verify:**
   - New tab/window opens to Stripe Customer Portal
   - Portal shows current payment method
   - Can add/update payment method
   - Return URL redirects back to dashboard

#### Test 2: View Invoice
1. Click "View" button on an invoice
2. **Verify:**
   - Opens Stripe invoice page in new tab
   - Shows invoice details

#### Test 3: Download Invoice PDF
1. Click "Download PDF" button
2. **Verify:**
   - PDF downloads to computer
   - PDF contains invoice details

### Subscription Cancellation

#### Test 1: Cancel Subscription
1. Login as subscribed user
2. Click "Cancel Subscription" button
3. **Verify:**
   - Modal opens with confirmation message
   - Modal shows cancellation end date (end of billing period)
   - "Yes, Cancel Subscription" button is red/danger styled
   - "Keep Subscription" button closes modal

4. Click "Yes, Cancel Subscription"
5. **Verify:**
   - Modal closes
   - Toast notification appears: "Subscription canceled. Access until [date]"
   - Status indicator updates to "Canceled"
   - "Cancels On" date appears in subscription details
   - Cancel button replaced with "Reactivate Subscription" button

#### Test 2: Keep Subscription
1. Click "Cancel Subscription"
2. Click "Keep Subscription" in modal
3. **Verify:**
   - Modal closes
   - No changes to subscription status

#### Test 3: Reactivate Subscription
1. After canceling, click "Reactivate Subscription"
2. **Verify:**
   - Opens Stripe Customer Portal
   - User can reactivate subscription via portal

### Mobile Responsive Testing

1. **Open dashboard on mobile device or resize browser to 375px width**
2. **Verify:**
   - All sections stack vertically
   - Buttons expand to full width
   - Invoice table converts to single-column layout
   - Sports leagues grid shows one column
   - Modal is responsive and scrollable
   - No horizontal scrolling required

### Error Handling

#### Test 1: Network Error
1. Stop backend server
2. Reload dashboard
3. **Verify:**
   - Error state appears: "Failed to load dashboard"
   - "Retry" button is visible
   - Clicking "Retry" reloads page

#### Test 2: Invalid API Response
1. Mock a 500 error from backend
2. **Verify:**
   - Appropriate error message appears
   - User can retry or navigate away

## Database Verification

### Verify Preferences Saved
```sql
-- Check user's local region
SELECT id, email, local_region FROM users WHERE email = 'test@example.com';

-- Check user's sports preferences
SELECT u.email, sl.name as league_name, usp.enabled
FROM user_sports_preferences usp
JOIN users u ON usp.user_id = u.id
JOIN sports_leagues sl ON usp.league_id = sl.id
WHERE u.email = 'test@example.com';
```

### Verify Subscription Status
```sql
-- Check subscription record
SELECT
    s.id,
    u.email,
    sp.plan_name,
    s.status,
    s.current_period_end,
    s.cancel_at_period_end
FROM subscriptions s
JOIN users u ON s.user_id = u.id
JOIN subscription_plans sp ON s.plan_id = sp.id
WHERE u.email = 'test@example.com';
```

## Test Completion Checklist

- [ ] Free tier user can view dashboard (no subscriptions section)
- [ ] Free tier user sees upgrade notices for sports leagues
- [ ] Free tier user can save local region preference
- [ ] Free tier user cannot select sports leagues
- [ ] Basic tier user can view subscription status
- [ ] Basic tier user can view billing information
- [ ] Basic tier user can select 1 sports league
- [ ] Basic tier user cannot select 2+ sports leagues
- [ ] Basic tier user can update payment method via Customer Portal
- [ ] Basic tier user can cancel subscription
- [ ] Premium tier user can select unlimited sports leagues
- [ ] Premium tier user can access premium-only leagues
- [ ] Premium tier user can view invoice history
- [ ] Invoice download/view links work correctly
- [ ] Subscription cancellation modal works
- [ ] Cancel at period end preserves access until end date
- [ ] Reactivation button appears after cancellation
- [ ] Mobile responsive design works on all screen sizes
- [ ] Error handling displays appropriate messages
- [ ] Success/error toasts appear and auto-dismiss
- [ ] Page loads without authentication redirect to login
- [ ] Database correctly stores preferences
- [ ] Database correctly updates subscription status

## Known Issues / Future Enhancements

1. **IP-based location inference:** Currently shows placeholder. Need to integrate IP geolocation API.
2. **Real-time updates:** Dashboard doesn't auto-refresh when subscription changes in another tab.
3. **Stripe webhooks:** Ensure webhook handlers properly update subscription status in database.
4. **Email notifications:** Not yet implemented (Phase 7.6).
5. **Subscription pause:** Not yet implemented (Phase 7.5).

## Test Data Setup

### Create Test Users
```bash
# Free tier user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "free@test.com", "password": "test1234", "username": "free_user"}'

# Basic tier user (requires Stripe subscription creation)
# 1. Register user
# 2. Create Stripe checkout session for Basic plan
# 3. Complete payment with test card 4242 4242 4242 4242

# Premium tier user (requires Stripe subscription creation)
# 1. Register user
# 2. Create Stripe checkout session for Premium plan
# 3. Complete payment with test card 4242 4242 4242 4242
```

### Seed Sports Leagues (Already in migration 003)
Sports leagues are automatically created via migration 003_subscription_schema.sql:
- EPL, NBA, NFL, MLB, NHL, MLS (Basic tier)
- La Liga, Bundesliga, Serie A, Champions League (Premium tier)

## Success Criteria

✅ All backend endpoints return correct responses
✅ Frontend dashboard renders correctly for all tier levels
✅ User preferences save and persist across sessions
✅ Tier restrictions enforced (Free = 0, Basic = 1, Premium = unlimited)
✅ Payment method management works via Stripe Customer Portal
✅ Subscription cancellation flow works correctly
✅ Invoice history displays and downloads work
✅ Mobile responsive design functions properly
✅ Error handling provides user-friendly messages
✅ No console errors in browser developer tools
