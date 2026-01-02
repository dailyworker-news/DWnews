# Sports Subscription Configuration - Implementation Plan

## Document Information

**Version:** 1.0
**Date:** 2026-01-01
**Phase:** 7.7 - Sports Subscription Configuration
**Dependencies:** Phase 7.1 (Database Schema), Phase 7.3 (Access Control)
**Complexity:** M

---

## Overview

Implement sports coverage as a subscription tier feature, starting with UK Premier League results. This allows The Daily Worker to provide working-class sports coverage while creating differentiated subscription value.

### Key Objectives

1. **Tier-based sports access**: Free users get no sports, basic subscribers get 1 league, premium subscribers get unlimited leagues
2. **User customization**: Subscribers can choose which league(s) to follow
3. **Automated sports content**: Ingest results and generate articles via specialized sports journalist agent
4. **Starting point**: UK Premier League (expandable to other leagues)
5. **Worker-centric sports coverage**: Focus on labor issues in sports, ticket affordability, fan culture

---

## Database Schema Extensions

### sports_leagues Table

```sql
CREATE TABLE sports_leagues (
    id SERIAL PRIMARY KEY,
    league_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    sport_type VARCHAR(50), -- football, basketball, baseball, etc.
    tier_requirement VARCHAR(20) NOT NULL, -- 'free', 'basic', 'premium'
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Initial data
INSERT INTO sports_leagues (league_code, name, country, sport_type, tier_requirement, display_order) VALUES
('EPL', 'English Premier League', 'England', 'football', 'basic', 1),
('NBA', 'National Basketball Association', 'USA', 'basketball', 'basic', 2),
('NFL', 'National Football League', 'USA', 'american_football', 'basic', 3),
('MLB', 'Major League Baseball', 'USA', 'baseball', 'basic', 4),
('NHL', 'National Hockey League', 'USA/Canada', 'hockey', 'basic', 5),
('LA_LIGA', 'La Liga', 'Spain', 'football', 'premium', 6),
('BUNDESLIGA', 'Bundesliga', 'Germany', 'football', 'premium', 7),
('SERIE_A', 'Serie A', 'Italy', 'football', 'premium', 8);

CREATE INDEX idx_sports_leagues_tier ON sports_leagues(tier_requirement);
CREATE INDEX idx_sports_leagues_active ON sports_leagues(is_active);
```

### user_sports_preferences Table

```sql
CREATE TABLE user_sports_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    league_id INTEGER NOT NULL REFERENCES sports_leagues(id) ON DELETE CASCADE,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, league_id)
);

CREATE INDEX idx_user_sports_prefs_user ON user_sports_preferences(user_id);
CREATE INDEX idx_user_sports_prefs_league ON user_sports_preferences(league_id);
```

### sports_results Table

```sql
CREATE TABLE sports_results (
    id SERIAL PRIMARY KEY,
    league_id INTEGER NOT NULL REFERENCES sports_leagues(id),
    match_date DATE NOT NULL,
    home_team VARCHAR(100) NOT NULL,
    away_team VARCHAR(100) NOT NULL,
    home_score INTEGER,
    away_score INTEGER,
    status VARCHAR(50), -- scheduled, live, finished, postponed
    summary TEXT,
    source_url TEXT,
    external_match_id VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sports_results_league ON sports_results(league_id);
CREATE INDEX idx_sports_results_date ON sports_results(match_date DESC);
CREATE INDEX idx_sports_results_status ON sports_results(status);
```

### articles Table Extension

```sql
-- Add sports_league_id column to existing articles table
ALTER TABLE articles ADD COLUMN sports_league_id INTEGER REFERENCES sports_leagues(id) NULL;

CREATE INDEX idx_articles_sports_league ON articles(sports_league_id);
```

---

## Subscription Tier Configuration

### subscription_plans.features_json Structure

```json
{
  "plan_name": "basic",
  "price_cents": 1500,
  "billing_interval": "month",
  "features": {
    "article_access": "unlimited",
    "sports_leagues_limit": 1,
    "sports_leagues_available": ["EPL", "NBA", "NFL", "MLB", "NHL"],
    "archive_access": true,
    "ad_free": true
  }
}
```

```json
{
  "plan_name": "premium",
  "price_cents": 2500,
  "billing_interval": "month",
  "features": {
    "article_access": "unlimited",
    "sports_leagues_limit": null,
    "sports_leagues_available": "*",
    "archive_access": true,
    "ad_free": true,
    "exclusive_sports_analysis": true
  }
}
```

### Free Tier (No Subscription)

- **Sports Access:** None
- **Display:** Sports articles hidden from homepage
- **CTA:** "Subscribe to access sports coverage" banner on Sports category page

---

## Sports Data Ingestion System

### Option 1: API-Football (Recommended for MVP)

**Service:** https://www.api-football.com/
**Pricing:** Free tier - 100 requests/day (sufficient for daily updates)

**Endpoint Example:**
```bash
GET https://v3.football.api-sports.io/fixtures?league=39&season=2025&from=2025-01-01&to=2025-01-07
Headers:
  x-rapidapi-key: {API_KEY}
```

**Response Format:**
```json
{
  "response": [
    {
      "fixture": {
        "id": 12345,
        "date": "2025-01-01T15:00:00+00:00",
        "status": { "short": "FT" }
      },
      "teams": {
        "home": { "name": "Arsenal" },
        "away": { "name": "Manchester United" }
      },
      "goals": {
        "home": 2,
        "away": 1
      }
    }
  ]
}
```

**Integration Plan:**
1. Daily cron job at 11 PM UTC (after most matches finish)
2. Fetch fixtures for EPL (league_id: 39) from last 3 days
3. Upsert to `sports_results` table (match on external_match_id)
4. Trigger sports journalist agent for finished matches

### Option 2: BBC Sport RSS (Fallback)

**Service:** BBC Sport RSS Feeds (free, no API key)
**URL:** https://feeds.bbci.co.uk/sport/football/rss.xml

**Pros:** Zero cost, reliable, no rate limits
**Cons:** Less structured data, requires HTML parsing

---

## Sports Journalist Agent

### Agent Definition: `.claude/agents/sports-journalist.md`

**Role:** Generate match reports and results summaries from sports data

**Capabilities:**
- Ingest structured match data from `sports_results` table
- Generate 200-300 word match reports
- Worker-centric angle: Ticket prices, fan culture, labor issues in sports
- Reading level: 7.5-8.5 Flesch-Kincaid
- Tone: Informative, accessible, working-class perspective

**Article Generation Workflow:**

```python
# Trigger: sports_results.status changes to 'finished'
# Input: sports_results record with match data

def generate_sports_article(match_id):
    match = db.query(sports_results).get(match_id)
    league = db.query(sports_leagues).get(match.league_id)

    # Build context for LLM
    context = {
        "league": league.name,
        "home_team": match.home_team,
        "away_team": match.away_team,
        "home_score": match.home_score,
        "away_score": match.away_score,
        "date": match.match_date
    }

    # Call LLM to generate article
    prompt = f"""
    Write a 200-word match report for {context['home_team']} vs {context['away_team']}
    in the {context['league']}.

    Final score: {context['home_team']} {context['home_score']} - {context['away_score']} {context['away_team']}

    Requirements:
    - Working-class perspective (focus on fans, ticket affordability, atmosphere)
    - Reading level: 7.5-8.5 Flesch-Kincaid
    - Include: match highlights, key moments, implications for league standings
    - Tone: Informative, accessible, worker-centric
    """

    article = llm.generate(prompt)

    # Store in articles table
    db.insert(articles, {
        "headline": f"{context['home_team']} {context['home_score']}-{context['away_score']} {context['away_team']}: Match Report",
        "body": article,
        "category_id": get_category_id("Sport"),
        "sports_league_id": match.league_id,
        "is_premium": False,  # Sports articles require subscription
        "status": "ai_review"
    })
```

---

## User Interface Components

### 1. Sports Preferences UI (Subscriber Dashboard)

**Location:** `/account/preferences/sports`

**Features:**
- Display available leagues based on user's subscription tier
- Checkbox list for each league (Basic: select 1, Premium: select unlimited)
- Visual indicator of tier requirement (Basic/Premium badge)
- "Upgrade to Premium" CTA for basic subscribers wanting more leagues
- Save button updates `user_sports_preferences` table

**Wireframe:**
```
+-------------------------------------------+
| Sports Preferences                         |
+-------------------------------------------+
| Select leagues to follow (1 allowed)       |
|                                            |
| [ ] English Premier League (Basic)         |
| [x] NBA (Basic)                            |
| [ ] NFL (Basic)                            |
| [ ] La Liga (Premium) [Upgrade to unlock]  |
|                                            |
| [Save Preferences]                         |
+-------------------------------------------+
```

### 2. Sports Section on Homepage

**Filtering Logic:**
```sql
-- Get sports articles for user's selected leagues
SELECT a.* FROM articles a
JOIN user_sports_preferences usp ON a.sports_league_id = usp.league_id
WHERE usp.user_id = {user_id}
  AND usp.enabled = TRUE
  AND a.category_id = (SELECT id FROM categories WHERE slug = 'sport')
ORDER BY a.publication_date DESC
LIMIT 10;
```

**Display:**
- "Your Sports" section if user has preferences set
- Show match reports from selected leagues only
- "Explore More Leagues" CTA if basic subscriber (upgrade prompt)

### 3. Admin Portal: Sports Leagues Management

**Location:** `/admin/sports/leagues`

**Features:**
- List all leagues with edit/delete actions
- Add new league form (name, country, tier requirement)
- Toggle league active/inactive status
- Reorder leagues (display_order)
- View subscriber count per league

### 4. Free User Paywall

**Location:** `/sport` category page when user not subscribed

**Display:**
```
+-------------------------------------------+
| Sport Coverage - Subscribe to Access      |
+-------------------------------------------+
| Get match reports, results, and analysis  |
| from your favorite leagues.               |
|                                            |
| [Subscribe for $15/month] [Learn More]    |
+-------------------------------------------+
```

---

## Access Control Logic

### Middleware: `check_sports_access(user, league_id)`

```python
def check_sports_access(user_id, league_id):
    """
    Verify user has access to requested sports league content.
    Returns: (has_access: bool, reason: str)
    """

    # 1. Check if user is subscribed
    subscription = db.query(subscriptions).filter_by(user_id=user_id, status='active').first()
    if not subscription:
        return (False, "subscription_required")

    # 2. Get league tier requirement
    league = db.query(sports_leagues).get(league_id)
    if league.tier_requirement == 'free':
        return (True, None)

    # 3. Get user's subscription plan
    plan = db.query(subscription_plans).get(subscription.plan_type)
    plan_features = json.loads(plan.features_json)

    # 4. Check tier access
    if league.tier_requirement == 'premium' and plan.plan_name != 'premium':
        return (False, "premium_required")

    # 5. Check user's selected leagues (Basic tier limit)
    if plan_features.get('sports_leagues_limit') is not None:
        user_prefs = db.query(user_sports_preferences).filter_by(
            user_id=user_id,
            league_id=league_id,
            enabled=True
        ).first()

        if not user_prefs:
            return (False, "league_not_selected")

    return (True, None)
```

### Article Endpoint Access Control

```python
@app.route('/api/articles/<slug>')
def get_article(slug):
    article = db.query(articles).filter_by(slug=slug).first()

    # If sports article, check access
    if article.sports_league_id:
        has_access, reason = check_sports_access(current_user.id, article.sports_league_id)

        if not has_access:
            if reason == "subscription_required":
                return {"error": "Subscription required", "upgrade_url": "/subscribe"}, 403
            elif reason == "premium_required":
                return {"error": "Premium subscription required", "upgrade_url": "/subscribe/premium"}, 403
            elif reason == "league_not_selected":
                return {"error": "League not in your preferences", "settings_url": "/account/preferences/sports"}, 403

    return article
```

---

## Testing Plan

### Test Cases

1. **Tier Access:**
   - Free user cannot see sports articles
   - Basic subscriber can select 1 league
   - Premium subscriber can select unlimited leagues
   - Basic subscriber cannot access premium-tier leagues

2. **User Preferences:**
   - Basic user can change selected league
   - Changing league updates homepage sports section
   - Disabling league hides its articles

3. **Sports Data Ingestion:**
   - API-Football daily fetch updates `sports_results`
   - Finished matches trigger article generation
   - Duplicate matches are upserted (no duplicates)

4. **Article Generation:**
   - Sports journalist agent generates 200-300 word reports
   - Reading level 7.5-8.5 validated
   - Articles linked to correct league_id
   - Articles marked as is_premium=False (require subscription)

5. **Upgrade Prompts:**
   - Free user sees "Subscribe to access sports" on /sport page
   - Basic user sees "Upgrade to Premium" when trying to add 2nd league
   - Premium prompt displays premium-only leagues

---

## Implementation Sequence

### Step 1: Database Schema (Phase 7.1)
- Create 3 new tables: `sports_leagues`, `user_sports_preferences`, `sports_results`
- Add `sports_league_id` column to `articles`
- Seed `sports_leagues` with initial leagues
- Test migrations locally

### Step 2: Subscription Plans Update (Phase 7.1)
- Update `subscription_plans` table with sports features
- Basic plan: `sports_leagues_limit: 1`
- Premium plan: `sports_leagues_limit: null` (unlimited)

### Step 3: Sports Data Ingestion (Phase 7.7)
- Integrate API-Football (free tier)
- Build daily cron job for EPL results
- Store results in `sports_results` table
- Test with historical data

### Step 4: Sports Journalist Agent (Phase 7.7)
- Create `.claude/agents/sports-journalist.md`
- Implement match report generation function
- Test with sample matches
- Validate reading level, worker-centric angle

### Step 5: Access Control (Phase 7.3 + 7.7)
- Implement `check_sports_access()` middleware
- Add sports article filtering on homepage
- Test tier-based access restrictions

### Step 6: User Interface (Phase 7.4 + 7.7)
- Build sports preferences page in subscriber dashboard
- Add sports section to homepage (filtered by preferences)
- Implement admin sports leagues management
- Add upgrade prompts for free/basic users

### Step 7: End-to-End Testing (Phase 7.7)
- Test complete flow: subscription → league selection → data ingestion → article generation → display
- Verify tier restrictions
- Test upgrade prompts
- Validate user preferences persistence

---

## Success Criteria

- [x] Database schema supports sports leagues, user preferences, and results
- [x] Basic subscribers can select 1 league, premium subscribers unlimited
- [x] UK Premier League results ingested daily via API-Football
- [x] Sports journalist agent generates match reports automatically
- [x] Homepage displays sports articles only from user's selected leagues
- [x] Free users see upgrade prompt on sports category page
- [x] Admin can manage leagues (add, edit, set tier requirements)
- [x] All access control rules enforced correctly

---

## Future Enhancements (Post-MVP)

### Additional Sports Coverage
- NBA (US basketball)
- NFL (US football)
- MLB (US baseball)
- La Liga, Bundesliga, Serie A (European football)

### Advanced Features
- Live score updates (WebSocket integration)
- Match prediction articles (pre-game analysis)
- League standings tables on category page
- Player transfer news (labor angle: contract negotiations, workers' rights in sports)
- Ticket price tracking (affordability for working-class fans)

### Worker-Centric Sports Coverage
- Union organizing in professional sports
- Stadium worker labor disputes
- Ticket affordability campaigns
- Fan ownership models
- Sports broadcasting monopolies

---

## API Cost Estimates

**API-Football Free Tier:**
- 100 requests/day
- Usage: 1 request/day for EPL results (7 requests/week)
- Cost: $0/month
- Upgrade path: Pro tier ($10/month) for 3,000 requests/day (all leagues)

**Alternative (BBC Sport RSS):**
- Cost: $0/month
- Reliability: High
- Data quality: Lower (requires parsing)

---

**Document End**
