// The Daily Worker - Frontend JavaScript
// Handles article loading and display

const API_BASE_URL = 'http://localhost:8000/api';

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('The Daily Worker - Initializing');
    loadArticles();
    setupRegionSelector();
});

// Load articles from API
async function loadArticles(region = 'national', category = null) {
    const articlesGrid = document.getElementById('articlesGrid');
    articlesGrid.innerHTML = '<p class="loading-message">Loading articles...</p>';

    try {
        // TODO: Replace with actual API endpoint when implemented
        const response = await fetch(`${API_BASE_URL}/articles?region=${region}${category ? `&category=${category}` : ''}`);

        if (!response.ok) {
            throw new Error('Failed to fetch articles');
        }

        const articles = await response.json();

        if (articles.length === 0) {
            articlesGrid.innerHTML = '<p class="loading-message">No articles found. Start generating content!</p>';
            return;
        }

        renderArticles(articles);
    } catch (error) {
        console.error('Error loading articles:', error);
        articlesGrid.innerHTML = `
            <p class="loading-message">
                Unable to load articles. Make sure the backend is running at ${API_BASE_URL}
            </p>
        `;
    }
}

// Render articles to the grid
function renderArticles(articles) {
    const articlesGrid = document.getElementById('articlesGrid');

    articlesGrid.innerHTML = articles.map(article => `
        <article class="article-card ${article.is_ongoing ? 'ongoing' : ''}">
            ${article.image_url ? `
                <img src="${article.image_url}" alt="${article.title}" loading="lazy">
            ` : ''}
            <div class="article-content">
                ${article.is_ongoing ? '<span class="article-badge badge-ongoing">Ongoing</span>' : ''}
                ${!article.is_ongoing && isNewArticle(article.published_at) ? '<span class="article-badge badge-new">New</span>' : ''}
                ${article.is_local ? '<span class="article-badge badge-local">Local</span>' : ''}

                <p class="article-category">${article.category}</p>
                <h3 class="article-title">
                    <a href="/article/${article.id}">${article.title}</a>
                </h3>
                <p class="article-date">${formatDate(article.published_at)}</p>
            </div>
        </article>
    `).join('');
}

// Check if article is new (published within last 24 hours)
function isNewArticle(publishedAt) {
    const articleDate = new Date(publishedAt);
    const now = new Date();
    const hoursDiff = (now - articleDate) / (1000 * 60 * 60);
    return hoursDiff < 24;
}

// Format date for display
function formatDate(dateString) {
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

// Set up region selector
function setupRegionSelector() {
    const regionSelect = document.getElementById('regionSelect');

    regionSelect.addEventListener('change', (e) => {
        const region = e.target.value;
        console.log(`Switching to ${region} articles`);
        loadArticles(region);
    });
}

// Set up category navigation
function setupCategoryNav() {
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();

            // Update active state
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Load articles for category
            const category = link.textContent.toLowerCase();
            const region = document.getElementById('regionSelect').value;

            if (category === 'home') {
                loadArticles(region);
            } else {
                loadArticles(region, category);
            }
        });
    });
}

// Initialize category navigation
setupCategoryNav();
