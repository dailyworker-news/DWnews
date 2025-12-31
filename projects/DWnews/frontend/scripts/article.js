// The Daily Worker - Article Page JavaScript
// Handles loading and displaying individual articles

const API_BASE_URL = 'http://localhost:8000/api';

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    console.log('Article page - Initializing');

    const articleId = getArticleIdFromUrl();

    if (!articleId) {
        showError('No article ID provided');
        return;
    }

    loadArticle(articleId);
});

// Get article ID from URL
function getArticleIdFromUrl() {
    // Support both /article/123 and /article.html?id=123 formats
    const pathMatch = window.location.pathname.match(/\/article\/(\d+)/);
    if (pathMatch) {
        return pathMatch[1];
    }

    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

// Load article from API
async function loadArticle(articleId) {
    const loadingMessage = document.getElementById('loadingMessage');
    const articleContent = document.getElementById('articleContent');
    const errorMessage = document.getElementById('errorMessage');

    loadingMessage.style.display = 'block';
    articleContent.style.display = 'none';
    errorMessage.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE_URL}/articles/${articleId}`);

        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Article not found');
            }
            throw new Error('Failed to fetch article');
        }

        const article = await response.json();

        // Only show published articles to public
        if (article.status !== 'published') {
            throw new Error('Article not available');
        }

        loadingMessage.style.display = 'none';
        renderArticle(article);

    } catch (error) {
        console.error('Error loading article:', error);
        loadingMessage.style.display = 'none';
        showError(error.message);
    }
}

// Render article content
function renderArticle(article) {
    const articleContent = document.getElementById('articleContent');

    try {
        // Update page title and meta
        document.getElementById('pageTitle').textContent = `${article.title} - The Daily Worker`;
        if (article.summary) {
            document.getElementById('pageDescription').setAttribute('content', article.summary);
        }

        // Header badges
        const categoryBadge = document.getElementById('categoryBadge');
        categoryBadge.textContent = article.category_name || article.category;
        categoryBadge.className = 'article-badge';

        if (article.is_ongoing) {
            document.getElementById('ongoingBadge').style.display = 'inline-block';
        }

        if (article.is_new || isNewArticle(article.published_at)) {
            document.getElementById('newBadge').style.display = 'inline-block';
        }

        if (article.is_local) {
            document.getElementById('localBadge').style.display = 'inline-block';
        }

        // Title
        document.getElementById('articleTitle').textContent = article.title;

        // Meta information
        document.getElementById('articleDate').textContent = formatFullDate(article.published_at);

        const readingLevelSpan = document.getElementById('articleReadingLevel');
        if (article.reading_level) {
            readingLevelSpan.textContent = `Reading Level: ${article.reading_level.toFixed(1)}`;

            // Add color class based on reading level
            if (article.reading_level >= 7.5 && article.reading_level <= 8.5) {
                readingLevelSpan.classList.add('reading-level-good');
            } else if (article.reading_level >= 7.0 && article.reading_level <= 9.0) {
                readingLevelSpan.classList.add('reading-level-acceptable');
            } else {
                readingLevelSpan.classList.add('reading-level-difficult');
            }
        } else {
            readingLevelSpan.textContent = '';
        }

        if (article.word_count) {
            const readTime = Math.ceil(article.word_count / 200); // Assume 200 words/min
            document.getElementById('articleWordCount').textContent = `${article.word_count} words (~${readTime} min read)`;
        }

        // Image
        if (article.image_url) {
            const imageContainer = document.getElementById('articleImageContainer');
            const image = document.getElementById('articleImage');
            const attribution = document.getElementById('imageAttribution');

            image.src = article.image_url;
            image.alt = article.title;

            if (article.image_attribution) {
                attribution.textContent = article.image_attribution;
            }

            imageContainer.style.display = 'block';
        }

        // Summary
        if (article.summary) {
            const summaryContainer = document.getElementById('articleSummaryContainer');
            document.getElementById('articleSummary').textContent = article.summary;
            summaryContainer.style.display = 'block';
        }

        // Body
        const bodyElement = document.getElementById('articleBody');
        bodyElement.innerHTML = formatArticleBody(article.body);

        // Special sections
        if (article.why_this_matters) {
            const whySection = document.getElementById('whyThisMattersSection');
            document.getElementById('whyThisMattersContent').textContent = article.why_this_matters;
            whySection.style.display = 'block';
        }

        if (article.what_you_can_do) {
            const whatSection = document.getElementById('whatYouCanDoSection');
            document.getElementById('whatYouCanDoContent').textContent = article.what_you_can_do;
            whatSection.style.display = 'block';
        }

        // Footer metadata
        document.getElementById('footerCategory').textContent = article.category_name || article.category;
        document.getElementById('footerReadingLevel').textContent = article.reading_level
            ? article.reading_level.toFixed(1)
            : 'N/A';
        document.getElementById('footerPublished').textContent = formatFullDate(article.published_at);
        document.getElementById('footerWordCount').textContent = article.word_count || 'N/A';

        // Show article
        articleContent.style.display = 'block';

        // Setup share buttons
        setupShareButtons(article);

    } catch (error) {
        console.error('Error rendering article:', error);
        showError(`Failed to render article: ${error.message}`);
    }
}

// Format article body (convert line breaks to paragraphs)
function formatArticleBody(body) {
    if (!body) return '';

    // Split by double line breaks to create paragraphs
    const paragraphs = body.split('\n\n').filter(p => p.trim());

    return paragraphs.map(p => {
        // Preserve single line breaks within paragraphs
        const content = p.trim().replace(/\n/g, '<br>');
        return `<p>${content}</p>`;
    }).join('');
}

// Check if article is new (within 24 hours)
function isNewArticle(publishedAt) {
    if (!publishedAt) return false;
    const articleDate = new Date(publishedAt);
    const now = new Date();
    const hoursDiff = (now - articleDate) / (1000 * 60 * 60);
    return hoursDiff < 24;
}

// Format full date
function formatFullDate(dateString) {
    if (!dateString) return '';

    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Show error message
function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    const loadingMessage = document.getElementById('loadingMessage');
    const articleContent = document.getElementById('articleContent');

    loadingMessage.style.display = 'none';
    articleContent.style.display = 'none';
    errorMessage.style.display = 'block';

    // Update error message if needed
    if (message && message !== 'Article not found') {
        errorMessage.querySelector('p').textContent = message;
    }
}

// Setup share buttons
function setupShareButtons(article) {
    const url = window.location.href;
    const title = article.title;
    const summary = article.summary || title;

    // Twitter/X
    document.getElementById('shareTwitter').addEventListener('click', () => {
        const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}`;
        window.open(twitterUrl, '_blank', 'width=550,height=420');
    });

    // Facebook
    document.getElementById('shareFacebook').addEventListener('click', () => {
        const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
        window.open(facebookUrl, '_blank', 'width=550,height=420');
    });

    // LinkedIn
    document.getElementById('shareLinkedIn').addEventListener('click', () => {
        const linkedInUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;
        window.open(linkedInUrl, '_blank', 'width=550,height=420');
    });

    // Reddit
    document.getElementById('shareReddit').addEventListener('click', () => {
        const redditUrl = `https://reddit.com/submit?url=${encodeURIComponent(url)}&title=${encodeURIComponent(title)}`;
        window.open(redditUrl, '_blank', 'width=550,height=420');
    });

    // Email
    document.getElementById('shareEmail').addEventListener('click', () => {
        const subject = encodeURIComponent(`The Daily Worker: ${title}`);
        const body = encodeURIComponent(`I thought you might find this article interesting:\n\n${title}\n\n${summary}\n\nRead more: ${url}`);
        window.location.href = `mailto:?subject=${subject}&body=${body}`;
    });

    // Copy Link
    document.getElementById('copyLink').addEventListener('click', async () => {
        const button = document.getElementById('copyLink');
        const buttonText = document.getElementById('copyLinkText');

        try {
            await navigator.clipboard.writeText(url);

            // Visual feedback
            button.classList.add('copied');
            buttonText.textContent = '✓ Copied!';

            setTimeout(() => {
                button.classList.remove('copied');
                buttonText.textContent = 'Copy Link';
            }, 2000);

        } catch (err) {
            console.error('Failed to copy:', err);

            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = url;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            document.body.appendChild(textArea);
            textArea.select();

            try {
                document.execCommand('copy');
                button.classList.add('copied');
                buttonText.textContent = '✓ Copied!';

                setTimeout(() => {
                    button.classList.remove('copied');
                    buttonText.textContent = 'Copy Link';
                }, 2000);
            } catch (err2) {
                buttonText.textContent = 'Failed to copy';
                setTimeout(() => {
                    buttonText.textContent = 'Copy Link';
                }, 2000);
            }

            document.body.removeChild(textArea);
        }
    });
}
