# DWnews Operational Procedures

**Automated Journalism Pipeline - Operations Manual**

Version 1.0 | Last Updated: 2026-01-01

---

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Agent Management](#agent-management)
3. [Manual Overrides](#manual-overrides)
4. [Quality Monitoring](#quality-monitoring)
5. [Performance Metrics](#performance-metrics)
6. [Escalation Procedures](#escalation-procedures)
7. [Emergency Procedures](#emergency-procedures)

---

## Daily Operations

### Automated Daily Workflow

The DWnews automated journalism pipeline runs on the following schedule:

```
06:00 AM - Signal Intake Agent discovers events
08:00 AM - Evaluation Agent scores events
09:00 AM - Verification Agent verifies approved events
10:00 AM - Journalist Agent drafts articles
12:00 PM - Editorial Coordinator assigns to editors
02:00 PM - Human editors review and approve articles
05:00 PM - Publication Agent publishes approved articles
Ongoing  - Monitoring Agent tracks published articles (7-day window)
```

### Running Agents Manually

#### 1. Signal Intake Agent

Discover newsworthy labor events from multiple sources:

```bash
cd /path/to/DWnews
python3 -m backend.agents.signal_intake_agent
```

**Expected output:** 20-50 events discovered daily
**Runtime:** 5-10 minutes
**Dependencies:** Internet connection, API credentials

#### 2. Evaluation Agent

Score discovered events on newsworthiness:

```bash
python3 -m backend.agents.evaluation_agent
```

**Expected output:** 10-20% of events approved (≥65/100 score)
**Runtime:** 2-5 minutes
**Dependencies:** Database with discovered events

#### 3. Verification Agent

Verify sources for approved events:

```bash
python3 -m backend.agents.verification_agent
```

**Expected output:** ≥3 credible sources per topic
**Runtime:** 10-15 minutes
**Dependencies:** Web search API access

#### 4. Enhanced Journalist Agent

Generate article drafts from verified topics:

```bash
python3 -m backend.agents.enhanced_journalist_agent
```

**Expected output:** 2-10 articles daily
**Runtime:** 15-30 minutes
**Dependencies:** LLM API access

#### 5. Editorial Coordinator Agent

Assign articles to human editors:

```bash
python3 -m backend.agents.editorial_coordinator_agent
```

**Expected output:** All draft articles assigned
**Runtime:** < 1 minute
**Dependencies:** Email service configured

#### 6. Publication Agent

Publish editor-approved articles:

```bash
python3 -m backend.agents.publication_agent
```

**Expected output:** 2-8 articles published daily
**Runtime:** < 1 minute
**Dependencies:** Web server access

#### 7. Monitoring Agent

Track published articles for corrections:

```bash
python3 -m backend.agents.monitoring_agent
```

**Expected output:** Monitoring logs for 7-day window
**Runtime:** 5-10 minutes
**Dependencies:** Social media API access

### Cron Job Setup

To run the pipeline automatically, add to crontab:

```cron
# DWnews Automated Journalism Pipeline
0 6 * * * cd /path/to/DWnews && python3 -m backend.agents.signal_intake_agent >> logs/signal_intake.log 2>&1
0 8 * * * cd /path/to/DWnews && python3 -m backend.agents.evaluation_agent >> logs/evaluation.log 2>&1
0 9 * * * cd /path/to/DWnews && python3 -m backend.agents.verification_agent >> logs/verification.log 2>&1
0 10 * * * cd /path/to/DWnews && python3 -m backend.agents.enhanced_journalist_agent >> logs/journalist.log 2>&1
0 12 * * * cd /path/to/DWnews && python3 -m backend.agents.editorial_coordinator_agent >> logs/editorial.log 2>&1
0 17 * * * cd /path/to/DWnews && python3 -m backend.agents.publication_agent >> logs/publication.log 2>&1
0 */6 * * * cd /path/to/DWnews && python3 -m backend.agents.monitoring_agent >> logs/monitoring.log 2>&1
```

### Monitoring Dashboard Access

Access the real-time monitoring dashboard:

```bash
cd /path/to/DWnews
python3 backend/api/main.py  # Start API server
```

Then navigate to: `http://localhost:8000/admin/dashboard`

**Dashboard features:**
- Real-time pipeline status
- Quality gate metrics
- Article approval queue
- Error logs and alerts
- Performance analytics

---

## Agent Management

### Starting/Stopping Individual Agents

**Start an agent:**
```bash
python3 -m backend.agents.<agent_name>
```

**Stop an agent:**
- Ctrl+C (for manual runs)
- `kill -TERM <pid>` (for background processes)

**Check agent status:**
```bash
ps aux | grep python | grep agents
```

### Agent Health Checks

Each agent logs to `/logs/<agent_name>.log`. Monitor for errors:

```bash
tail -f logs/signal_intake.log
tail -f logs/evaluation.log
tail -f logs/verification.log
tail -f logs/journalist.log
tail -f logs/editorial.log
tail -f logs/publication.log
tail -f logs/monitoring.log
```

**Healthy indicators:**
- Regular log entries
- No ERROR level messages
- Expected throughput numbers
- Database transactions completing

**Unhealthy indicators:**
- No log activity for >30 minutes
- Repeated ERROR messages
- Database connection failures
- API rate limit errors

### Restarting Agents

If an agent fails or hangs:

1. **Identify the agent process:**
   ```bash
   ps aux | grep <agent_name>
   ```

2. **Kill the process gracefully:**
   ```bash
   kill -TERM <pid>
   ```

3. **Wait 10 seconds, then force kill if needed:**
   ```bash
   kill -KILL <pid>
   ```

4. **Restart the agent:**
   ```bash
   python3 -m backend.agents.<agent_name>
   ```

5. **Verify restart:**
   ```bash
   tail -f logs/<agent_name>.log
   ```

---

## Manual Overrides

### Manually Approve/Reject Events

To override the Evaluation Agent's scoring:

```python
from backend.database import SessionLocal
from database.models import EventCandidate

session = SessionLocal()

# Approve an event manually
event = session.query(EventCandidate).get(EVENT_ID)
event.status = 'approved'
event.final_newsworthiness_score = 70.0  # Override score
session.commit()

# Reject an event manually
event = session.query(EventCandidate).get(EVENT_ID)
event.status = 'rejected'
event.rejection_reason = 'Manual override: Not relevant to labor focus'
session.commit()
```

### Manually Publish Articles

**CAUTION:** This bypasses editorial approval. Use only in emergencies.

```python
from backend.database import SessionLocal
from database.models import Article
from datetime import datetime

session = SessionLocal()

# Force-publish an article
article = session.query(Article).get(ARTICLE_ID)
article.status = 'published'
article.published_at = datetime.now()
article.editorial_notes = 'EMERGENCY PUBLICATION - Manual override by [YOUR_NAME]'
session.commit()
```

**When to use:**
- Breaking news requiring immediate publication
- Editorial approval system failure
- Critical correction needed urgently

**Always document:**
- Reason for override
- Your name and timestamp
- Follow-up actions required

### Manually Flag Corrections

To manually flag an article for correction:

```python
from backend.database import SessionLocal
from database.models import Correction
from datetime import datetime

session = SessionLocal()

correction = Correction(
    article_id=ARTICLE_ID,
    correction_type='factual_error',  # or 'source_error', 'clarification', 'update', 'retraction'
    incorrect_text='The incorrect text here',
    correct_text='The corrected text here',
    section_affected='body',  # or 'headline', 'summary'
    severity='minor',  # or 'moderate', 'major', 'critical'
    description='Detailed explanation of what was wrong',
    reported_by='Editor Name',
    reported_at=datetime.now(),
    status='pending'
)
session.add(correction)
session.commit()
```

### Manual Article Assignment

To reassign an article to a different editor:

```python
from backend.database import SessionLocal
from database.models import Article
from backend.agents.editorial_coordinator_agent import EditorialCoordinator

session = SessionLocal()
coordinator = EditorialCoordinator(session)

# Reassign article
coordinator.assign_article(
    article_id=ARTICLE_ID,
    editor_email='new-editor@dailyworker.news'
)
```

---

## Quality Monitoring

### Daily Quality Checks

Run the quality gates verification script daily:

```bash
python3 scripts/verify_quality_gates.py --verbose
```

**Review checklist:**
- [ ] All approved events scored ≥65/100
- [ ] All verified topics have ≥3 sources OR ≥2 academic citations
- [ ] All articles passed self-audit
- [ ] All articles passed bias scan
- [ ] All articles have reading level 7.5-8.5
- [ ] All published articles had editorial approval

### Weekly Quality Review

Every Monday, review:

1. **Approval Rates:**
   ```sql
   SELECT
       COUNT(*) as total_events,
       SUM(CASE WHEN status='approved' THEN 1 ELSE 0 END) as approved,
       ROUND(SUM(CASE WHEN status='approved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as approval_rate
   FROM event_candidates
   WHERE discovery_date >= DATE('now', '-7 days');
   ```
   **Target:** 10-20% approval rate

2. **Publication Success Rate:**
   ```sql
   SELECT
       COUNT(*) as total_articles,
       SUM(CASE WHEN status='published' THEN 1 ELSE 0 END) as published,
       ROUND(SUM(CASE WHEN status='published' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as publication_rate
   FROM articles
   WHERE created_at >= DATE('now', '-7 days');
   ```
   **Target:** >80% publication rate

3. **Correction Rate:**
   ```sql
   SELECT
       COUNT(*) as total_corrections,
       SUM(CASE WHEN severity='critical' THEN 1 ELSE 0 END) as critical,
       SUM(CASE WHEN severity='major' THEN 1 ELSE 0 END) as major
   FROM corrections
   WHERE reported_at >= DATE('now', '-7 days');
   ```
   **Target:** <5% of published articles need corrections

### Source Reliability Trends

Monitor source credibility scores monthly:

```sql
SELECT
    s.name,
    s.credibility_score,
    COUNT(srl.id) as events,
    AVG(srl.reliability_delta) as avg_delta
FROM sources s
LEFT JOIN source_reliability_log srl ON s.id = srl.source_id
WHERE srl.logged_at >= DATE('now', '-30 days')
GROUP BY s.id
ORDER BY avg_delta DESC;
```

**Action items:**
- Sources with avg_delta < -0.5: Review and potentially remove
- Sources with credibility_score < 2: Disable immediately
- Sources with 0 events in 30 days: Review for relevance

---

## Performance Metrics

### Expected Daily Throughput

| Metric | Target | Acceptable Range |
|--------|--------|------------------|
| Events discovered | 20-50 | 15-60 |
| Events approved | 10-20% | 8-25% |
| Topics verified | 80-100% | 70-100% |
| Articles generated | 2-10 | 1-12 |
| Articles published | 2-8 | 1-10 |

### System Health Indicators

**Green (Healthy):**
- All agents running without errors
- Throughput within target ranges
- Quality gates passing >95%
- No critical corrections in past 7 days

**Yellow (Needs Attention):**
- 1-2 agents reporting errors
- Throughput 20% outside target range
- Quality gates passing 85-95%
- 1-2 major corrections in past 7 days

**Red (Critical):**
- 3+ agents failing
- Throughput >30% outside target range
- Quality gates passing <85%
- Any critical correction or 3+ major corrections in past 7 days

### Performance Optimization

If throughput is low:

1. **Check API rate limits:**
   ```bash
   grep "rate limit" logs/*.log
   ```

2. **Verify database performance:**
   ```sql
   EXPLAIN QUERY PLAN SELECT * FROM event_candidates WHERE status='discovered';
   ```

3. **Monitor resource usage:**
   ```bash
   top -p $(pgrep -f "backend.agents")
   ```

4. **Review agent logs for bottlenecks:**
   ```bash
   grep -i "slow\|timeout\|retry" logs/*.log
   ```

---

## Escalation Procedures

### When to Escalate to Senior Editor

Escalate article to senior editor when:

1. **Critical factual concerns:** Potential major factual error
2. **Legal risk:** Potential libel, defamation, or legal issues
3. **Sensitive topics:** Whistleblower protection, ongoing investigations
4. **Source conflicts:** Contradictory information from credible sources
5. **Ethical dilemmas:** Privacy concerns, vulnerable populations

**Escalation process:**

```python
from backend.database import SessionLocal
from database.models import Article

session = SessionLocal()
article = session.query(Article).get(ARTICLE_ID)
article.status = 'needs_senior_review'
article.editorial_notes += '\n\nESCALATED TO SENIOR EDITOR\nReason: [DETAILED REASON]\nEscalated by: [YOUR_NAME]\nDate: [DATE]'
session.commit()
```

Send email to: `senior-editor@dailyworker.news`

### When to Pause Automated Publishing

**Immediately pause if:**
- Critical error in published article requiring retraction
- System security breach detected
- Repeated quality gate failures (>3 in 24 hours)
- External API providing false information

**Pause procedure:**

1. **Stop Publication Agent:**
   ```bash
   kill -TERM $(pgrep -f publication_agent)
   ```

2. **Set maintenance flag:**
   ```python
   from backend.database import SessionLocal
   # Set system-wide maintenance mode
   # (implementation depends on your config system)
   ```

3. **Notify editorial team:**
   Send email to: `editors@dailyworker.news`

4. **Investigate and resolve issue**

5. **Resume after senior editor approval**

### When to Manually Intervene

**Immediate intervention required:**
- Article published with critical error
- Source reliability compromised
- Duplicate article published
- Article violates editorial guidelines

**Intervention protocol:**

1. **Assess severity (1-5 scale)**
2. **Document issue in detail**
3. **Take corrective action:**
   - Critical (5): Unpublish immediately, issue correction
   - Major (4): Flag for urgent correction
   - Moderate (3): Schedule correction within 24 hours
   - Minor (2): Add to correction queue
   - Trivial (1): Note for future reference

4. **Log intervention:**
   ```python
   # Log to intervention_log table
   # (or create incident report)
   ```

5. **Report to team in next daily standup**

---

## Emergency Procedures

### Emergency Article Retraction

If an article contains serious errors requiring retraction:

1. **Unpublish immediately:**
   ```python
   from backend.database import SessionLocal
   from database.models import Article
   from datetime import datetime

   session = SessionLocal()
   article = session.query(Article).get(ARTICLE_ID)
   article.status = 'archived'
   article.editorial_notes += f'\n\nRETRACTED: {datetime.now()}\nReason: [DETAILED REASON]'
   session.commit()
   ```

2. **Create retraction notice:**
   ```python
   from database.models import Correction

   correction = Correction(
       article_id=ARTICLE_ID,
       correction_type='retraction',
       severity='critical',
       description='Full article retracted due to [REASON]',
       incorrect_text='[Original article content]',
       correct_text='ARTICLE RETRACTED',
       reported_by='[YOUR_NAME]',
       corrected_by='[SENIOR_EDITOR_NAME]',
       status='published',
       is_published=True,
       public_notice='This article has been retracted due to significant factual errors...'
   )
   session.add(correction)
   session.commit()
   ```

3. **Notify stakeholders:**
   - Editorial team
   - Social media team (remove shares)
   - Newsletter team (if article was sent)
   - Legal team (if necessary)

4. **Post-mortem analysis:**
   - What went wrong?
   - Which quality gates failed?
   - What process changes are needed?

### System-Wide Failure

If multiple agents are failing:

1. **Stop all automated processes:**
   ```bash
   killall -TERM python3
   crontab -r  # Remove cron jobs temporarily
   ```

2. **Check system resources:**
   ```bash
   df -h          # Disk space
   free -m        # Memory
   top            # CPU usage
   ```

3. **Check database connectivity:**
   ```bash
   python3 -c "from backend.database import SessionLocal; SessionLocal()"
   ```

4. **Review error logs:**
   ```bash
   tail -100 logs/*.log | grep ERROR
   ```

5. **Contact system administrator**

6. **Switch to manual operations until resolved**

### Database Corruption

If database corruption is suspected:

1. **Stop all write operations**

2. **Create immediate backup:**
   ```bash
   sqlite3 dwnews.db ".backup dwnews_emergency_backup.db"
   ```

3. **Run integrity check:**
   ```bash
   sqlite3 dwnews.db "PRAGMA integrity_check;"
   ```

4. **If corruption confirmed:**
   - Restore from most recent clean backup
   - Replay transactions from logs if possible
   - Contact database administrator

5. **Document all actions taken**

---

## Support Contacts

**Editorial Team:**
- Senior Editor: `senior-editor@dailyworker.news`
- Editorial Coordinator: `editorial@dailyworker.news`

**Technical Team:**
- System Administrator: `sysadmin@dailyworker.news`
- Database Administrator: `dba@dailyworker.news`
- On-call Engineer: `oncall@dailyworker.news`

**Escalation Path:**
1. Editor → Senior Editor
2. Senior Editor → Editorial Director
3. Editorial Director → Publisher

**Emergency Hotline:** [PHONE_NUMBER]

---

## Appendix: Quick Reference

### Most Common Commands

```bash
# Check agent status
ps aux | grep "backend.agents"

# View recent logs
tail -50 logs/journalist.log

# Verify quality gates
python3 scripts/verify_quality_gates.py

# Run end-to-end test
python3 scripts/test_end_to_end_pipeline.py

# Check database status
sqlite3 dwnews.db "SELECT COUNT(*) FROM articles WHERE status='published';"

# Restart an agent
kill -TERM <pid> && python3 -m backend.agents.<agent_name>
```

### Status Codes Reference

**Event Statuses:** `discovered`, `evaluated`, `approved`, `rejected`, `converted`

**Article Statuses:** `draft`, `pending_review`, `under_review`, `revision_requested`, `approved`, `published`, `archived`, `needs_senior_review`

**Correction Statuses:** `pending`, `verified`, `corrected`, `published`

**Verification Statuses:** `pending`, `in_progress`, `verified`, `partial`, `failed`

---

**Document Revision History:**
- v1.0 (2026-01-01): Initial version - Batch 6 completion
