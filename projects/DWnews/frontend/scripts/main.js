// The Daily Worker - Frontend JavaScript
// Event-based homepage with separate ONGOING and LATEST sections
// Phase 7.3.1: Chronological Timeline Layout

const API_BASE_URL = 'http://localhost:8000/api';

// State management
let currentPage = 1;
let currentRegion = 'all';  // Changed from 'national' to show all articles by default
let currentCategory = 'all';
const articlesPerPage = 12;
let allArticles = []; // Store all loaded articles for timeline
let isLoadingMore = false;
let hasMoreArticles = true;

// Subscription tier configuration (mock for now, will be replaced with actual user data)
let userSubscriptionTier = 'free'; // 'free', 'basic', 'premium'
const ARCHIVE_LIMITS = {
    free: 5,      // 5 days for free users
    basic: 10,    // 10 days for basic subscribers
    premium: 365  // Full archive for premium subscribers
};

// Set current date in masthead
function setCurrentDate() {
    const dateElement = document.getElementById('currentDate');
    if (!dateElement) return;

    const today = new Date();
    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };
    dateElement.textContent = today.toLocaleDateString('en-US', options);
}

// Populate archive dates (last 7 days)
function populateArchiveDates() {
    const archiveList = document.getElementById('archiveList');
    if (!archiveList) return;

    const dates = [];
    const today = new Date();

    for (let i = 1; i <= 7; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        dates.push(date);
    }

    archiveList.innerHTML = dates.map(date => {
        const formattedDate = date.toLocaleDateString('en-US', {
            month: 'long',
            day: 'numeric',
            year: 'numeric'
        });
        const dateParam = date.toISOString().split('T')[0]; // YYYY-MM-DD format

        return `
            <li>
                <a href="?date=${dateParam}" class="archive-date">
                    ${formattedDate}
                </a>
            </li>
        `;
    }).join('');
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('The Daily Worker - Initializing');

    // Set current date in masthead
    setCurrentDate();

    // Populate archive dates
    populateArchiveDates();

    // Load state from URL first
    loadStateFromUrl();

    setupCategoryNav();
    setupRegionSelector();
    setupTierSelector();  // Phase 7.3.1: Subscription tier testing
    setupPagination();

    // Apply saved state to UI
    applyStateToUI();

    loadContent();
});

// Load all content (ongoing + latest)
async function loadContent() {
    await loadOngoingStories();
    await loadLatestStories();
}

// Load ongoing stories (sidebar section)
async function loadOngoingStories() {
    const ongoingSection = document.getElementById('ongoingSection');
    const ongoingList = document.getElementById('ongoingList');

    try {
        // Fetch ongoing stories (always show all ongoing, regardless of region/category for now)
        const params = new URLSearchParams({
            status: 'published',
            ongoing: 'true',
            limit: '10'
        });

        const response = await fetch(`${API_BASE_URL}/articles/?${params}`);

        if (!response.ok) {
            throw new Error('Failed to fetch ongoing stories');
        }

        const articles = await response.json();

        if (articles.length === 0) {
            ongoingSection.style.display = 'none';
            return;
        }

        ongoingSection.style.display = 'block';
        renderOngoingStories(articles);

    } catch (error) {
        console.error('Error loading ongoing stories:', error);
        ongoingSection.style.display = 'none';
    }
}

// Render ongoing stories to sidebar (compact list format)
function renderOngoingStories(articles) {
    const ongoingList = document.getElementById('ongoingList');

    ongoingList.innerHTML = articles.map(article => `
        <div class="ongoing-item">
            <p class="ongoing-category">${article.category_name || article.category}</p>
            <h4 class="ongoing-title">
                <a href="article.html?id=${article.id}">${article.title}</a>
            </h4>
            <p class="ongoing-date">${formatDate(article.published_at)}</p>
        </div>
    `).join('');
}

// Load latest stories (main grid, with timeline support)
async function loadLatestStories() {
    const articlesGrid = document.getElementById('articlesGrid');
    const majorHeadlineSection = document.getElementById('majorHeadlineSection');
    articlesGrid.innerHTML = '<p class="loading-message">Loading articles...</p>';

    try {
        const params = new URLSearchParams({
            status: 'published',
            ongoing: 'false',  // Exclude ongoing stories from latest section
            limit: articlesPerPage.toString(),
            offset: ((currentPage - 1) * articlesPerPage).toString()
        });

        // Add region filter
        if (currentRegion !== 'all') {
            params.append('region', currentRegion);
        }

        // Add category filter
        if (currentCategory !== 'all') {
            params.append('category', currentCategory);
        }

        const response = await fetch(`${API_BASE_URL}/articles/?${params}`);

        if (!response.ok) {
            throw new Error('Failed to fetch articles');
        }

        const articles = await response.json();

        if (articles.length === 0) {
            articlesGrid.innerHTML = '<p class="loading-message">No articles found. Try a different filter!</p>';
            if (majorHeadlineSection) majorHeadlineSection.style.display = 'none';
            updatePagination(false);
            return;
        }

        // Store articles for timeline
        if (currentPage === 1) {
            allArticles = articles;
        } else {
            allArticles = [...allArticles, ...articles];
        }

        hasMoreArticles = articles.length === articlesPerPage;

        // On first page, show first article as major headline
        if (currentPage === 1 && articles.length > 0) {
            renderMajorHeadline(articles[0]);
            renderTimelineStories(articles.slice(1), currentPage === 1); // Show remaining articles in timeline
        } else {
            if (majorHeadlineSection) majorHeadlineSection.style.display = 'none';
            renderTimelineStories(articles, false);
        }

        updatePagination(articles.length === articlesPerPage);

    } catch (error) {
        console.error('Error loading latest stories:', error);
        articlesGrid.innerHTML = `
            <p class="loading-message">
                Unable to load articles. Make sure the backend is running at ${API_BASE_URL}
            </p>
        `;
        if (majorHeadlineSection) majorHeadlineSection.style.display = 'none';
        updatePagination(false);
    }
}

// Render major headline (first article on page 1)
function renderMajorHeadline(article) {
    const majorHeadlineSection = document.getElementById('majorHeadlineSection');
    if (!majorHeadlineSection) return;

    majorHeadlineSection.style.display = 'block';
    majorHeadlineSection.innerHTML = `
        <article class="major-headline">
            ${article.image_url ? `
                <div class="major-headline-image">
                    <img src="${article.image_url}" alt="${article.title}" loading="eager">
                </div>
            ` : ''}
            <div class="major-headline-content">
                <p class="major-headline-category">${article.category_name || article.category}</p>
                <h2 class="major-headline-title">
                    <a href="article.html?id=${article.id}">${article.title}</a>
                </h2>
                ${article.summary ? `<p class="major-headline-deck">${article.summary}</p>` : ''}
                <p class="major-headline-meta">
                    <span class="story-timestamp">${formatRelativeTime(article.published_at)}</span>
                    ${article.is_local ? ' • <span class="badge-local">Local</span>' : ''}
                </p>
            </div>
        </article>
    `;
}

// Render timeline stories with date separators and archive access control
function renderTimelineStories(articles, clearGrid = true) {
    const articlesGrid = document.getElementById('articlesGrid');

    if (clearGrid) {
        articlesGrid.innerHTML = '';
    }

    // Group articles by day for date separators
    const groupedArticles = groupArticlesByDay(articles);
    const archiveDayLimit = ARCHIVE_LIMITS[userSubscriptionTier];
    const now = new Date();

    // Render each day group
    Object.keys(groupedArticles).forEach(dateKey => {
        const dayArticles = groupedArticles[dateKey];
        const articleDate = new Date(dayArticles[0].published_at);
        const daysDiff = Math.floor((now - articleDate) / (1000 * 60 * 60 * 24));

        // Check if this content is within user's archive access
        const isLocked = daysDiff > archiveDayLimit;

        // Add date separator
        const separator = createDateSeparator(articleDate, isLocked);
        articlesGrid.insertAdjacentHTML('beforeend', separator);

        // If locked, show upgrade prompt instead of articles
        if (isLocked) {
            const upgradePrompt = createArchiveUpgradePrompt(daysDiff, archiveDayLimit);
            articlesGrid.insertAdjacentHTML('beforeend', upgradePrompt);
        } else {
            // Render articles for this day
            dayArticles.forEach(article => {
                const articleCard = createArticleCard(article);
                articlesGrid.insertAdjacentHTML('beforeend', articleCard);
            });
        }
    });

    // Add "Load More" button if there are more articles
    updateLoadMoreButton();
}

// Group articles by day
function groupArticlesByDay(articles) {
    const groups = {};

    articles.forEach(article => {
        const date = new Date(article.published_at);
        const dateKey = date.toDateString(); // e.g., "Tue Jan 02 2026"

        if (!groups[dateKey]) {
            groups[dateKey] = [];
        }
        groups[dateKey].push(article);
    });

    return groups;
}

// Create date separator element
function createDateSeparator(date, isLocked) {
    const dateLabel = getDateLabel(date);
    const lockIcon = isLocked ? '<span class="lock-icon">🔒</span>' : '';

    return `
        <div class="timeline-date-separator ${isLocked ? 'locked' : ''}">
            <h3 class="timeline-date-label">${lockIcon} ${dateLabel}</h3>
        </div>
    `;
}

// Get human-readable date label
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

// Create article card HTML
function createArticleCard(article) {
    return `
        <article class="newspaper-story-card">
            ${article.image_url ? `
                <div class="story-image">
                    <img src="${article.image_url}" alt="${article.title}" loading="lazy">
                </div>
            ` : ''}
            <div class="story-content">
                <p class="story-category">${article.category_name || article.category}</p>
                <h3 class="story-headline">
                    <a href="article.html?id=${article.id}">${article.title}</a>
                </h3>
                ${article.summary ? `<p class="story-summary">${article.summary}</p>` : ''}
                <p class="story-meta">
                    <span class="story-timestamp">${formatRelativeTime(article.published_at)}</span>
                    ${article.is_local ? ' • <span class="badge-local">Local</span>' : ''}
                </p>
            </div>
        </article>
    `;
}

// Create archive upgrade prompt
function createArchiveUpgradePrompt(daysPast, userLimit) {
    const tierName = userSubscriptionTier === 'free' ? 'Free' : 'Basic';
    const nextTier = userSubscriptionTier === 'free' ? 'Basic ($15/month)' : 'Premium ($25/month)';
    const nextTierDays = userSubscriptionTier === 'free' ? '10 days' : 'unlimited';

    return `
        <div class="archive-upgrade-prompt">
            <div class="upgrade-prompt-content">
                <span class="lock-icon-large">🔒</span>
                <h4>Archive Access Limited</h4>
                <p>You've reached the ${userLimit}-day archive limit for ${tierName} tier.</p>
                <p>Upgrade to ${nextTier} for ${nextTierDays} of archive access.</p>
                <button class="subscribe-btn-large" onclick="alert('Subscription feature coming soon!')">
                    Upgrade Now
                </button>
            </div>
        </div>
    `;
}

// Update "Load More" button
function updateLoadMoreButton() {
    let loadMoreBtn = document.getElementById('loadMoreBtn');

    // Remove existing button if present
    if (loadMoreBtn) {
        loadMoreBtn.remove();
    }

    // Add button if there are more articles
    if (hasMoreArticles && !isLoadingMore) {
        const articlesGrid = document.getElementById('articlesGrid');
        const buttonHTML = `
            <div class="load-more-container" id="loadMoreContainer">
                <button id="loadMoreBtn" class="load-more-btn" onclick="loadMoreArticles()">
                    Load More Articles
                </button>
            </div>
        `;
        articlesGrid.insertAdjacentHTML('beforeend', buttonHTML);
    }
}

// Load more articles (pagination via button click)
async function loadMoreArticles() {
    if (isLoadingMore || !hasMoreArticles) return;

    isLoadingMore = true;
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {
        loadMoreBtn.textContent = 'Loading...';
        loadMoreBtn.disabled = true;
    }

    currentPage++;
    await loadLatestStories();

    isLoadingMore = false;
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
}

// Format relative timestamp (e.g., "2 hours ago", "Yesterday at 3pm")
function formatRelativeTime(dateString) {
    if (!dateString) return '';

    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor(diff / (1000 * 60));

    if (minutes < 1) {
        return 'Just now';
    } else if (minutes < 60) {
        return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
    } else if (hours < 1) {
        return `${minutes} minutes ago`;
    } else if (hours < 24) {
        const timeStr = date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
        return hours === 1 ? `1 hour ago` : `${hours} hours ago`;
    } else if (hours < 48) {
        const timeStr = date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
        return `Yesterday at ${timeStr}`;
    } else {
        const daysDiff = Math.floor(hours / 24);
        if (daysDiff < 7) {
            const timeStr = date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
            const dayName = date.toLocaleDateString('en-US', { weekday: 'long' });
            return `${dayName} at ${timeStr}`;
        } else {
            return date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
            });
        }
    }
}

// Render latest stories to main grid (newspaper-style cards) - DEPRECATED in favor of renderTimelineStories
function renderLatestStories(articles) {
    // This function is now handled by renderTimelineStories
    renderTimelineStories(articles, true);
}

// Check if article is new (published within last 24 hours)
function isNewArticle(publishedAt) {
    if (!publishedAt) return false;
    const articleDate = new Date(publishedAt);
    const now = new Date();
    const hoursDiff = (now - articleDate) / (1000 * 60 * 60);
    return hoursDiff < 24;
}

// Format date for display
function formatDate(dateString) {
    if (!dateString) return '';

    const date = new Date(dateString);
    const now = new Date();
    const hoursDiff = (now - date) / (1000 * 60 * 60);

    if (hoursDiff < 1) {
        return 'Just now';
    } else if (hoursDiff < 24) {
        return `${Math.floor(hoursDiff)} hours ago`;
    } else if (hoursDiff < 48) {
        return 'Yesterday';
    } else {
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
        });
    }
}

// Set up category navigation
function setupCategoryNav() {
    const navLinks = document.querySelectorAll('.nav-link');
    const footerLinks = document.querySelectorAll('.footer-nav a[data-category]');

    // Main nav
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();

            // Update active state
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Get category from data attribute
            const category = link.getAttribute('data-category');
            currentCategory = category || 'all';
            currentPage = 1;  // Reset to first page

            console.log(`Switching to category: ${currentCategory}`);
            updateUrlState();
            loadLatestStories();
        });
    });

    // Footer nav
    footerLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();

            const category = link.getAttribute('data-category');
            currentCategory = category || 'all';
            currentPage = 1;

            // Update main nav active state
            navLinks.forEach(l => {
                if (l.getAttribute('data-category') === category) {
                    l.classList.add('active');
                } else {
                    l.classList.remove('active');
                }
            });

            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });

            updateUrlState();
            loadLatestStories();
        });
    });
}

// Set up region selector
function setupRegionSelector() {
    const regionSelect = document.getElementById('regionSelect');

    regionSelect.addEventListener('change', (e) => {
        currentRegion = e.target.value;
        currentPage = 1;  // Reset to first page

        console.log(`Switching to ${currentRegion} articles`);
        updateUrlState();
        loadContent();  // Reload both ongoing and latest
    });
}

// Set up subscription tier selector (testing only - Phase 7.3.1)
function setupTierSelector() {
    const tierSelect = document.getElementById('tierSelect');

    if (tierSelect) {
        tierSelect.addEventListener('change', (e) => {
            userSubscriptionTier = e.target.value;
            currentPage = 1;  // Reset to first page

            console.log(`Switching to ${userSubscriptionTier} subscription tier (${ARCHIVE_LIMITS[userSubscriptionTier]} days)`);

            // Reload articles to re-render with new tier
            loadLatestStories();
        });
    }
}

// Set up pagination
function setupPagination() {
    const prevButton = document.getElementById('prevPage');
    const nextButton = document.getElementById('nextPage');

    prevButton.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            updateUrlState();
            loadLatestStories();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });

    nextButton.addEventListener('click', () => {
        currentPage++;
        updateUrlState();
        loadLatestStories();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// Update pagination UI
function updatePagination(hasMore) {
    const pagination = document.getElementById('pagination');
    const prevButton = document.getElementById('prevPage');
    const nextButton = document.getElementById('nextPage');
    const pageInfo = document.getElementById('pageInfo');

    // Show/hide pagination
    pagination.style.display = (currentPage > 1 || hasMore) ? 'flex' : 'none';

    // Update button states
    prevButton.disabled = currentPage === 1;
    nextButton.disabled = !hasMore;

    // Update page info
    pageInfo.textContent = `Page ${currentPage}`;
}

// URL State Management - Save and restore filters
function loadStateFromUrl() {
    const params = new URLSearchParams(window.location.search);

    if (params.has('region')) {
        currentRegion = params.get('region');
    }

    if (params.has('category')) {
        currentCategory = params.get('category');
    }

    if (params.has('page')) {
        const page = parseInt(params.get('page'));
        if (!isNaN(page) && page > 0) {
            currentPage = page;
        }
    }

    console.log('Loaded state from URL:', { currentRegion, currentCategory, currentPage });
}

// Apply current state to UI elements
function applyStateToUI() {
    // Set region selector
    const regionSelect = document.getElementById('regionSelect');
    if (regionSelect) {
        regionSelect.value = currentRegion;
    }

    // Set active category nav link
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        const linkCategory = link.getAttribute('data-category');
        if (linkCategory === currentCategory) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Update URL with current state (without page reload)
function updateUrlState() {
    const params = new URLSearchParams();

    if (currentRegion !== 'national') {
        params.set('region', currentRegion);
    }

    if (currentCategory !== 'all') {
        params.set('category', currentCategory);
    }

    if (currentPage > 1) {
        params.set('page', currentPage.toString());
    }

    const newUrl = params.toString()
        ? `${window.location.pathname}?${params.toString()}`
        : window.location.pathname;

    window.history.pushState({}, '', newUrl);
}
