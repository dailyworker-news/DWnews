// The Daily Worker - Frontend JavaScript
// Event-based homepage with separate ONGOING and LATEST sections

const API_BASE_URL = 'http://localhost:8000/api';

// State management
let currentPage = 1;
let currentRegion = 'all';  // Changed from 'national' to show all articles by default
let currentCategory = 'all';
const articlesPerPage = 12;

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

// Load latest stories (main grid, paginated)
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

        // On first page, show first article as major headline
        if (currentPage === 1 && articles.length > 0) {
            renderMajorHeadline(articles[0]);
            renderLatestStories(articles.slice(1)); // Show remaining articles in grid
        } else {
            if (majorHeadlineSection) majorHeadlineSection.style.display = 'none';
            renderLatestStories(articles);
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
                ${article.summary ? `<p class="major-headline-summary">${article.summary}</p>` : ''}
                <p class="major-headline-meta">
                    ${formatDate(article.published_at)}
                    ${article.is_local ? ' • <span class="badge-local">Local</span>' : ''}
                </p>
            </div>
        </article>
    `;
}

// Render latest stories to main grid (newspaper-style cards)
function renderLatestStories(articles) {
    const articlesGrid = document.getElementById('articlesGrid');

    articlesGrid.innerHTML = articles.map(article => `
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
                    ${formatDate(article.published_at)}
                    ${article.is_local ? ' • <span class="badge-local">Local</span>' : ''}
                </p>
            </div>
        </article>
    `).join('');
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
