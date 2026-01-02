// The Daily Worker - Admin Dashboard JavaScript

const API_BASE = 'http://localhost:8000/api';
let currentFilter = 'draft';
let currentArticle = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Admin Dashboard initialized');
    loadArticles('draft');
    updateCounts();
});

// Filter articles by status
function filterArticles(status) {
    currentFilter = status;

    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.closest('.nav-item').classList.add('active');

    // Update title
    const titles = {
        'draft': 'Pending Review',
        'published': 'Published Articles',
        'archived': 'Archived Articles',
        'all': 'All Articles'
    };
    document.getElementById('listTitle').textContent = titles[status] || 'Articles';

    // Load articles
    loadArticles(status);
}

// Load articles from API
async function loadArticles(status = 'draft') {
    const articlesList = document.getElementById('articlesList');
    articlesList.innerHTML = '<div class="loading-message">Loading articles...</div>';

    try {
        const url = status === 'all'
            ? `${API_BASE}/articles/`
            : `${API_BASE}/articles/?status=${status}`;

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error('Failed to fetch articles');
        }

        const articles = await response.json();

        if (articles.length === 0) {
            articlesList.innerHTML = '<div class="loading-message">No articles found</div>';
            return;
        }

        renderArticlesList(articles);

    } catch (error) {
        console.error('Error loading articles:', error);
        articlesList.innerHTML = '<div class="loading-message">Error loading articles</div>';
    }
}

// Render articles list
function renderArticlesList(articles) {
    const articlesList = document.getElementById('articlesList');

    articlesList.innerHTML = articles.map(article => `
        <div class="article-card">
            <div class="article-card-header">
                <h3 class="article-card-title">${article.title}</h3>
                <span class="article-card-status status-${article.status}">${article.status}</span>
            </div>

            <div class="article-card-meta">
                <span>📁 ${article.category_name}</span>
                <span>${article.is_national ? '🌎 National' : '📍 Local'}</span>
                ${article.is_ongoing ? '<span>🚩 Ongoing</span>' : ''}
                ${article.is_new ? '<span>✨ New</span>' : ''}
            </div>

            ${article.summary ? `<p class="article-card-summary">${article.summary}</p>` : ''}

            <div class="article-card-actions" style="margin-top: 10px; display: flex; gap: 10px;">
                <button onclick="openReview(${article.id}); event.stopPropagation();"
                        style="padding: 8px 16px; background: #2196f3; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    📋 Review
                </button>
                <button onclick="loadArticlePreview(${article.id}); event.stopPropagation();"
                        style="padding: 8px 16px; background: #757575; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    👁️ Quick View
                </button>
            </div>
        </div>
    `).join('');
}

// Open article review page
function openReview(articleId) {
    window.location.href = `review-article.html?id=${articleId}`;
}

// Load article preview
async function loadArticlePreview(articleId) {
    try {
        const response = await fetch(`${API_BASE}/articles/${articleId}`);

        if (!response.ok) {
            throw new Error('Failed to fetch article');
        }

        const article = await response.json();
        currentArticle = article;

        // Show preview panel
        const preview = document.getElementById('articlePreview');
        preview.style.display = 'block';

        // Populate preview
        document.getElementById('previewCategory').textContent = article.category_name;
        document.getElementById('previewStatus').textContent = article.status;
        document.getElementById('previewStatus').className = `preview-status status-${article.status}`;
        document.getElementById('previewTitle').textContent = article.title;

        // Info
        document.getElementById('previewReadingLevel').textContent =
            article.reading_level ? article.reading_level.toFixed(1) : 'N/A';
        document.getElementById('previewWordCount').textContent =
            article.word_count || 'N/A';

        const typeFlags = [];
        if (article.is_national) typeFlags.push('National');
        if (article.is_local) typeFlags.push('Local');
        if (article.is_ongoing) typeFlags.push('Ongoing');
        if (article.is_new) typeFlags.push('New');
        document.getElementById('previewType').textContent = typeFlags.join(', ') || 'N/A';

        // Image
        if (article.image_url) {
            const imageDiv = document.getElementById('previewImage');
            imageDiv.style.display = 'block';
            imageDiv.querySelector('img').src = article.image_url;
            imageDiv.querySelector('.image-attribution').textContent =
                article.image_attribution || '';
        } else {
            document.getElementById('previewImage').style.display = 'none';
        }

        // Body
        document.getElementById('previewBody').textContent = article.body;

        // Special sections
        if (article.why_this_matters) {
            const whyDiv = document.getElementById('previewWhyMatters');
            whyDiv.style.display = 'block';
            document.getElementById('whyMattersText').textContent = article.why_this_matters;
        } else {
            document.getElementById('previewWhyMatters').style.display = 'none';
        }

        if (article.what_you_can_do) {
            const whatDiv = document.getElementById('previewWhatToDo');
            whatDiv.style.display = 'block';
            document.getElementById('whatToDoText').textContent = article.what_you_can_do;
        } else {
            document.getElementById('previewWhatToDo').style.display = 'none';
        }

        // Update ongoing button
        const ongoingBtn = document.getElementById('btnOngoing');
        if (article.is_ongoing) {
            ongoingBtn.textContent = '✓ Marked as Ongoing';
            ongoingBtn.classList.add('active');
        } else {
            ongoingBtn.textContent = '🚩 Mark as Ongoing';
            ongoingBtn.classList.remove('active');
        }

    } catch (error) {
        console.error('Error loading article preview:', error);
        alert('Failed to load article preview');
    }
}

// Close preview
function closePreview() {
    document.getElementById('articlePreview').style.display = 'none';
    currentArticle = null;
}

// Approve article (publish)
async function approveArticle() {
    if (!currentArticle) return;

    if (!confirm('Approve and publish this article?')) return;

    try {
        const response = await fetch(`${API_BASE}/articles/${currentArticle.id}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: 'published' })
        });

        if (!response.ok) {
            throw new Error('Failed to approve article');
        }

        alert('Article published successfully!');
        closePreview();
        refreshArticles();

    } catch (error) {
        console.error('Error approving article:', error);
        alert('Failed to approve article');
    }
}

// Flag as ongoing story
async function flagOngoing() {
    if (!currentArticle) return;

    const newOngoingStatus = !currentArticle.is_ongoing;

    try {
        const response = await fetch(`${API_BASE}/articles/${currentArticle.id}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ is_ongoing: newOngoingStatus })
        });

        if (!response.ok) {
            throw new Error('Failed to update article');
        }

        currentArticle.is_ongoing = newOngoingStatus;

        // Update button
        const ongoingBtn = document.getElementById('btnOngoing');
        if (newOngoingStatus) {
            ongoingBtn.textContent = '✓ Marked as Ongoing';
            ongoingBtn.classList.add('active');
            alert('Article marked as ongoing story');
        } else {
            ongoingBtn.textContent = '🚩 Mark as Ongoing';
            ongoingBtn.classList.remove('active');
            alert('Ongoing flag removed');
        }

        refreshArticles();

    } catch (error) {
        console.error('Error updating article:', error);
        alert('Failed to update article');
    }
}

// Archive article
async function archiveArticle() {
    if (!currentArticle) return;

    if (!confirm('Archive this article? It will not be displayed publicly.')) return;

    try {
        const response = await fetch(`${API_BASE}/articles/${currentArticle.id}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: 'archived' })
        });

        if (!response.ok) {
            throw new Error('Failed to archive article');
        }

        alert('Article archived');
        closePreview();
        refreshArticles();

    } catch (error) {
        console.error('Error archiving article:', error);
        alert('Failed to archive article');
    }
}

// Refresh current view
function refreshArticles() {
    loadArticles(currentFilter);
    updateCounts();
}

// Update article counts in sidebar
async function updateCounts() {
    try {
        // Get counts for each status
        const statuses = ['draft', 'published', 'archived'];

        for (const status of statuses) {
            const response = await fetch(`${API_BASE}/articles/?status=${status}`);
            if (response.ok) {
                const articles = await response.json();
                document.getElementById(`count-${status}`).textContent = articles.length;
            }
        }

        // All articles
        const allResponse = await fetch(`${API_BASE}/articles/`);
        if (allResponse.ok) {
            const allArticles = await allResponse.json();
            document.getElementById('count-all').textContent = allArticles.length;

            // Calculate statistics
            updateStatistics(allArticles);
        }

    } catch (error) {
        console.error('Error updating counts:', error);
    }
}

// Update statistics
function updateStatistics(articles) {
    // Today's articles
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const todayArticles = articles.filter(a => {
        if (!a.created_at) return false;
        const created = new Date(a.created_at);
        return created >= today;
    });
    document.getElementById('stat-today').textContent = todayArticles.length;

    // This week's articles
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    const weekArticles = articles.filter(a => {
        if (!a.created_at) return false;
        const created = new Date(a.created_at);
        return created >= weekAgo;
    });
    document.getElementById('stat-week').textContent = weekArticles.length;

    // Average reading level
    const publishedArticles = articles.filter(a => a.status === 'published');
    if (publishedArticles.length > 0) {
        const avgReading = publishedArticles.reduce((sum, a) => {
            return sum + (a.reading_level || 8.0);
        }, 0) / publishedArticles.length;
        document.getElementById('stat-reading').textContent = avgReading.toFixed(1);
    }
}

// Logout (simple - just reload page which will trigger auth again)
function logout() {
    if (confirm('Logout from admin dashboard?')) {
        window.location.href = '/';
    }
}
