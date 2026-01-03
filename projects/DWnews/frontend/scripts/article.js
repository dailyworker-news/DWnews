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

        // Verification badge
        displayVerificationBadge(article);

        // Verification callout and references
        displayVerificationCallout(article);
        displayReferences(article);

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

        // Load and display corrections
        loadCorrections(article.id);

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

    // Use marked.js to parse markdown if available
    if (typeof marked !== 'undefined') {
        // Configure marked for safe rendering
        marked.setOptions({
            breaks: true,  // Convert \n to <br>
            gfm: true,     // GitHub Flavored Markdown
            sanitize: false // We trust our own content
        });

        return marked.parse(body);
    }

    // Fallback: Simple paragraph splitting if marked.js not loaded
    const paragraphs = body.split('\n\n').filter(p => p.trim());

    return paragraphs.map(p => {
        // Preserve single line breaks within paragraphs
        const content = p.trim().replace(/\n/g, '<br>');
        return `<p>${content}</p>`;
    }).join('');
}

// Display verification badge based on editorial notes
function displayVerificationBadge(article) {
    const verificationBadge = document.getElementById('verificationBadge');

    // Extract verification info from editorial_notes
    if (!article.editorial_notes) {
        return; // No verification info
    }

    const notes = article.editorial_notes.toLowerCase();
    let verificationLevel = null;
    let sourceCount = 0;

    // Parse verification level from editorial notes (new terminology)
    const sourceMatch = notes.match(/(\d+)\s*source/);
    if (sourceMatch) sourceCount = parseInt(sourceMatch[1]);

    if (notes.includes('multi-sourced') || notes.includes('multi-source')) {
        verificationLevel = 'multi-sourced';
    } else if (notes.includes('corroborated')) {
        verificationLevel = 'corroborated';
    } else if (notes.includes('aggregated')) {
        verificationLevel = 'aggregated';
    } else if (notes.includes('certified')) {
        verificationLevel = 'multi-sourced'; // Legacy mapping
    } else if (notes.includes('verified')) {
        verificationLevel = 'corroborated'; // Legacy mapping
    } else if (notes.includes('unverified')) {
        verificationLevel = 'aggregated'; // Legacy mapping
    }

    if (!verificationLevel) {
        return; // No verification info found
    }

    // Set badge content and class
    verificationBadge.className = 'article-badge badge-verification';

    switch(verificationLevel) {
        case 'multi-sourced':
            verificationBadge.classList.add('badge-multi-source');
            verificationBadge.innerHTML = `<span class="badge-icon">📰</span> Multi-Source`;
            verificationBadge.title = '5+ independent sources';
            break;
        case 'corroborated':
            verificationBadge.classList.add('badge-corroborated');
            verificationBadge.innerHTML = `<span class="badge-icon">📋</span> Corroborated`;
            verificationBadge.title = '2-4 independent sources';
            break;
        case 'aggregated':
            verificationBadge.classList.add('badge-aggregated');
            verificationBadge.innerHTML = `<span class="badge-icon">📄</span> Aggregated`;
            verificationBadge.title = 'Single credible source';
            break;
    }

    verificationBadge.style.display = 'inline-block';
}

// Display verification callout box with simplified text
function displayVerificationCallout(article) {
    const callout = document.getElementById('verificationCallout');
    const statusIcon = document.getElementById('verificationStatusIcon');
    const statusText = document.getElementById('verificationStatusText');
    const description = document.getElementById('verificationDescription');

    if (!article.editorial_notes) {
        return; // No verification info
    }

    const notes = article.editorial_notes.toLowerCase();
    let verificationLevel = null;
    let sourceCount = 0;

    // Extract verification level from editorial notes
    if (notes.includes('multi-sourced') || notes.includes('multi-source')) {
        verificationLevel = 'multi-sourced';
    } else if (notes.includes('corroborated')) {
        verificationLevel = 'corroborated';
    } else if (notes.includes('aggregated')) {
        verificationLevel = 'aggregated';
    } else if (notes.includes('certified')) {
        verificationLevel = 'multi-sourced'; // Legacy mapping
    } else if (notes.includes('verified')) {
        verificationLevel = 'corroborated'; // Legacy mapping
    } else if (notes.includes('unverified')) {
        verificationLevel = 'aggregated'; // Legacy mapping
    }

    // Extract source count
    const sourceMatch = notes.match(/(\d+)\s*source/);
    if (sourceMatch) {
        sourceCount = parseInt(sourceMatch[1]);
    }

    if (!verificationLevel) return;

    // Set content based on verification level
    switch(verificationLevel) {
        case 'multi-sourced':
            callout.className = 'verification-callout multi-source';
            statusIcon.textContent = '📰';
            statusText.textContent = 'Multi-Source';
            description.textContent = `${sourceCount}+ independent sources — see references below.`;
            break;
        case 'corroborated':
            callout.className = 'verification-callout corroborated';
            statusIcon.textContent = '📋';
            statusText.textContent = 'Corroborated';
            description.textContent = sourceCount > 0
                ? `${sourceCount} independent sources — see references below.`
                : '2-4 independent sources — see references below.';
            break;
        case 'aggregated':
            callout.className = 'verification-callout aggregated';
            statusIcon.textContent = '📄';
            statusText.textContent = 'Aggregated';
            description.textContent = sourceCount > 0
                ? `Single credible source — see references below.`
                : 'Single credible source — see references below.';
            break;
    }

    callout.style.display = 'block';
}

// Display references section
function displayReferences(article) {
    const referencesSection = document.getElementById('referencesSection');
    const referencesList = document.getElementById('referencesList');

    // Check if article has sources (would come from article_sources table)
    // For now, extract from editorial notes or sources field if available
    const references = [];

    // Try to get sources from article.sources (if populated by backend)
    if (article.sources && Array.isArray(article.sources) && article.sources.length > 0) {
        article.sources.forEach(source => {
            references.push({
                title: source.title || source.name || 'Source',
                url: source.url
            });
        });
    }

    // If no sources, don't show references section
    if (references.length === 0) {
        referencesSection.style.display = 'none';
        return;
    }

    // Build references list HTML
    const referencesHTML = references.map(ref => {
        if (ref.url) {
            return `<li><a href="${ref.url}" target="_blank" rel="noopener noreferrer">${ref.title}</a></li>`;
        } else {
            return `<li>${ref.title}</li>`;
        }
    }).join('');

    referencesList.innerHTML = referencesHTML;
    referencesSection.style.display = 'block';
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

// Load corrections for article
async function loadCorrections(articleId) {
    try {
        const response = await fetch(`${API_BASE_URL}/articles/${articleId}`);

        if (!response.ok) {
            return; // Fail silently if corrections endpoint not available
        }

        const article = await response.json();

        // Check if article has corrections (assuming corrections are included in article response)
        // For now, we'll need to update the backend to include corrections in article response
        // Or fetch corrections separately

        // Placeholder: Fetch corrections from monitoring endpoint
        const correctionsResponse = await fetch(`${API_BASE_URL}/articles/${articleId}/corrections`);

        if (correctionsResponse.ok) {
            const corrections = await correctionsResponse.json();

            if (corrections && corrections.length > 0) {
                displayCorrections(corrections);
            }
        }

    } catch (error) {
        console.error('Error loading corrections:', error);
        // Fail silently - corrections are optional
    }
}

// Display corrections on page
function displayCorrections(corrections) {
    const correctionNotice = document.getElementById('correctionNotice');
    const correctionsList = document.getElementById('correctionsList');

    if (!corrections || corrections.length === 0) {
        return;
    }

    // Filter for published corrections only
    const publishedCorrections = corrections.filter(c => c.is_published);

    if (publishedCorrections.length === 0) {
        return;
    }

    // Build corrections HTML
    let correctionsHTML = '';

    publishedCorrections.forEach(correction => {
        const correctionDate = formatCorrectionDate(correction.published_at);
        const severityClass = `correction-${correction.severity}`;

        correctionsHTML += `
            <div class="correction-item ${severityClass}">
                <p class="correction-meta">
                    <strong>${correctionDate}</strong> - ${formatCorrectionType(correction.correction_type)}
                </p>
                <p class="correction-description">${correction.public_notice || correction.description}</p>
                ${correction.incorrect_text ? `
                    <div class="correction-details">
                        <p><strong>Original:</strong> "${correction.incorrect_text}"</p>
                        <p><strong>Corrected:</strong> "${correction.correct_text}"</p>
                    </div>
                ` : ''}
            </div>
        `;
    });

    correctionsList.innerHTML = correctionsHTML;
    correctionNotice.style.display = 'block';
}

// Format correction date
function formatCorrectionDate(dateString) {
    if (!dateString) return '';

    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Format correction type
function formatCorrectionType(type) {
    const typeMap = {
        'factual_error': 'Factual Error',
        'source_error': 'Source Error',
        'clarification': 'Clarification',
        'update': 'Update',
        'retraction': 'Retraction'
    };

    return typeMap[type] || type;
}

