"""
Web Tools - Fetch and extract content from URLs

Provides tools for fetching web content and extracting article text.
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional
import time


class WebFetch:
    """
    Fetches content from URLs and extracts main article text
    """

    def __init__(self, timeout: int = 10):
        """
        Initialize WebFetch

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; DailyWorkerBot/1.0; +https://dailyworker.news)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

    def fetch(self, url: str, prompt: str = None) -> Optional[str]:
        """
        Fetch content from a URL and extract main article text

        Args:
            url: URL to fetch
            prompt: Optional prompt describing what to extract (currently ignored, for compatibility)

        Returns:
            Extracted article text, or None if fetch failed
        """
        try:
            # Add small delay to be respectful
            time.sleep(0.5)

            # Fetch the page
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'iframe', 'noscript']):
                element.decompose()

            # Try to find article content using common selectors
            article_content = None

            # Strategy 1: Look for <article> tag
            article_tag = soup.find('article')
            if article_tag:
                article_content = article_tag

            # Strategy 2: Look for common article class names
            if not article_content:
                for selector in [
                    {'class': 'article-content'},
                    {'class': 'post-content'},
                    {'class': 'entry-content'},
                    {'class': 'story-body'},
                    {'class': 'article-body'},
                    {'itemprop': 'articleBody'},
                ]:
                    article_content = soup.find('div', selector)
                    if article_content:
                        break

            # Strategy 3: Look for main content area
            if not article_content:
                main_tag = soup.find('main')
                if main_tag:
                    article_content = main_tag

            # Strategy 4: Fall back to body
            if not article_content:
                article_content = soup.find('body')

            if not article_content:
                return None

            # Extract text from paragraphs
            paragraphs = article_content.find_all('p')
            text_chunks = []

            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 50:  # Skip short paragraphs (likely navigation/ads)
                    text_chunks.append(text)

            # Join paragraphs
            article_text = '\n\n'.join(text_chunks)

            # Clean up whitespace
            article_text = ' '.join(article_text.split())

            return article_text if len(article_text) > 200 else None

        except requests.exceptions.Timeout:
            print(f"     Timeout fetching {url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"     Request error fetching {url}: {e}")
            return None
        except Exception as e:
            print(f"     Error processing {url}: {e}")
            return None


    def fetch_with_metadata(self, url: str) -> Optional[dict]:
        """
        Fetch content and extract metadata (title, author, date)

        Args:
            url: URL to fetch

        Returns:
            Dict with 'title', 'author', 'date', 'content' keys, or None if fetch failed
        """
        try:
            # Fetch content
            content = self.fetch(url)
            if not content:
                return None

            # Re-fetch to get metadata (could optimize by caching)
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title = None
            title_tag = soup.find('h1') or soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)

            # Extract author (common meta tags)
            author = None
            author_meta = soup.find('meta', {'name': 'author'}) or soup.find('meta', {'property': 'article:author'})
            if author_meta:
                author = author_meta.get('content')

            # Extract date
            date = None
            date_meta = soup.find('meta', {'property': 'article:published_time'}) or soup.find('time')
            if date_meta:
                date = date_meta.get('datetime') or date_meta.get('content') or date_meta.get_text(strip=True)

            return {
                'title': title,
                'author': author,
                'date': date,
                'content': content
            }

        except Exception as e:
            print(f"     Error fetching metadata from {url}: {e}")
            return None
