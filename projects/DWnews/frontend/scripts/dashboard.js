/**
 * The Daily Worker - Dashboard JavaScript
 * Handles subscription management, billing, and user preferences
 * Phase 7.4: Subscriber Dashboard & User Preferences
 */

const API_BASE_URL = 'http://localhost:8000';

// State management
const state = {
    user: null,
    subscription: null,
    invoices: [],
    sportsLeagues: [],
    userPreferences: null
};

/**
 * Initialize dashboard on page load
 */
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Check if user is authenticated
        await checkAuth();

        // Load all dashboard data
        await Promise.all([
            loadSubscriptionStatus(),
            loadInvoices(),
            loadSportsLeagues(),
            loadUserPreferences()
        ]);

        // Hide loading, show content
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('dashboardContent').style.display = 'block';

        // Set up event listeners
        setupEventListeners();

    } catch (error) {
        console.error('Dashboard initialization error:', error);
        showError(error.message || 'Failed to load dashboard');
    }
});

/**
 * Check if user is authenticated
 */
async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
            credentials: 'include'
        });

        if (!response.ok) {
            // Not authenticated - redirect to login
            window.location.href = '/login.html?redirect=/dashboard.html';
            throw new Error('Not authenticated');
        }

        state.user = await response.json();
        document.getElementById('userEmail').textContent = state.user.email;

    } catch (error) {
        throw new Error('Authentication failed');
    }
}

/**
 * Load subscription status
 */
async function loadSubscriptionStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard/subscription`, {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Failed to load subscription status');
        }

        state.subscription = await response.json();
        renderSubscriptionStatus();

    } catch (error) {
        console.error('Error loading subscription:', error);
        throw error;
    }
}

/**
 * Render subscription status UI
 */
function renderSubscriptionStatus() {
    const sub = state.subscription;

    // Plan badge
    const planBadge = document.getElementById('planBadge');
    planBadge.className = `plan-badge plan-${sub.plan_id}`;
    document.getElementById('planName').textContent = sub.plan_name;

    // Status indicator
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');

    const statusClasses = {
        'free': 'status-free',
        'active': 'status-active',
        'trialing': 'status-active',
        'canceled': 'status-canceled',
        'past_due': 'status-past-due'
    };

    const statusLabels = {
        'free': 'Free Account',
        'active': 'Active',
        'trialing': 'Trial Period',
        'canceled': 'Canceled',
        'past_due': 'Payment Failed'
    };

    statusDot.className = `status-dot ${statusClasses[sub.status] || 'status-free'}`;
    statusText.textContent = statusLabels[sub.status] || sub.status;

    // Subscription details
    const detailsContainer = document.getElementById('subscriptionDetails');
    const details = [];

    if (sub.status !== 'free') {
        // Price
        details.push(`<div class="detail-item">
            <span class="detail-label">Price:</span>
            <span class="detail-value">$${(sub.price_cents / 100).toFixed(2)}/${sub.billing_interval}</span>
        </div>`);

        // Next billing date
        if (sub.next_billing_date && sub.status === 'active' && !sub.cancel_at_period_end) {
            details.push(`<div class="detail-item">
                <span class="detail-label">Next Billing:</span>
                <span class="detail-value">${formatDate(sub.next_billing_date)}</span>
            </div>`);
        }

        // Cancellation notice
        if (sub.cancel_at_period_end) {
            details.push(`<div class="detail-item cancellation-notice">
                <span class="detail-label">Cancels On:</span>
                <span class="detail-value">${formatDate(sub.renewal_date)}</span>
            </div>`);
        }

        // Subscription start date
        if (sub.subscription_start_date) {
            details.push(`<div class="detail-item">
                <span class="detail-label">Member Since:</span>
                <span class="detail-value">${formatDate(sub.subscription_start_date)}</span>
            </div>`);
        }
    } else {
        // Free tier
        details.push(`<div class="detail-item">
            <span class="detail-label">Access:</span>
            <span class="detail-value">5 days of articles</span>
        </div>`);

        details.push(`<div class="detail-item">
            <span class="detail-label">Upgrade to:</span>
            <span class="detail-value">Unlock full archive & personalization</span>
        </div>`);
    }

    detailsContainer.innerHTML = details.join('');

    // Action buttons
    const actionsContainer = document.getElementById('subscriptionActions');
    const actions = [];

    if (sub.status === 'free') {
        actions.push(`<button onclick="upgradeSubscription()" class="btn btn-primary">
            Upgrade to Basic ($15/month)
        </button>`);
        actions.push(`<button onclick="upgradeSubscription('premium')" class="btn btn-primary">
            Upgrade to Premium ($25/month)
        </button>`);
    } else if (sub.status === 'active' && !sub.cancel_at_period_end) {
        actions.push(`<button onclick="openCancelModal()" class="btn btn-danger">
            Cancel Subscription
        </button>`);
    } else if (sub.cancel_at_period_end) {
        actions.push(`<button onclick="reactivateSubscription()" class="btn btn-primary">
            Reactivate Subscription
        </button>`);
    }

    actionsContainer.innerHTML = actions.join('');

    // Show/hide billing section
    const billingSection = document.getElementById('billingSection');
    if (sub.status !== 'free' && sub.stripe_customer_id) {
        billingSection.style.display = 'block';

        // Render payment method
        const paymentDetails = document.getElementById('paymentMethodDetails');
        if (sub.payment_method_brand && sub.payment_method_last4) {
            paymentDetails.innerHTML = `
                <div class="payment-card">
                    <span class="card-brand">${capitalizeFirst(sub.payment_method_brand)}</span>
                    <span class="card-number">•••• ${sub.payment_method_last4}</span>
                </div>
            `;
        } else {
            paymentDetails.innerHTML = '<p class="no-payment">No payment method on file</p>';
        }
    }
}

/**
 * Load invoices
 */
async function loadInvoices() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard/invoices`, {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Failed to load invoices');
        }

        const data = await response.json();
        state.invoices = data.invoices;
        renderInvoices();

    } catch (error) {
        console.error('Error loading invoices:', error);
        document.getElementById('invoicesList').innerHTML = '<p class="error-message">Failed to load invoices</p>';
    }
}

/**
 * Render invoices list
 */
function renderInvoices() {
    const container = document.getElementById('invoicesList');

    if (state.invoices.length === 0) {
        container.innerHTML = '<p class="no-data">No invoices yet</p>';
        return;
    }

    const invoiceRows = state.invoices.map(invoice => `
        <div class="invoice-row">
            <span class="invoice-date">${formatDate(invoice.created_at)}</span>
            <span class="invoice-amount">$${(invoice.amount_cents / 100).toFixed(2)}</span>
            <span class="invoice-status status-${invoice.status}">${capitalizeFirst(invoice.status)}</span>
            <div class="invoice-actions">
                ${invoice.invoice_url ? `<a href="${invoice.invoice_url}" target="_blank" class="btn btn-small">View</a>` : ''}
                ${invoice.invoice_pdf ? `<a href="${invoice.invoice_pdf}" target="_blank" class="btn btn-small">Download PDF</a>` : ''}
            </div>
        </div>
    `).join('');

    container.innerHTML = `<div class="invoices-table">${invoiceRows}</div>`;
}

/**
 * Load sports leagues
 */
async function loadSportsLeagues() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard/sports-leagues`, {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Failed to load sports leagues');
        }

        const data = await response.json();
        state.sportsLeagues = data.leagues;

    } catch (error) {
        console.error('Error loading sports leagues:', error);
        throw error;
    }
}

/**
 * Load user preferences
 */
async function loadUserPreferences() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard/preferences`, {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Failed to load preferences');
        }

        state.userPreferences = await response.json();
        renderPreferences();

    } catch (error) {
        console.error('Error loading preferences:', error);
        throw error;
    }
}

/**
 * Render user preferences UI
 */
function renderPreferences() {
    const sub = state.subscription;
    const prefs = state.userPreferences;

    // Sports leagues section
    const sportsSection = document.getElementById('sportsLeaguesSection');

    // Update sports description based on tier
    const sportsDescription = document.getElementById('sportsDescription');

    if (sub.plan_id === 'free') {
        sportsDescription.innerHTML = '⚠️ <strong>Upgrade to Basic or Premium</strong> to select sports leagues';
        sportsSection.innerHTML = `
            <div class="upgrade-notice">
                <p>Sports league personalization is available for subscribers:</p>
                <ul>
                    <li><strong>Basic ($15/month):</strong> Select 1 sports league</li>
                    <li><strong>Premium ($25/month):</strong> Unlimited sports leagues</li>
                </ul>
                <button onclick="upgradeSubscription()" class="btn btn-primary">Upgrade Now</button>
            </div>
        `;
    } else {
        // Render sports leagues selection
        const maxLeagues = sub.plan_id === 'basic' ? 1 : 999;
        const selectionType = sub.plan_id === 'basic' ? 'radio' : 'checkbox';

        sportsDescription.textContent = sub.plan_id === 'basic'
            ? 'Select 1 sports league (Basic tier)'
            : 'Select unlimited sports leagues (Premium tier)';

        const leagueOptions = state.sportsLeagues.map(league => {
            const isSelected = prefs.sports_leagues.includes(league.id);
            const isDisabled = league.tier_requirement === 'premium' && sub.plan_id === 'basic';

            return `
                <label class="sports-league-option ${isDisabled ? 'disabled' : ''}">
                    <input
                        type="${selectionType}"
                        name="sports_league"
                        value="${league.id}"
                        ${isSelected ? 'checked' : ''}
                        ${isDisabled ? 'disabled' : ''}
                    >
                    <span class="league-name">${league.name} (${league.country})</span>
                    ${isDisabled ? '<span class="premium-badge">Premium Only</span>' : ''}
                </label>
            `;
        }).join('');

        sportsSection.innerHTML = `<div class="sports-leagues-grid">${leagueOptions}</div>`;
    }

    // Local region
    const localRegionInput = document.getElementById('localRegionInput');
    localRegionInput.value = prefs.local_region || '';

    // Inferred location (placeholder - would come from IP lookup)
    document.getElementById('inferredLocation').textContent = prefs.local_region || 'Unknown';
}

/**
 * Save user preferences
 */
async function savePreferences() {
    const saveBtn = document.getElementById('savePreferencesBtn');
    const statusSpan = document.getElementById('preferencesStatus');

    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving...';
    statusSpan.textContent = '';

    try {
        // Get selected sports leagues
        let sportsLeagues = [];

        if (state.subscription.plan_id !== 'free') {
            const selectionType = state.subscription.plan_id === 'basic' ? 'radio' : 'checkbox';
            const inputs = document.querySelectorAll(`input[name="sports_league"]:checked`);
            sportsLeagues = Array.from(inputs).map(input => parseInt(input.value));
        }

        // Get local region
        const localRegion = document.getElementById('localRegionInput').value.trim();

        // Send update request
        const response = await fetch(`${API_BASE_URL}/api/dashboard/preferences`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                sports_leagues: sportsLeagues,
                local_region: localRegion || null
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save preferences');
        }

        // Success
        statusSpan.className = 'status-message success';
        statusSpan.textContent = '✓ Preferences saved successfully!';

        // Reload preferences
        await loadUserPreferences();

        // Hide success message after 3 seconds
        setTimeout(() => {
            statusSpan.textContent = '';
        }, 3000);

    } catch (error) {
        console.error('Error saving preferences:', error);
        statusSpan.className = 'status-message error';
        statusSpan.textContent = `✗ ${error.message}`;
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = 'Save Preferences';
    }
}

/**
 * Update payment method via Stripe Customer Portal
 */
async function updatePaymentMethod() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard/customer-portal`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                return_url: window.location.href
            })
        });

        if (!response.ok) {
            throw new Error('Failed to create portal session');
        }

        const data = await response.json();
        window.open(data.portal_url, '_blank');

    } catch (error) {
        console.error('Error opening customer portal:', error);
        showToast('Failed to open payment portal', 'error');
    }
}

/**
 * Cancel subscription
 */
async function cancelSubscription() {
    const confirmBtn = document.getElementById('confirmCancelBtn');
    confirmBtn.disabled = true;
    confirmBtn.textContent = 'Canceling...';

    try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard/cancel-subscription`, {
            method: 'POST',
            credentials: 'include'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to cancel subscription');
        }

        const data = await response.json();

        // Close modal
        closeCancelModal();

        // Show success message
        showToast(`Subscription canceled. Access until ${formatDate(data.access_until)}`, 'success');

        // Reload subscription status
        await loadSubscriptionStatus();

    } catch (error) {
        console.error('Error canceling subscription:', error);
        showToast(error.message, 'error');
    } finally {
        confirmBtn.disabled = false;
        confirmBtn.textContent = 'Yes, Cancel Subscription';
    }
}

/**
 * Upgrade subscription
 */
function upgradeSubscription(plan = 'basic') {
    // Redirect to subscription page
    window.location.href = `/subscribe.html?plan=${plan}`;
}

/**
 * Reactivate subscription
 */
async function reactivateSubscription() {
    // Open Stripe Customer Portal to reactivate
    await updatePaymentMethod();
}

/**
 * Open cancel confirmation modal
 */
function openCancelModal() {
    const modal = document.getElementById('cancelModal');
    const endDate = document.getElementById('cancelEndDate');

    endDate.textContent = formatDate(state.subscription.renewal_date);
    modal.style.display = 'flex';
}

/**
 * Close cancel modal
 */
function closeCancelModal() {
    document.getElementById('cancelModal').style.display = 'none';
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Save preferences button
    document.getElementById('savePreferencesBtn').addEventListener('click', savePreferences);

    // Update payment method button
    const updatePaymentBtn = document.getElementById('updatePaymentBtn');
    if (updatePaymentBtn) {
        updatePaymentBtn.addEventListener('click', updatePaymentMethod);
    }

    // Cancel modal
    document.getElementById('confirmCancelBtn').addEventListener('click', cancelSubscription);
    document.getElementById('closeCancelModalBtn').addEventListener('click', closeCancelModal);

    // Close modal on outside click
    document.getElementById('cancelModal').addEventListener('click', (e) => {
        if (e.target.id === 'cancelModal') {
            closeCancelModal();
        }
    });
}

/**
 * Show error state
 */
function showError(message) {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('dashboardContent').style.display = 'none';
    document.getElementById('errorState').style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');

    toastMessage.textContent = message;
    toast.className = `toast toast-${type}`;
    toast.style.display = 'block';

    setTimeout(() => {
        toast.style.display = 'none';
    }, 5000);
}

/**
 * Format date string
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';

    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Capitalize first letter
 */
function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}
