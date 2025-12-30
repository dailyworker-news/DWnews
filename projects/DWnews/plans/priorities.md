# The Daily Worker - Strategic Priorities

**Document Version:** 1.0
**Date:** 2025-12-29
**Project:** The Daily Worker (DWnews)

---

## Value Proposition

Accurate, worker-centric news that doesn't pull punches.

**Why This Matters:**
- Corporate media serves advertisers and shareholders, not workers
- Working-class perspective systematically underrepresented in news coverage
- Mainstream outlets pull punches on issues affecting labor (union-busting, wage theft, workplace safety)
- Target audience: Workers who need news about issues affecting their livelihoods and economic security

---

## Strategic Rationale

### Why Worker-Centric News
**Market Gap:** Existing news prioritizes elite perspectives. Workers want coverage that doesn't frame labor struggles through a corporate lens.

**Content Approach:** "Doesn't pull punches" means:
- Calling union-busting what it is
- Honest framing of wage theft and exploitation
- No both-sidesing of worker vs. employer conflicts when facts are clear
- Accessible language (8th-grade level) without dumbing down substance

### Why NEW + CONTINUING Stories
**Problem Solved:** News cycle abandons ongoing struggles (strikes, organizing campaigns, legislative battles) after initial coverage. Workers need to track these to the end.

**Differentiation:** Corporate media moves on when stories stop generating clicks. We maintain visibility for ongoing worker issues.

**Implementation:** Dual display keeps breaking news fresh while ensuring multi-week stories (e.g., strike in progress) don't disappear.

### Why National (5+) + Local (5+) Split
**Relevance:** National issues matter (federal labor law, Supreme Court decisions) but local impacts daily life (state minimum wage, local union elections, nearby plant closures).

**Reader Value:** Workers care about both what affects all workers AND what's happening in their region.

**Operational:** Start with fewer states, expand as capacity allows. National default ensures value even before local coverage scales.

### Why GCP (vs. AWS/Azure/Others)
**Integration:** Seamless Gemini API access (user already has account, same ecosystem).

**Cost:** GCP free tier generous, Cloud Run serverless fits low-traffic MVP, pay-per-use scaling.

**Simplicity:** Fewer services to learn than AWS, better free tier for small projects than Azure.

**Not Locked In:** Can migrate if costs or needs change, but GCP optimal for MVP phase.

### Why Manual-First Operations
**Validation Logic:** Prove readers want content before investing in automation infrastructure.

**Cost Discipline:** Manual operations for initial volume (5+ national, 5+ local daily) keeps burn rate under $500/month.

**Learning:** Manual process reveals what should be automated (vs. building automation that wasn't needed).

**Scale Trigger:** When manual workflow becomes unsustainable bottleneck AND reader demand validated AND ROI proven, then automate.

### Why P1: Auto Social + Faceless Vlogs
**Auto Social (Facebook, X.com):**
- Amplification: Organic reach on social platforms drives reader acquisition (free distribution)
- Manual posting acceptable initially but time sink as volume scales
- Automation justifiable when posting time exceeds content creation time

**Faceless Vlogs (Instagram/TikTok):**
- Format: caitlinjohnstone.com style - text overlaid on imagery, narrated
- Platform: Short-form video dominates TikTok/Instagram, younger workers concentrated there
- Cost-Effective: Text-to-video with Gemini imagery, no video production team needed
- Reach: Different audience demographic than web readers

**P1 Trigger:** MVP validated with engaged web readers, ready to expand distribution channels. Each feature requires ROI demonstration before build.

### Why P2: Native Apps Deferred
**Web-First Sufficient:**
- Responsive web works on all devices (mobile-friendly design)
- No app store approval delays or fees
- Update instantly without app store review
- One codebase vs. three (web, iOS, Android)

**Cost Reality:**
- Native apps: $5K+ development each OR ongoing maintenance burden
- Web optimization costs fraction of native development
- Can add PWA features for app-like experience at lower cost

**Deferral Criteria:**
- Web platform proven successful with readers
- Evidence responsive web insufficient (reader feedback, retention data)
- Revenue model validated to fund app development
- Business analyst confirms ROI positive

**Decision Authority:** Business analyst determines timing, not arbitrary timeline.

---

## Strategic Priorities

### Content Strategy
- **National News:** 5+ stories
- **Local News:** 5+ stories per state/region
- **Local Delivery:** User preference-based, IP-based state inference, national default fallback
- **Article Quality:** Accurate, accessible (8th-grade level), working-class perspective

### Front Page Organization
- **NEW stories:** Chronological, newest-first
- **CONTINUING stories:** Visual prominence for ongoing issues
- Dual display ensures ongoing worker struggles remain visible

### Technical Stack
- **Cloud Platform:** Google Cloud Platform (GCP)
- **Opinion Imagery:** Google Gemini (user's API)
- **Development:** Agent-driven, <$5K budget
- **Operations:** <$500/month initially

### Cost Discipline
- Challenge every external API cost
- Leverage free tiers aggressively
- User has paid LLM subscriptions (marginal cost = $0)
- Simple, pragmatic security (not enterprise-grade)

---

## Prioritization Framework

### P0: Launch Prerequisites
**Goal:** Working prototype with satisfactory utility

**Must Have:**
1. Web portal (responsive, mobile-friendly)
2. Front page: NEW + CONTINUING story display
3. National (5+) + Local (5+) news split
4. Local selection by user preference/IP inference
5. Article display (accurate, worker-centric, accessible)
6. Social sharing buttons
7. Basic legal compliance (Terms, Privacy Policy)
8. GCP deployment
9. Gemini opinion imagery integration

**Quality Bar for Soft Launch:**
- Satisfactory utility to readers
- UX bugs fixed
- Article quality meets standards (accuracy, accessibility, worker perspective)

**Explicitly Deferred from P0:**
- Complex AI automation
- Automated content discovery
- Advanced analytics
- Performance optimization beyond "good enough"
- Mobile apps

---

### P1: Post-Launch Amplification
**Trigger:** MVP validated with engaged readers

**Features:**
1. **Auto Social Posting:**
   - Facebook automation
   - X.com (Twitter) automation
   - Scheduling and distribution optimization

2. **Faceless Vlogs:**
   - Instagram/TikTok content generation
   - Style: caitlinjohnstone.com approach
   - Text-to-video with imagery
   - Platform-optimized formatting

**Cost Justification Required:** Each P1 feature must demonstrate ROI before implementation

---

### P2: Native Apps
**Trigger:** Business analyst determines timing based on:
- Proven web platform success
- Reader demand evidence
- Revenue model validated
- Resource availability

**Scope:**
- iOS application
- Android application

**Deferred until:** P1 complete and business case proven

---

## Success Definition

Launch occurs when prototype achieves quality bar:

**Utility Satisfaction:**
- Readers find content valuable (qualitative feedback: "this is useful")
- Working-class perspective resonates (readers share with others)
- Local + National mix serves needs (readers check both sections)

**UX Quality:**
- Fast, responsive, mobile-friendly (loads quickly on phones, usable interface)
- NEW + CONTINUING display works intuitively (readers understand dual organization)
- Local selection functions correctly (preference saves, IP inference works)
- No blocking bugs (site navigable, articles readable, sharing works)

**Article Standards:**
- Accurate and factual (sources cited, fact-checkable)
- 8th-grade reading level (Flesch-Kincaid 7.5-8.5)
- Worker-centric perspective (not corporate framing)
- Doesn't pull punches (honest language about labor issues)

**NOT success criteria:**
- Traffic volume (vanity metric)
- Growth rate (irrelevant pre-validation)
- Engagement metrics (premature optimization)
- MAU/DAU numbers (focus on utility first)

**P1 Validation Trigger:**
"Engaged readers" means:
- Evidence of organic sharing (readers forwarding links)
- Return visitors (people coming back)
- Qualitative feedback requesting more content
- Sustainable manual operations validated

Launch when quality bar met, not timeline-driven.

---

## Technical Implementation

### Infrastructure
- **Platform:** GCP (free tier → paid as needed)
- **Hosting:** Static site OR simple server-rendered
- **Database:** Free tier (Firestore/Cloud SQL) OR serverless
- **CDN:** GCP Cloud CDN
- **Cost Target:** <$500/month operations

### Content Management
- Manual editorial workflow acceptable
- Simple CMS OR markdown + Git
- Gemini API for opinion imagery
- Human quality control required

### Local News Handling
**User Preference:**
- Explicit state/region selection
- Stored in browser localStorage OR user account (if implemented)

**IP-Based Inference:**
- GeoIP lookup for state detection
- Fallback to national if inference fails

**Default:**
- National news if no preference/location detected

### Front Page Display
**NEW Stories Section:**
- Chronological display, newest first
- Standard article cards
- Publication timestamp visible

**CONTINUING Stories Section:**
- Visual prominence (larger cards, highlighted, OR separate section)
- Ongoing issue tracking
- Updated timestamp visible
- Clear indication of "continuing coverage"

---

## Cost Philosophy

**Development Budget: <$5,000**
- Agent-driven development (leverage existing LLM subscriptions)
- Marginal cost approach: use tools already paid for
- Sweat equity prioritized over cash expenditure

**Why <$5K:** Bootstrapped sustainability. Prove concept before significant capital investment. Keeps project viable if validation fails.

**Operations Budget: <$500/month**
- GCP free tier maximized (generous for low-traffic MVP)
- Gemini API: user's existing account (marginal cost = $0)
- No paid external APIs until justified (manual curation sufficient initially)
- Simple infrastructure over complex (static site OR lightweight server)

**Why <$500/month:** Can run indefinitely without revenue pressure. Validates cost discipline before scaling. Prevents burn rate crisis.

**Scale Only When Justified:**
- Reader demand drives infrastructure spend (not projected capacity)
- Revenue model proven before P1/P2 investment (no speculation)
- Manual operations acceptable until proven bottleneck (validate need first)
- Every dollar challenged: "What reader value does this create?"

**Cost Escalation Gates:**
- P0 → P1: Engaged readers validated, manual workflow hitting limits, ROI demonstrable
- P1 → P2: Revenue covering costs, reader demand for native apps proven, business case positive
- Any paid service: Free tier exhausted AND specific reader value identified

---

## Risk Mitigation

**Top Risks:**
1. Building too much before validation
2. Cost creep beyond $500/month
3. Article quality below standards
4. Local news sourcing difficulty
5. Security neglect

**Mitigations:**
1. Stick to P0 scope, resist feature creep
2. Monitor costs weekly, challenge every expense
3. Human editorial quality control
4. Start with fewer states, expand gradually
5. HTTPS, basic auth, standard security practices from day one

---

## Strategic Advantages

**Differentiation:**
- Worker-centric perspective (not corporate media)
- Doesn't pull punches (honest framing)
- Local + National split (relevant to daily lives)
- CONTINUING stories prominence (ongoing issues don't disappear)

**Competitive Edge:**
- Low cost base (sustainable indefinitely)
- Agent-driven development (fast iteration)
- Lean operations (no burn rate pressure)
- Quality focus (not growth-at-all-costs)

**Sustainable Model:**
- Prove utility before scaling spend
- Manual operations validate automation need
- Reader-driven growth (organic)
- Cost discipline as core competency

---

## Business Model Context

**Revenue Strategy:** Deferred to post-validation phase.

**Why Defer Monetization:**
- P0 goal: Prove utility to readers, not maximize revenue
- Early monetization (ads, paywall) may compromise worker-centric mission
- Need reader trust before asking for money
- Sustainable at <$500/month without revenue pressure

**Future Revenue Options (Post-Validation):**
- Reader donations/patronage (aligned with mission)
- Union/labor organization sponsorships
- Ethical advertising (worker-friendly businesses)
- Premium features (if reader demand warrants)

**Decision Point:** Explore monetization when:
- Reader base validated (engaged, returning readers)
- Operating costs exceed $500/month sustainability threshold
- Growth requires funding (e.g., hiring writers, expanding coverage)
- Revenue approach doesn't compromise editorial independence

**Not This Project's Focus:** Building for venture scale. This is bootstrapped, mission-driven journalism proving utility first.

---

## Next Steps

1. Stakeholder approval of VERSION 1 priorities
2. GCP project setup
3. Gemini API integration planning
4. Infrastructure architecture (static vs. server-rendered decision)
5. Local news sourcing strategy (which states to launch with)
6. Front page UI design (NEW + CONTINUING display approach)
7. Content management workflow design
8. Build working prototype
9. Quality validation
10. Soft launch

---

**Prepared By:** Business Analysis Agent
**Frameworks:** Porter's Value Chain, VRIO, SWOT, Jobs To Be Done, Kano Model
**Philosophy:** Lean execution, prove before scale, quality over speed

---

**End of Document**
