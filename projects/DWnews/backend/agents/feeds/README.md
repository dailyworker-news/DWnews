# RSS Feed Sources - DWnews Content Aggregation

**Last Updated:** 2026-01-02 (Phase 11.2)
**Total Feeds:** 21 sources
**Event Discovery Target:** 30-60 events/day

---

## Overview

This directory contains the RSS feed aggregation system for DWnews. RSS feeds are the primary content discovery mechanism, providing unlimited, free, reliable news aggregation without API rate limits or authentication requirements.

**Strategic Context:**
Following Twitter API limitations (100 posts/month quota exhausted in 3 days), DWnews pivoted to an RSS-first aggregation model. RSS feeds provide sustainable, scalable content discovery with zero ongoing cost.

---

## Feed Sources (21 Total)

### CRITICAL Priority (3 feeds)
Daily updates, all content highly relevant to working class

1. **Labor Notes** - `https://labornotes.org/rss.xml`
   Union organizing, labor movement grassroots

2. **The Lever** - `https://www.levernews.com/rss`
   Worker-focused investigative journalism (David Sirota)

3. **Jacobin** - `https://jacobin.com/feed`
   Socialist labor perspective, leading left publication

### HIGH Priority (13 feeds)
Daily/weekly updates, labor-focused or keyword-filtered

4. **Reuters Business** - `https://www.reuters.com/rssFeed/businessNews`
   Major news, keyword-filtered for labor coverage

5. **Associated Press** - `https://apnews.com/rss`
   Major news, keyword-filtered for labor coverage

6. **ProPublica** - `https://www.propublica.org/feeds/propublica/main`
   Investigative journalism, labor violations

7. **ICIJ** - `https://www.icij.org/feed/`
   Global investigations, corporate accountability

8. **Reveal** - `https://revealnews.org/feed/`
   Center for Investigative Reporting, worker safety

9. **The Markup** - `https://themarkup.org/feeds/rss.xml`
   Tech accountability, algorithmic bias, worker surveillance

10. **The Intercept** - `https://theintercept.com/feed/`
    Investigative journalism, labor and community

11. **Democracy Now!** - `https://www.democracynow.org/democracynow.rss`
    Independent news, labor and protest coverage

12. **Al Jazeera** - `https://www.aljazeera.com/xml/rss/all.xml`
    International news, keyword-filtered

13. **The Guardian** - `https://www.theguardian.com/world/rss`
    UK news, strong labor coverage

14. **LaborPress NYC** - `https://www.laborpress.org/feed/`
    NYC labor news, union coverage

15. **Belt Magazine** - `https://beltmag.com/feed/`
    Rust Belt/Midwest labor, industrial manufacturing

16. **Scalawag** - `https://scalawagmagazine.org/feed/`
    Southern labor organizing, economic justice

### MEDIUM Priority (5 feeds)
Weekly/periodic updates, supplementary coverage

17. **Working Class Perspectives** - `https://workingclassstudies.wordpress.com/feed/`
    Academic labor analysis

18. **Economic Policy Institute** - `https://www.epi.org/blog/feed/`
    Labor economics, policy research

19. **Truthout** - `https://truthout.org/feed/`
    Alternative news, labor focus

20. **Common Dreams** - `https://www.commondreams.org/feeds/feed.rss`
    Progressive news, labor and environment

21. **BBC Sport** - `http://feeds.bbci.co.uk/sport/football/rss.xml`
    Sports coverage (Premier League focus)

---

## Geographic Coverage

- **National U.S.:** 15 feeds (Reuters, AP, ProPublica, Lever, Jacobin, Reveal, Intercept, Democracy Now, Guardian, Truthout, Common Dreams, EPI, Working Class Perspectives, Labor Notes, The Markup)
- **Regional U.S.:** 4 feeds
  - NYC: LaborPress
  - Midwest/Rust Belt: Belt Magazine
  - South: Scalawag
  - California: The Markup (now part of CalMatters)
- **International:** 4 feeds (Al Jazeera, Guardian, ICIJ, BBC)

---

## Worker Relevance Categories

### Union Organizing & Strikes
Labor Notes, The Lever, Jacobin, LaborPress, Belt Magazine, Scalawag

### Labor Economics & Policy
Economic Policy Institute, ProPublica, The Lever, Jacobin, Working Class Perspectives

### Worker Surveillance & Tech
The Markup, The Intercept

### Investigative Labor Violations
ICIJ, Reveal, ProPublica, The Lever

### Regional Labor Movements
LaborPress (NYC), Belt Magazine (Midwest), Scalawag (South), The Markup (California)

### International Labor
ICIJ, Al Jazeera, The Guardian

---

## Update Frequencies

### Daily Updates (14 sources)
Provide real-time news discovery for timely article generation:
- Reuters, AP, The Lever, Jacobin, ICIJ, Reveal, The Markup, LaborPress, The Intercept, Democracy Now, Al Jazeera, Guardian, Truthout, Common Dreams

### Weekly Updates (3 sources)
Provide curated analysis and depth:
- Belt Magazine, Scalawag, Working Class Perspectives

### Monthly Updates (0 sources)

### Variable (4 sources)
- Economic Policy Institute, Labor Notes, BBC Sport

**Combined Capacity:** 30-60 events/day from daily sources + 3-6 events/week from weekly sources

---

## Keyword Filtering Strategy

### No Keywords (All Content Relevant)
Labor-focused publications where all articles are relevant to working class:
- Labor Notes, The Lever, Jacobin, LaborPress, Belt Magazine, Working Class Perspectives, BBC Sport

### Keyword-Filtered (General News Sources)
General news sources filtered for labor-related content:
- **Reuters, AP, ProPublica, ICIJ, Reveal, The Markup, Truthout, Common Dreams, Democracy Now, Al Jazeera, Guardian, Intercept, Economic Policy Institute, Scalawag**

**Standard Keywords:**
labor, union, worker, workers, strike, wage, wages, employment, unemployment, workplace, organizing, bargaining, collective bargaining, picket, protest, demonstration, layoff, layoffs, firing, termination, benefit, benefits, healthcare, pension, retirement, safety, OSHA, injury, accident, violation, discrimination, harassment, retaliation, minimum wage, living wage, pay raise, salary, working class, blue collar, white collar, exploitation, corruption, wage theft, surveillance, gig economy, tech, algorithm, economic justice

---

## Feed Health & Reliability

### RSS Protocol Benefits
- **Open Standard:** RSS 2.0 spec from 2002, stable and widely supported
- **No Authentication:** No API keys required, no deprecation risk
- **No Rate Limits:** Unlimited polling frequency
- **High Availability:** 99%+ uptime for established news organizations
- **Zero Cost:** All sources provide free RSS feeds

### Comparison to Social Media APIs
| Aspect | RSS Feeds | Twitter API (Free) | Twitter API (Basic) |
|--------|-----------|-------------------|---------------------|
| **Cost** | $0 | $0 | $100/month |
| **Rate Limits** | None | 100 posts/month | Higher limits |
| **Authentication** | None required | API key required | API key required |
| **Sustainability** | High (open standard) | Low (quota exhausted in 3 days) | Medium (cost exceeds budget) |
| **Business Risk** | None (no corporate control) | High (sudden API changes) | Medium (pricing changes) |

**Decision:** RSS-first model provides sustainable, unlimited content aggregation

---

## Usage

### Basic Usage
```python
from backend.agents.feeds.rss_feeds import RSSFeedAggregator

# Initialize aggregator (fetch articles from last 24 hours)
aggregator = RSSFeedAggregator(max_age_hours=24)

# Fetch all feeds
events = aggregator.fetch_all_feeds()

# Process events
for event in events:
    print(f"Title: {event['title']}")
    print(f"Source: {event['discovered_from']}")
    print(f"Category: {event['suggested_category']}")
    print(f"Keywords: {event['keywords']}")
```

### Integration with Signal Intake Agent
```python
from backend.agents.signal_intake_agent import SignalIntakeAgent

agent = SignalIntakeAgent()
agent.run()  # Automatically fetches from all RSS feeds
```

---

## Testing

### Test Suite
Run comprehensive test suite (18 tests):
```bash
cd /Users/home/sandbox/daily_worker/projects/DWnews
python3 scripts/test_expanded_rss_feeds.py
```

**Expected Output:**
- Tests run: 18
- Successes: 18
- Failures: 0
- Errors: 0

### Test Coverage
- Source addition validation
- Total feed count (21 feeds)
- URL accuracy
- Priority level configuration
- Keyword filter setup
- Individual feed parsing (The Lever, Jacobin)
- Keyword filtering logic
- Deduplication across sources
- Event volume targets
- Geographic diversity
- Source credibility tiers
- Date format parsing (RSS 2.0 vs. Atom 1.0)
- Performance benchmarks
- Error handling (graceful feed failures)
- Worker relevance coverage
- Update frequency diversity

---

## Files in This Directory

### Core Implementation
- **`rss_feeds.py`** - Main RSS feed aggregator class (382 lines)
  - Fetches and parses 21 RSS feeds
  - Keyword filtering for general news sources
  - Event extraction and categorization
  - Error handling and logging

- **`twitter_feed.py`** - Twitter API integration (deprecated as primary source)
  - Now used only for trending topic monitoring (when quota allows)
  - 100 posts/month limit makes it unsuitable for daily content generation

- **`reddit_feed.py`** - Reddit API integration (deprecated as primary source)
  - Deprioritized due to API rate limits
  - Kept for potential future trending topic discovery

- **`government_feeds.py`** - Government RSS feeds (DOL, OSHA, BLS)
  - Supplementary source for labor policy and regulations

### Documentation
- **`README.md`** - This file (comprehensive feed documentation)
- **`RSS_SOURCE_RESEARCH.md`** - Phase 11.1 research (18 sources evaluated)
- **`PRIORITY_RANKING.md`** - Source prioritization and implementation plan
- **`source_evaluation_matrix.csv`** - Credibility scores and metadata for all sources

---

## Future Expansion

### Phase 11.3: Feed Health Monitoring (Next Phase)
- Build feed health monitoring system
- Create `feed_health_log` table
- Implement health checks and alerting
- Admin dashboard for feed status
- Automatic feed disabling/re-activation

### Batch 2 (Future - Target 30+ Feeds)
Additional sources to add after Phase 11.3 complete:

**Blocked/Requires Research (5 sources):**
1. Documented - https://documentedny.com/feed/ (403 blocked, need whitelist)
2. CEPR - https://cepr.net/feed/ (403 blocked, need whitelist)
3. WNY Labor Today (404, manual investigation needed)
4. ITUC - International Trade Union Confederation (404, find correct RSS path)
5. ILO - International Labour Organization (404, check Newsroom for RSS)

**State-Level Expansion (5-7 sources):**
1. AFL-CIO State Chapters (CA, IL, TX, MI, OH)
2. ProPublica State Bureaus (TX, IL, CA)
3. Regional labor publications

**Potential (2 sources):**
1. IndustriALL Global Union - https://www.industriall-union.org/rss.xml (validated but lower priority)
2. More Perfect Union (YouTube RSS integration - requires Phase 12)

**Target:** 30+ feeds, 50-70 events/day, comprehensive U.S. regional coverage

---

## Version History

### v2.0 - 2026-01-02 (Phase 11.2)
- Added 8 new sources (Batch 1): The Lever, Jacobin, ICIJ, Reveal, The Markup, LaborPress, Belt Magazine, Scalawag
- Total feeds: 13 → 21 (62% increase)
- Target event discovery: 10-20/day → 30-60/day
- Established RSS-first aggregation model
- Comprehensive test suite (18 tests, 100% passing)

### v1.0 - 2025-12-29 (Phase 6.2)
- Initial implementation with 13 RSS sources
- Basic keyword filtering
- Event extraction and categorization
- Integration with Signal Intake Agent

---

## Maintenance

### Adding New Sources
1. Research and validate RSS feed URL
2. Determine priority level (CRITICAL, HIGH, MEDIUM)
3. Configure keyword filters (if general news source)
4. Add to `FEED_SOURCES` dictionary in `rss_feeds.py`
5. Write test case in `test_expanded_rss_feeds.py`
6. Update this README with new source details
7. Update `PRIORITY_RANKING.md` and `source_evaluation_matrix.csv`

### Troubleshooting Feed Failures
1. Check feed URL is still active (RSS often changes URL structure)
2. Verify feed format (RSS 2.0 vs. Atom 1.0)
3. Check for bot protection (403 errors)
4. Review parsing errors in logs
5. Test with `feedparser` library directly

### Monitoring
- Track event discovery rates (should maintain 30-60/day)
- Monitor feed failures (alert if source down >24 hours)
- Review keyword filter effectiveness (adjust if too many/few articles)
- Validate geographic balance (ensure all regions represented)

---

## Support

For questions or issues:
1. Review test suite: `scripts/test_expanded_rss_feeds.py`
2. Check dev logs: `docs/dev-log-phase-11.2.md`
3. Review Phase 11.1 research: `backend/agents/feeds/RSS_SOURCE_RESEARCH.md`

---

**Last Updated:** 2026-01-02 (Phase 11.2)
**Maintained By:** DWnews Development Team
**Status:** Production Ready ✅
