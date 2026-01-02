"""
Source Identifier

Identifies primary sources for topic verification using WebSearch.
Searches for original documents, press releases, academic papers, and news coverage.
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Source:
    """Represents a discovered source"""
    name: str
    url: str
    source_type: str  # government_document, academic, news_agency, organization_statement, etc.
    snippet: str = ""
    discovered_via: str = ""  # search query used
    credibility_tier: int = 0  # Set by SourceRanker later


class SourceIdentifier:
    """
    Identifies primary sources for a topic using various search strategies
    """

    def __init__(self, web_search_fn=None):
        """
        Initialize SourceIdentifier

        Args:
            web_search_fn: Optional function for web searching (for testing)
                          If None, will import WebSearch tool at runtime
        """
        self.web_search_fn = web_search_fn

    def identify_sources(self, topic_text: str, event_data: Optional[Dict] = None) -> List[Source]:
        """
        Identify sources for a topic using multiple search strategies

        Args:
            topic_text: The topic title/description to search for
            event_data: Optional dict with additional event context

        Returns:
            List of Source objects discovered
        """
        sources = []

        # Extract key entities for targeted searches
        entities = self._extract_entities(topic_text)

        # Strategy 1: Search for official/government sources
        official_sources = self._search_official_sources(topic_text, entities)
        sources.extend(official_sources)

        # Strategy 2: Search for academic papers
        academic_sources = self._search_academic_sources(topic_text, entities)
        sources.extend(academic_sources)

        # Strategy 3: Search for news coverage from credible outlets
        news_sources = self._search_news_sources(topic_text, entities)
        sources.extend(news_sources)

        # Strategy 4: Search for primary documents (press releases, reports)
        document_sources = self._search_documents(topic_text, entities)
        sources.extend(document_sources)

        # Deduplicate sources by URL
        sources = self._deduplicate_sources(sources)

        return sources

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract key entities from text for targeted searching

        Args:
            text: Topic text

        Returns:
            Dict with entity types and values
        """
        entities = {
            'organizations': [],
            'locations': [],
            'people': [],
            'topics': []
        }

        # Common organization patterns
        org_patterns = [
            r'\b([A-Z][A-Za-z]+ (?:Inc|Corp|LLC|Company|Corporation|Association|Union|Agency|Department))\b',
            r'\b(Amazon|Google|Apple|Microsoft|Meta|Tesla|Walmart|Starbucks|McDonald\'s)\b',
            r'\b(NLRB|OSHA|SEC|FTC|FDA|EPA|DOL|Department of Labor)\b',
            r'\b([A-Z]{2,})\b',  # Acronyms
        ]

        for pattern in org_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['organizations'].extend(matches)

        # Location patterns (cities, states)
        location_pattern = r'\b(New York|Los Angeles|Chicago|Houston|Phoenix|Philadelphia|San Antonio|San Diego|Dallas|San Jose|Austin|Seattle|Denver|Boston|Detroit|Portland|Atlanta|Miami|Baltimore|Oakland|Minneapolis|St\. Louis|Washington D\.C\.|California|Texas|Florida|New York|Pennsylvania|Illinois|Ohio|Georgia|North Carolina|Michigan)\b'
        entities['locations'] = re.findall(location_pattern, text, re.IGNORECASE)

        return entities

    def _search_official_sources(self, topic_text: str, entities: Dict) -> List[Source]:
        """
        Search for official government/regulatory sources

        Args:
            topic_text: Topic text
            entities: Extracted entities

        Returns:
            List of Source objects
        """
        sources = []
        search_queries = []

        # Build queries for government sources
        if entities['organizations']:
            for org in entities['organizations'][:3]:  # Limit to top 3
                search_queries.append(f"{org} official statement")
                search_queries.append(f"{org} government ruling")

        # General government source queries
        search_queries.append(f"{topic_text} NLRB ruling")
        search_queries.append(f"{topic_text} government report")
        search_queries.append(f"{topic_text} official statement")
        search_queries.append(f"{topic_text} court filing")

        # Execute searches (limit to avoid too many API calls)
        for query in search_queries[:4]:
            results = self._execute_search(query)
            for result in results:
                if self._is_official_source(result):
                    sources.append(Source(
                        name=result.get('title', 'Unknown'),
                        url=result['url'],
                        source_type='government_document',
                        snippet=result.get('snippet', ''),
                        discovered_via=query
                    ))

        return sources

    def _search_academic_sources(self, topic_text: str, entities: Dict) -> List[Source]:
        """
        Search for academic/peer-reviewed sources

        Args:
            topic_text: Topic text
            entities: Extracted entities

        Returns:
            List of Source objects
        """
        sources = []

        # Academic search queries
        search_queries = [
            f"{topic_text} academic research",
            f"{topic_text} study peer-reviewed",
            f"{topic_text} site:scholar.google.com",
            f"{topic_text} site:arxiv.org",
            f"{topic_text} site:jstor.org"
        ]

        for query in search_queries[:3]:  # Limit searches
            results = self._execute_search(query)
            for result in results:
                if self._is_academic_source(result):
                    sources.append(Source(
                        name=result.get('title', 'Unknown'),
                        url=result['url'],
                        source_type='academic',
                        snippet=result.get('snippet', ''),
                        discovered_via=query
                    ))

        return sources

    def _search_news_sources(self, topic_text: str, entities: Dict) -> List[Source]:
        """
        Search for credible news coverage

        Args:
            topic_text: Topic text
            entities: Extracted entities

        Returns:
            List of Source objects
        """
        sources = []

        # Target credible news outlets
        credible_outlets = [
            'reuters.com',
            'apnews.com',
            'bloomberg.com',
            'npr.org',
            'propublica.org',
            'nytimes.com',
            'washingtonpost.com'
        ]

        # Build site-specific queries
        search_queries = [f"{topic_text} site:{outlet}" for outlet in credible_outlets[:5]]

        # Also general news search
        search_queries.append(f"{topic_text} news")

        for query in search_queries[:4]:  # Limit searches
            results = self._execute_search(query)
            for result in results:
                sources.append(Source(
                    name=self._extract_outlet_name(result['url']),
                    url=result['url'],
                    source_type='news_agency',
                    snippet=result.get('snippet', ''),
                    discovered_via=query
                ))

        return sources

    def _search_documents(self, topic_text: str, entities: Dict) -> List[Source]:
        """
        Search for primary documents (press releases, reports, etc.)

        Args:
            topic_text: Topic text
            entities: Extracted entities

        Returns:
            List of Source objects
        """
        sources = []

        search_queries = [
            f"{topic_text} press release",
            f"{topic_text} official report",
            f"{topic_text} public records"
        ]

        if entities['organizations']:
            org = entities['organizations'][0]
            search_queries.append(f"{org} {topic_text} statement")

        for query in search_queries[:3]:  # Limit searches
            results = self._execute_search(query)
            for result in results:
                sources.append(Source(
                    name=result.get('title', 'Unknown'),
                    url=result['url'],
                    source_type='organization_statement',
                    snippet=result.get('snippet', ''),
                    discovered_via=query
                ))

        return sources

    def _execute_search(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Execute a web search query

        Args:
            query: Search query string
            max_results: Maximum results to return

        Returns:
            List of search results (dicts with title, url, snippet)
        """
        # If using custom search function (for testing), use it
        if self.web_search_fn:
            return self.web_search_fn(query, max_results)

        # In production, this would integrate with WebSearch tool
        # For now, return empty list as placeholder
        # The actual implementation will be in the main VerificationAgent
        # which has access to the WebSearch tool via Claude Code
        return []

    def _is_official_source(self, result: Dict) -> bool:
        """
        Check if a search result is from an official/government source

        Args:
            result: Search result dict

        Returns:
            True if official source
        """
        url = result['url'].lower()
        official_domains = [
            '.gov',
            'nlrb.gov',
            'osha.gov',
            'dol.gov',
            'sec.gov',
            'ftc.gov',
            'uscourts.gov'
        ]

        return any(domain in url for domain in official_domains)

    def _is_academic_source(self, result: Dict) -> bool:
        """
        Check if a search result is from an academic source

        Args:
            result: Search result dict

        Returns:
            True if academic source
        """
        url = result['url'].lower()
        academic_indicators = [
            'scholar.google',
            'arxiv.org',
            'jstor.org',
            '.edu/',
            'sciencedirect.com',
            'springer.com',
            'wiley.com',
            'researchgate.net',
            'academia.edu'
        ]

        title = result.get('title', '').lower()
        academic_terms = ['journal', 'study', 'research', 'peer-reviewed', 'paper']

        has_academic_url = any(indicator in url for indicator in academic_indicators)
        has_academic_title = any(term in title for term in academic_terms)

        return has_academic_url or has_academic_title

    def _extract_outlet_name(self, url: str) -> str:
        """
        Extract news outlet name from URL

        Args:
            url: URL string

        Returns:
            Outlet name
        """
        # Extract domain
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if domain_match:
            domain = domain_match.group(1)

            # Map common domains to outlet names
            outlet_map = {
                'reuters.com': 'Reuters',
                'apnews.com': 'Associated Press',
                'bloomberg.com': 'Bloomberg',
                'npr.org': 'NPR',
                'propublica.org': 'ProPublica',
                'nytimes.com': 'New York Times',
                'washingtonpost.com': 'Washington Post',
                'wsj.com': 'Wall Street Journal',
                'theguardian.com': 'The Guardian',
                'bbc.com': 'BBC',
                'cnn.com': 'CNN'
            }

            for key, name in outlet_map.items():
                if key in domain:
                    return name

            # Default: capitalize domain name
            return domain.replace('.com', '').replace('.org', '').title()

        return 'Unknown'

    def _deduplicate_sources(self, sources: List[Source]) -> List[Source]:
        """
        Remove duplicate sources by URL

        Args:
            sources: List of Source objects

        Returns:
            Deduplicated list of sources
        """
        seen_urls = set()
        unique_sources = []

        for source in sources:
            if source.url not in seen_urls:
                seen_urls.add(source.url)
                unique_sources.append(source)

        return unique_sources
