"""
Deep Context Research Module for Investigatory Journalist Agent - Phase 6.9.3

Provides comprehensive historical and geographic context for labor events:
- Historical event research (precedents, similar past events)
- Key actor profiling (organizations, people, track records)
- Local news source aggregation (geographic-specific sources)
- Geographic context gathering (regional political/economic factors)
- Related event clustering (identifying patterns across events)
- Context richness scoring (0-100 scale)

This module enhances investigation with deep background research and pattern recognition.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict, field

logger = logging.getLogger(__name__)


@dataclass
class HistoricalEvent:
    """Historical event precedent."""

    title: str
    description: str
    date: datetime
    location: str
    source_url: str

    # Similarity metrics
    similarity_score: float = 0.0  # 0-100, how similar to current event
    relevance_factors: List[str] = field(default_factory=list)  # What makes it relevant

    # Outcomes
    outcome: Optional[str] = None
    lessons_learned: List[str] = field(default_factory=list)

    # Context
    key_actors: List[str] = field(default_factory=list)
    economic_conditions: Optional[str] = None
    political_climate: Optional[str] = None


@dataclass
class ActorProfile:
    """Profile of a key actor (person or organization)."""

    name: str
    actor_type: str  # 'union', 'company', 'person', 'government', 'ngo'

    # Background
    description: str
    founded_year: Optional[int] = None
    headquarters_location: Optional[str] = None

    # Track record
    past_actions: List[str] = field(default_factory=list)
    victories: List[str] = field(default_factory=list)
    defeats: List[str] = field(default_factory=list)
    controversies: List[str] = field(default_factory=list)

    # Current status
    current_leadership: List[str] = field(default_factory=list)
    current_strategy: Optional[str] = None

    # Credibility assessment
    credibility_score: float = 0.0  # 0-100
    bias_indicator: Optional[str] = None  # 'pro-labor', 'pro-management', 'neutral'

    # Sources
    source_urls: List[str] = field(default_factory=list)
    verified_facts: List[str] = field(default_factory=list)


@dataclass
class GeographicContext:
    """Geographic and regional context for an event."""

    location: str
    region: str  # e.g., 'Midwest', 'Northeast', 'South', etc.
    state: Optional[str] = None
    city: Optional[str] = None

    # Economic context
    unemployment_rate: Optional[float] = None
    median_income: Optional[float] = None
    major_industries: List[str] = field(default_factory=list)
    economic_trends: List[str] = field(default_factory=list)

    # Political context
    political_lean: Optional[str] = None  # 'conservative', 'liberal', 'mixed'
    labor_law_environment: Optional[str] = None  # 'pro-labor', 'anti-labor', 'neutral'
    recent_elections: List[str] = field(default_factory=list)

    # Labor context
    union_density: Optional[float] = None  # Percentage of workforce unionized
    recent_labor_actions: List[str] = field(default_factory=list)
    active_unions: List[str] = field(default_factory=list)

    # Local news sources
    local_news_outlets: List[str] = field(default_factory=list)
    labor_reporters: List[str] = field(default_factory=list)


@dataclass
class EventCluster:
    """Cluster of related events showing patterns."""

    cluster_name: str
    pattern_description: str

    events: List[Dict] = field(default_factory=list)
    common_factors: List[str] = field(default_factory=list)

    # Pattern analysis
    time_span_days: int = 0
    geographic_spread: List[str] = field(default_factory=list)
    shared_actors: List[str] = field(default_factory=list)
    trend_direction: Optional[str] = None  # 'escalating', 'declining', 'stable'

    # Predictive value
    predictive_power: float = 0.0  # 0-100, how well cluster predicts future events


@dataclass
class ContextResearch:
    """Complete context research results."""

    topic_title: str
    research_date: datetime

    # Historical precedents
    historical_events: List[HistoricalEvent] = field(default_factory=list)
    most_relevant_precedent: Optional[HistoricalEvent] = None

    # Key actors
    actor_profiles: List[ActorProfile] = field(default_factory=list)
    primary_actors: List[ActorProfile] = field(default_factory=list)  # Most important actors

    # Geographic context
    geographic_context: Optional[GeographicContext] = None

    # Event patterns
    event_clusters: List[EventCluster] = field(default_factory=list)
    identified_patterns: List[str] = field(default_factory=list)

    # Local news
    local_sources: List[str] = field(default_factory=list)
    local_coverage_summary: Optional[str] = None

    # Analysis
    context_richness_score: float = 0.0  # 0-100
    research_completeness: str = 'unknown'  # 'comprehensive', 'partial', 'limited'
    research_notes: List[str] = field(default_factory=list)


class DeepContextResearcher:
    """
    Deep context research for labor events.

    Provides:
    - Historical precedent research
    - Key actor profiling
    - Geographic and economic context
    - Pattern identification across related events
    - Local news source aggregation
    """

    def __init__(self, use_mock_data: bool = False):
        """
        Initialize deep context researcher.

        Args:
            use_mock_data: If True, use mock data for testing
        """
        self.use_mock_data = use_mock_data

        # Historical labor events database (in production, this would be a real database)
        self.historical_db = self._initialize_historical_db()

        # Actor database (unions, companies, etc.)
        self.actor_db = self._initialize_actor_db()

        # Geographic data
        self.geographic_db = self._initialize_geographic_db()

    def research_context(
        self,
        topic_title: str,
        topic_description: str,
        keywords: List[str],
        location: Optional[str] = None,
        actors: Optional[List[str]] = None
    ) -> ContextResearch:
        """
        Conduct comprehensive context research for a topic.

        Args:
            topic_title: Title of the topic
            topic_description: Description of the topic
            keywords: List of keywords
            location: Geographic location (optional)
            actors: List of known actors/organizations (optional)

        Returns:
            ContextResearch with all findings
        """
        logger.info(f"Starting deep context research: {topic_title}")
        logger.info(f"Keywords: {keywords}")
        logger.info(f"Location: {location}")
        logger.info(f"Actors: {actors}")

        # 1. Research historical precedents
        historical_events = self._research_historical_precedents(keywords, location)
        logger.info(f"Found {len(historical_events)} historical precedents")

        # 2. Profile key actors
        actor_profiles = self._profile_actors(actors or keywords, topic_description)
        logger.info(f"Profiled {len(actor_profiles)} key actors")

        # 3. Gather geographic context
        geographic_context = None
        if location:
            geographic_context = self._research_geographic_context(location)
            logger.info(f"Gathered geographic context for {location}")

        # 4. Identify event patterns
        event_clusters = self._identify_event_clusters(keywords, historical_events)
        logger.info(f"Identified {len(event_clusters)} event patterns")

        # 5. Aggregate local news sources
        local_sources = []
        if location:
            local_sources = self._aggregate_local_news(location)
            logger.info(f"Found {len(local_sources)} local news sources")

        # Find most relevant precedent
        most_relevant = None
        if historical_events:
            most_relevant = max(historical_events, key=lambda e: e.similarity_score)

        # Identify primary actors (top 3 by credibility)
        primary_actors = sorted(actor_profiles, key=lambda a: a.credibility_score, reverse=True)[:3]

        # Calculate context richness score
        context_richness = self._calculate_context_richness(
            len(historical_events),
            len(actor_profiles),
            geographic_context is not None,
            len(event_clusters),
            len(local_sources)
        )

        # Determine research completeness
        completeness = self._assess_completeness(context_richness)

        research = ContextResearch(
            topic_title=topic_title,
            research_date=datetime.utcnow(),
            historical_events=historical_events,
            most_relevant_precedent=most_relevant,
            actor_profiles=actor_profiles,
            primary_actors=primary_actors,
            geographic_context=geographic_context,
            event_clusters=event_clusters,
            identified_patterns=[cluster.pattern_description for cluster in event_clusters],
            local_sources=local_sources,
            local_coverage_summary=f"Found {len(local_sources)} local news outlets covering labor issues" if local_sources else None,
            context_richness_score=context_richness,
            research_completeness=completeness,
            research_notes=[]
        )

        logger.info(f"Context research complete: {context_richness:.1f}/100 richness score ({completeness})")

        return research

    def _research_historical_precedents(
        self,
        keywords: List[str],
        location: Optional[str]
    ) -> List[HistoricalEvent]:
        """Research historical labor events similar to current event."""

        if self.use_mock_data:
            return self._generate_mock_historical_events(keywords)

        # In production: Search historical database, news archives, labor history sources
        # For now, return mock data
        return self._generate_mock_historical_events(keywords)

    def _profile_actors(
        self,
        actor_names: List[str],
        context: str
    ) -> List[ActorProfile]:
        """Profile key actors involved in the event."""

        if self.use_mock_data:
            return self._generate_mock_actor_profiles(actor_names)

        # In production: Search actor database, Wikipedia, news sources, union websites
        # For now, return mock data
        return self._generate_mock_actor_profiles(actor_names)

    def _research_geographic_context(
        self,
        location: str
    ) -> GeographicContext:
        """Research geographic and regional context."""

        if self.use_mock_data:
            return self._generate_mock_geographic_context(location)

        # In production: Query census data, BLS data, local news databases
        # For now, return mock data
        return self._generate_mock_geographic_context(location)

    def _identify_event_clusters(
        self,
        keywords: List[str],
        historical_events: List[HistoricalEvent]
    ) -> List[EventCluster]:
        """Identify patterns across related events."""

        if not historical_events:
            return []

        # Simple clustering by keywords
        clusters = []

        # Look for industry patterns
        if any(kw in ['amazon', 'warehouse', 'logistics'] for kw in [k.lower() for k in keywords]):
            cluster = EventCluster(
                cluster_name="E-commerce Warehouse Organizing Wave",
                pattern_description="Surge in warehouse worker organizing at major e-commerce companies",
                events=[asdict(e) for e in historical_events if 'warehouse' in e.title.lower()],
                common_factors=["Warehouse work conditions", "Corporate resistance", "Worker solidarity"],
                time_span_days=730,  # 2 years
                geographic_spread=["New York", "California", "Illinois"],
                shared_actors=["Amazon", "Warehouse workers", "ALU"],
                trend_direction="escalating",
                predictive_power=75.0
            )
            clusters.append(cluster)

        # Look for strike patterns
        if any(kw in ['strike', 'walkout', 'picket'] for kw in [k.lower() for k in keywords]):
            cluster = EventCluster(
                cluster_name="Post-Pandemic Strike Wave",
                pattern_description="Increased strike activity following COVID-19 pandemic",
                events=[asdict(e) for e in historical_events if 'strike' in e.title.lower()],
                common_factors=["Wage demands", "Safety concerns", "Union recognition"],
                time_span_days=1095,  # 3 years
                geographic_spread=["Nationwide"],
                shared_actors=["Various unions", "Workers"],
                trend_direction="escalating",
                predictive_power=80.0
            )
            clusters.append(cluster)

        return clusters

    def _aggregate_local_news(
        self,
        location: str
    ) -> List[str]:
        """Aggregate local news sources for geographic area."""

        # In production: Query local news database, Google News, regional outlets
        # For now, return mock data based on major cities

        local_outlets = {
            'new york': [
                'New York Daily News',
                'Gothamist',
                'NY1',
                'City & State New York'
            ],
            'chicago': [
                'Chicago Tribune',
                'Block Club Chicago',
                'Chicago Reader',
                'WBEZ Chicago'
            ],
            'seattle': [
                'The Seattle Times',
                'Crosscut',
                'KUOW',
                'Seattle Weekly'
            ],
            'san francisco': [
                'San Francisco Chronicle',
                'Mission Local',
                'KQED',
                'SF Examiner'
            ]
        }

        location_lower = location.lower()
        for city, outlets in local_outlets.items():
            if city in location_lower:
                return outlets

        # Default local sources
        return ['Local newspaper', 'Regional news network', 'City magazine']

    def _calculate_context_richness(
        self,
        num_historical: int,
        num_actors: int,
        has_geographic: bool,
        num_patterns: int,
        num_local_sources: int
    ) -> float:
        """Calculate context richness score (0-100)."""

        score = 0.0

        # Historical precedents (0-30 points)
        if num_historical >= 5:
            score += 30
        elif num_historical >= 3:
            score += 20
        elif num_historical >= 1:
            score += 10

        # Actor profiles (0-25 points)
        if num_actors >= 5:
            score += 25
        elif num_actors >= 3:
            score += 20
        elif num_actors >= 1:
            score += 10

        # Geographic context (20 points)
        if has_geographic:
            score += 20

        # Event patterns (0-15 points)
        if num_patterns >= 3:
            score += 15
        elif num_patterns >= 2:
            score += 10
        elif num_patterns >= 1:
            score += 5

        # Local sources (0-10 points)
        if num_local_sources >= 5:
            score += 10
        elif num_local_sources >= 3:
            score += 7
        elif num_local_sources >= 1:
            score += 4

        return min(score, 100)

    def _assess_completeness(self, context_richness: float) -> str:
        """Assess research completeness based on richness score."""
        if context_richness >= 75:
            return 'comprehensive'
        elif context_richness >= 50:
            return 'partial'
        else:
            return 'limited'

    def _initialize_historical_db(self) -> Dict:
        """Initialize historical events database."""
        return {}

    def _initialize_actor_db(self) -> Dict:
        """Initialize actor database."""
        return {}

    def _initialize_geographic_db(self) -> Dict:
        """Initialize geographic data."""
        return {}

    def _generate_mock_historical_events(self, keywords: List[str]) -> List[HistoricalEvent]:
        """Generate mock historical events for testing."""
        logger.info("Generating mock historical events")

        events = [
            HistoricalEvent(
                title="Amazon Staten Island Warehouse Workers Vote to Unionize (2022)",
                description="Workers at Amazon's JFK8 warehouse in Staten Island vote 2654-2131 to join the Amazon Labor Union, marking the first successful union drive at an Amazon facility in the United States.",
                date=datetime(2022, 4, 1),
                location="Staten Island, New York",
                source_url="https://example.com/amazon-union-2022",
                similarity_score=85.0,
                relevance_factors=[
                    "Amazon warehouse organizing",
                    "Grassroots union campaign",
                    "Worker-led organizing without traditional union backing"
                ],
                outcome="Union victory",
                lessons_learned=[
                    "Worker-led campaigns can succeed against corporate opposition",
                    "Focus on workplace conditions resonates with workers",
                    "Social media effective for organizing"
                ],
                key_actors=["Amazon Labor Union", "Chris Smalls", "Amazon"],
                economic_conditions="Post-pandemic labor shortage",
                political_climate="Increased labor activism nationwide"
            ),
            HistoricalEvent(
                title="Starbucks Workers United Campaign Begins (2021)",
                description="Workers at three Buffalo-area Starbucks stores file for union elections with NLRB, launching a nationwide organizing campaign that spreads to hundreds of stores.",
                date=datetime(2021, 8, 30),
                location="Buffalo, New York",
                source_url="https://example.com/starbucks-union-2021",
                similarity_score=75.0,
                relevance_factors=[
                    "Service worker organizing",
                    "Chain store unionization",
                    "Youth-led labor movement"
                ],
                outcome="Ongoing campaign with 300+ stores unionized",
                lessons_learned=[
                    "Store-by-store strategy can build momentum",
                    "Young workers enthusiastic about unions",
                    "Public support crucial for service worker campaigns"
                ],
                key_actors=["Starbucks Workers United", "Workers United", "Starbucks"],
                economic_conditions="Post-pandemic service industry recovery",
                political_climate="Growing labor movement among young workers"
            ),
            HistoricalEvent(
                title="UAW Strike Against Big Three Automakers (2023)",
                description="United Auto Workers launches historic simultaneous strike against GM, Ford, and Stellantis, using novel 'stand-up strike' strategy targeting key plants.",
                date=datetime(2023, 9, 15),
                location="Detroit, Michigan",
                source_url="https://example.com/uaw-strike-2023",
                similarity_score=70.0,
                relevance_factors=[
                    "Major industrial strike",
                    "Pattern bargaining",
                    "Strategic targeting of key facilities"
                ],
                outcome="Union victory with significant wage gains",
                lessons_learned=[
                    "Strategic strikes more effective than full walkout",
                    "Public messaging crucial for public support",
                    "Solidarity across plants strengthens bargaining power"
                ],
                key_actors=["UAW", "Shawn Fain", "GM", "Ford", "Stellantis"],
                economic_conditions="Strong auto industry profits",
                political_climate="Pro-labor Biden administration"
            )
        ]

        return events

    def _generate_mock_actor_profiles(self, actor_names: List[str]) -> List[ActorProfile]:
        """Generate mock actor profiles for testing."""
        logger.info(f"Generating mock actor profiles for: {actor_names}")

        profiles = []

        # Check if Amazon is mentioned
        if any('amazon' in name.lower() for name in actor_names):
            profiles.append(ActorProfile(
                name="Amazon",
                actor_type="company",
                description="Global e-commerce and technology company, second-largest private employer in the United States",
                founded_year=1994,
                headquarters_location="Seattle, Washington",
                past_actions=[
                    "Opposed unionization efforts at facilities nationwide",
                    "Increased starting wages to $15/hour in 2018",
                    "Implemented surveillance systems in warehouses"
                ],
                victories=["Defeated union drives at Bessemer, Alabama warehouse (2021, 2022)"],
                defeats=["Lost union election at Staten Island JFK8 warehouse (2022)"],
                controversies=[
                    "Warehouse injury rates higher than industry average",
                    "Anti-union tactics including mandatory meetings",
                    "Fired workers involved in organizing"
                ],
                current_leadership=["Andy Jassy (CEO)"],
                current_strategy="Opposing unionization through legal challenges and workplace improvements",
                credibility_score=60.0,
                bias_indicator="pro-management",
                source_urls=["https://example.com/amazon-labor-history"],
                verified_facts=[
                    "Employs over 1.5 million people worldwide",
                    "One successful union at JFK8 warehouse (2022)",
                    "Multiple pending NLRB complaints"
                ]
            ))

        # Check if ALU is mentioned
        if any('alu' in name.lower() or 'labor union' in name.lower() for name in actor_names):
            profiles.append(ActorProfile(
                name="Amazon Labor Union (ALU)",
                actor_type="union",
                description="Independent labor union formed by current and former Amazon workers to organize Amazon facilities",
                founded_year=2021,
                headquarters_location="Staten Island, New York",
                past_actions=[
                    "Organized grassroots campaign at JFK8 warehouse",
                    "Won union election April 2022",
                    "Filed unfair labor practice charges against Amazon"
                ],
                victories=["JFK8 warehouse union election (2654-2131, April 2022)"],
                defeats=["Lost election at LDJ5 warehouse (618-380, May 2022)"],
                controversies=["Internal leadership disputes (2023)"],
                current_leadership=["Chris Smalls (President)", "Derrick Palmer (Vice President)"],
                current_strategy="Attempting to secure first contract with Amazon, organizing additional facilities",
                credibility_score=75.0,
                bias_indicator="pro-labor",
                source_urls=["https://example.com/alu-history"],
                verified_facts=[
                    "First successful Amazon union in United States",
                    "Independent union, not affiliated with established labor organizations",
                    "Over 8,000 workers in bargaining unit"
                ]
            ))

        # Default generic profiles if no specific actors matched
        if not profiles:
            profiles.append(ActorProfile(
                name="Workers' Coalition",
                actor_type="union",
                description="Labor organizing group",
                credibility_score=70.0,
                bias_indicator="pro-labor"
            ))

        return profiles

    def _generate_mock_geographic_context(self, location: str) -> GeographicContext:
        """Generate mock geographic context for testing."""
        logger.info(f"Generating mock geographic context for: {location}")

        # Parse location
        parts = [p.strip() for p in location.split(',')]
        city = parts[0] if parts else location
        state = parts[1] if len(parts) > 1 else None

        # Mock data based on major cities
        if 'new york' in location.lower():
            return GeographicContext(
                location=location,
                region="Northeast",
                state="New York",
                city="New York City",
                unemployment_rate=4.3,
                median_income=67000,
                major_industries=["Finance", "Technology", "Retail", "Healthcare"],
                economic_trends=["Strong post-pandemic recovery", "Rising cost of living"],
                political_lean="liberal",
                labor_law_environment="pro-labor",
                recent_elections=["Democratic mayor elected 2021"],
                union_density=23.5,
                recent_labor_actions=[
                    "Amazon JFK8 union victory (2022)",
                    "Starbucks organizing wave (2021-2023)",
                    "NYC delivery worker campaigns"
                ],
                active_unions=["32BJ SEIU", "TWU Local 100", "1199SEIU", "ALU"],
                local_news_outlets=["NY Daily News", "Gothamist", "NY1"],
                labor_reporters=["Josh Eidelson", "Sara Ashley O'Brien"]
            )

        # Default context
        return GeographicContext(
            location=location,
            region="Unknown",
            state=state,
            city=city,
            unemployment_rate=5.0,
            median_income=55000,
            major_industries=["Varied"],
            political_lean="mixed",
            labor_law_environment="neutral",
            union_density=10.0,
            local_news_outlets=["Local newspaper"],
            labor_reporters=[]
        )


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    researcher = DeepContextResearcher(use_mock_data=True)

    research = researcher.research_context(
        topic_title="Amazon Warehouse Workers Authorize Strike",
        topic_description="Workers at Amazon's fulfillment center vote to authorize strike action over wages and working conditions",
        keywords=["amazon", "warehouse", "strike", "alu"],
        location="Staten Island, New York",
        actors=["Amazon", "Amazon Labor Union"]
    )

    print(f"\n=== Deep Context Research Results ===")
    print(f"Context Richness: {research.context_richness_score:.1f}/100 ({research.research_completeness})")
    print(f"\nHistorical Precedents: {len(research.historical_events)}")
    if research.most_relevant_precedent:
        print(f"  Most Relevant: {research.most_relevant_precedent.title}")
        print(f"  Similarity: {research.most_relevant_precedent.similarity_score:.1f}/100")

    print(f"\nKey Actors: {len(research.actor_profiles)}")
    for actor in research.primary_actors:
        print(f"  - {actor.name} ({actor.actor_type})")
        print(f"    Credibility: {actor.credibility_score:.1f}/100")
        print(f"    Bias: {actor.bias_indicator}")

    if research.geographic_context:
        print(f"\nGeographic Context: {research.geographic_context.location}")
        print(f"  Union Density: {research.geographic_context.union_density}%")
        print(f"  Labor Environment: {research.geographic_context.labor_law_environment}")

    print(f"\nEvent Patterns: {len(research.event_clusters)}")
    for cluster in research.event_clusters:
        print(f"  - {cluster.cluster_name}")
        print(f"    Trend: {cluster.trend_direction}")
