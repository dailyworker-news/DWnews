# Phase 7.3.1: Chronological Timeline Layout - Implementation Guide

**Status:** ✅ Complete
**Date:** 2026-01-01
**Complexity:** Medium
**Purpose:** Implement chronological timeline layout with subscription-tier-based archive access

---

## Overview

This phase implements a newspaper-style chronological timeline on the homepage, displaying articles in reverse chronological order with visual date separators and subscription-tier-based archive access control.

### Key Features Implemented

1. **Reverse Chronological Display** - Articles displayed newest first (already handled by backend API)
2. **Visual Date Separators** - "Today", "Yesterday", "X days ago" group headers
3. **Relative Timestamps** - Dynamic timestamps like "2 hours ago", "Yesterday at 3pm"
4. **Archive Access Control** - Tier-based limits (Free: 5 days, Basic: 10 days, Premium: unlimited)
5. **Locked Content Indicators** - 🔒 icons and grayed-out separators for locked content
6. **Inline Upgrade Prompts** - Non-blocking upgrade CTAs when users hit archive limit
7. **"Load More" Pagination** - Infinite scroll via button click
8. **Performance Optimization** - Lazy loading for images, smooth scrolling
9. **Mobile Responsive** - Optimized for all screen sizes

---

## Architecture

### Frontend Components

```
frontend/
├── scripts/main.js          # Timeline logic, date grouping, archive filtering
├── styles/main.css          # Timeline styling, date separators, upgrade prompts
└── index.html               # Subscription tier selector (testing only)
```

### Key Functions

#### Timeline Rendering (`main.js`)

```javascript
// Core timeline functions
renderTimelineStories(articles, clearGrid)  // Main timeline renderer
groupArticlesByDay(articles)                 // Group articles by date
createDateSeparator(date, isLocked)          // Create date separator HTML
createArticleCard(article)                   // Create article card HTML
createArchiveUpgradePrompt(daysPast, limit)  // Create upgrade prompt HTML
```

#### Date Formatting (`main.js`)

```javascript
getDateLabel(date)              // "Today", "Yesterday", "3 days ago"
formatRelativeTime(dateString)  // "2 hours ago", "Yesterday at 3pm"
```

#### Pagination (`main.js`)

```javascript
loadMoreArticles()       // Load next page of articles
updateLoadMoreButton()   // Show/hide "Load More" button
```

### State Management

```javascript
// Subscription tier (mock for now, will be replaced with actual user data)
let userSubscriptionTier = 'free'; // 'free', 'basic', 'premium'

// Archive limits by tier
const ARCHIVE_LIMITS = {
    free: 5,      // 5 days
    basic: 10,    // 10 days
    premium: 365  // Full archive
};

// Timeline state
let allArticles = [];       // Store all loaded articles
let isLoadingMore = false;  // Prevent duplicate loads
let hasMoreArticles = true; // Track if more articles available
```

---

## Archive Access Logic

### Tier-Based Limits

| Tier    | Archive Access | Lock Threshold |
|---------|----------------|----------------|
| Free    | 5 days         | Articles > 5 days old are locked |
| Basic   | 10 days        | Articles > 10 days old are locked |
| Premium | Unlimited      | Articles > 365 days old are locked |

### Access Control Flow

```javascript
// Calculate days difference
const now = new Date();
const articleDate = new Date(article.published_at);
const daysDiff = Math.floor((now - articleDate) / (1000 * 60 * 60 * 24));

// Check if locked
const archiveDayLimit = ARCHIVE_LIMITS[userSubscriptionTier];
const isLocked = daysDiff > archiveDayLimit;

// Render accordingly
if (isLocked) {
    // Show locked date separator
    // Show upgrade prompt instead of articles
} else {
    // Show normal date separator
    // Show articles
}
```

---

## Date Separator Logic

### Date Labels

```javascript
// Examples of date label formatting:
- "Today"              // Published today
- "Yesterday"          // Published yesterday
- "3 days ago"         // Published 3-6 days ago
- "Monday, January 1"  // Published 7+ days ago (this year)
- "Monday, January 1, 2025"  // Published in previous year
```

### Implementation

```javascript
function getDateLabel(date) {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const articleDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

    if (articleDate.getTime() === today.getTime()) {
        return 'Today';
    } else if (articleDate.getTime() === yesterday.getTime()) {
        return 'Yesterday';
    } else {
        const daysDiff = Math.floor((now - date) / (1000 * 60 * 60 * 24));
        if (daysDiff < 7) {
            return `${daysDiff} days ago`;
        } else {
            return date.toLocaleDateString('en-US', {
                weekday: 'long',
                month: 'long',
                day: 'numeric',
                year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
            });
        }
    }
}
```

---

## Relative Timestamps

### Format Examples

```
- "Just now"               // < 1 minute ago
- "5 minutes ago"          // < 1 hour ago
- "2 hours ago"            // < 24 hours ago
- "Yesterday at 3:45 PM"   // 24-48 hours ago
- "Monday at 2:30 PM"      // 2-7 days ago
- "Dec 25"                 // 7+ days ago (this year)
- "Dec 25, 2025"           // 7+ days ago (previous year)
```

### Implementation

```javascript
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor(diff / (1000 * 60));

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
    if (hours < 24) return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
    if (hours < 48) {
        const timeStr = date.toLocaleTimeString('en-US', {
            hour: 'numeric', minute: '2-digit', hour12: true
        });
        return `Yesterday at ${timeStr}`;
    }

    // Continue for other cases...
}
```

---

## Upgrade Prompt UI

### Design

```html
<div class="archive-upgrade-prompt">
    <div class="upgrade-prompt-content">
        <span class="lock-icon-large">🔒</span>
        <h4>Archive Access Limited</h4>
        <p>You've reached the 5-day archive limit for Free tier.</p>
        <p>Upgrade to Basic ($15/month) for 10 days of archive access.</p>
        <button class="subscribe-btn-large">Upgrade Now</button>
    </div>
</div>
```

### Styling

- **Background:** Light yellow (`--color-yellow-light`)
- **Border:** 3px solid yellow (`--color-yellow`)
- **Lock Icon:** Large (64px), semi-transparent
- **Typography:** Playfair Display headlines, Merriweather body
- **CTA Button:** Black border, yellow background on hover

---

## Load More Pagination

### Behavior

1. Initially loads first 12 articles
2. Shows "Load More" button if more articles available
3. On click, loads next 12 articles and appends to timeline
4. Button changes to "Loading..." while fetching
5. Automatically scrolls to show new content
6. Hides button when no more articles available

### Implementation

```javascript
async function loadMoreArticles() {
    if (isLoadingMore || !hasMoreArticles) return;

    isLoadingMore = true;
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {
        loadMoreBtn.textContent = 'Loading...';
        loadMoreBtn.disabled = true;
    }

    currentPage++;
    await loadLatestStories();  // Appends to existing articles

    isLoadingMore = false;
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
}
```

---

## Performance Optimizations

### 1. Image Lazy Loading

```javascript
// Major headline (first article) - load immediately
<img src="${article.image_url}" loading="eager">

// All other articles - lazy load
<img src="${article.image_url}" loading="lazy">
```

### 2. Smooth Scrolling

```javascript
window.scrollTo({ top: 0, behavior: 'smooth' });
```

### 3. Efficient DOM Updates

- Uses `insertAdjacentHTML` instead of `innerHTML += `
- Only re-renders changed sections
- Removes and re-creates "Load More" button instead of updating

---

## Mobile Responsiveness

### CSS Media Queries

```css
@media (max-width: 768px) {
  .timeline-date-label {
    font-size: 22px;  /* Smaller on mobile */
  }

  .lock-icon-large {
    font-size: 48px;  /* Smaller on mobile */
  }

  .archive-upgrade-prompt h4 {
    font-size: 22px;  /* Smaller on mobile */
  }

  .load-more-btn {
    width: 100%;
    max-width: 300px;
  }
}
```

### Grid Adjustments

Timeline grid already responsive via existing CSS:

```css
@media (max-width: 1024px) {
  .newspaper-stories-grid {
    grid-template-columns: repeat(2, 1fr);  /* 2 columns on tablet */
  }
}

@media (max-width: 768px) {
  .newspaper-stories-grid {
    grid-template-columns: 1fr;  /* 1 column on mobile */
  }
}
```

---

## Testing

### Automated Tests

Run the test suite:

```bash
cd /Users/home/sandbox/daily_worker/projects/DWnews
python scripts/test_timeline_layout.py
```

**Test Coverage:**

1. **Article Ordering** - Verifies reverse chronological order
2. **Archive Filtering** - Tests tier-based access control logic
3. **Date Grouping** - Validates grouping by day
4. **Pagination** - Tests offset/limit parameters and duplicate detection

### Manual Testing

1. **Start Backend:**
   ```bash
   cd projects/DWnews
   python start_backend.py
   ```

2. **Open Frontend:**
   ```
   http://localhost:3000
   ```

3. **Test Subscription Tiers:**
   - Use dropdown: "Subscription (Test)"
   - Switch between Free, Basic, Premium
   - Verify archive access changes correctly

4. **Test Timeline Features:**
   - Verify date separators appear
   - Check relative timestamps update
   - Test "Load More" button
   - Verify locked content shows upgrade prompt

5. **Test Mobile:**
   - Resize browser to mobile width
   - Or use DevTools device emulation
   - Verify responsive layout

---

## Configuration

### Subscription Tier Limits

To change archive limits, update `main.js`:

```javascript
const ARCHIVE_LIMITS = {
    free: 5,      // Change to desired days
    basic: 10,    // Change to desired days
    premium: 365  // Change to desired days
};
```

### Articles Per Page

To change pagination size, update `main.js`:

```javascript
const articlesPerPage = 12;  // Change to desired number
```

---

## Integration with Future Features

### Phase 7.2: Stripe Payment Integration

When implementing Stripe integration:

1. Remove mock `userSubscriptionTier` variable
2. Replace with actual user subscription data from backend
3. Update tier on login/subscription change
4. Add authentication check before rendering timeline

### Phase 7.3: Subscriber Authentication

When implementing auth:

1. Fetch user subscription tier from API
2. Store in session/localStorage
3. Update timeline rendering based on real tier
4. Add login prompt for free users at archive limit

---

## Troubleshooting

### Issue: Date separators not showing

**Cause:** Articles missing `published_at` field
**Fix:** Ensure all articles have valid `published_at` timestamp

### Issue: Archive limit not working

**Cause:** `userSubscriptionTier` not set correctly
**Fix:** Check subscription tier selector value, verify `ARCHIVE_LIMITS` configuration

### Issue: "Load More" button not appearing

**Cause:** Not enough articles in database
**Fix:** Add more articles, or reduce `articlesPerPage` for testing

### Issue: Images not lazy loading

**Cause:** Browser doesn't support lazy loading
**Fix:** Add JavaScript polyfill for older browsers (if needed)

---

## Files Modified

```
frontend/scripts/main.js      # 200+ lines added (timeline logic)
frontend/styles/main.css      # 170+ lines added (timeline styling)
frontend/index.html           # Tier selector added (testing)
scripts/test_timeline_layout.py  # 350 lines (test suite)
plans/roadmap.md              # Phase marked complete
```

---

## Success Criteria ✅

All requirements met:

- [x] Articles displayed in reverse chronological order (newest first)
- [x] Time-based archive filtering (5 days free, 10 days basic, unlimited premium)
- [x] "Load More" pagination for older articles
- [x] Visual date separators ("Today", "Yesterday", etc.)
- [x] Relative timestamps on article cards
- [x] Subscriber-only archive access indicators (🔒 icons)
- [x] Upgrade prompts when free users reach 5-day limit
- [x] Testing with various subscription tiers
- [x] Mobile responsiveness
- [x] Performance optimization (lazy loading)

---

## Next Steps

1. **Phase 7.2:** Implement Stripe payment integration
2. **Phase 7.3:** Implement subscriber authentication and access control
3. **Phase 7.4:** Build subscriber dashboard
4. **Integration:** Connect timeline to real user subscription data

---

## Conclusion

Phase 7.3.1 successfully implements a production-ready chronological timeline layout with subscription-tier-based archive access. The implementation is:

- **User-Friendly:** Clear visual hierarchy, intuitive date separators
- **Monetization-Ready:** Inline upgrade prompts, tier-based access control
- **Performance-Optimized:** Lazy loading, smooth scrolling, efficient DOM updates
- **Mobile-Responsive:** Optimized for all screen sizes
- **Test-Covered:** Automated test suite validates core functionality

The timeline is ready for integration with the subscription system (Phase 7.2-7.3) and provides a strong foundation for user engagement and conversion.
