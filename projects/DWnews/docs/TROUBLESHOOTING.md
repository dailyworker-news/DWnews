# DWnews Troubleshooting Guide

**Automated Journalism Pipeline - Problem Resolution**

Version 1.0 | Last Updated: 2026-01-01

---

## Table of Contents

1. [Common Errors](#common-errors)
2. [Agent-Specific Issues](#agent-specific-issues)
3. [Database Issues](#database-issues)
4. [API Connection Problems](#api-connection-problems)
5. [Performance Issues](#performance-issues)
6. [Quality Gate Failures](#quality-gate-failures)
7. [Diagnostic Tools](#diagnostic-tools)

---

## Common Errors

### Error: "Database is locked"

**Symptom:**
```
sqlite3.OperationalError: database is locked
```

**Cause:** Multiple processes trying to write to SQLite database simultaneously

**Solution:**
1. Check for multiple agent instances:
   ```bash
   ps aux | grep "backend.agents"
   ```

2. Kill duplicate processes:
   ```bash
   kill -TERM <pid>
   ```

3. If problem persists, wait 30 seconds and retry

4. **Long-term fix:** Consider PostgreSQL for production:
   ```python
   # In backend/config.py
   DATABASE_URL = "postgresql://user:pass@localhost/dwnews"
   ```

---

### Error: "API rate limit exceeded"

**Symptom:**
```
APIError: Rate limit exceeded. Please try again in 60 seconds.
```

**Cause:** Too many API requests to external service (Twitter, OpenAI, etc.)

**Solution:**

1. **Immediate:** Wait for rate limit reset (check error message for time)

2. **Check rate limit status:**
   ```python
   from backend.agents.utils.api_rate_limiter import RateLimiter
   limiter = RateLimiter()
   print(limiter.get_status())
   ```

3. **Temporary workaround:** Reduce batch size:
   ```python
   # In agent configuration
   MAX_BATCH_SIZE = 10  # Reduce from default 50
   ```

4. **Long-term fix:** Implement exponential backoff:
   ```python
   import time
   for retry in range(5):
       try:
           result = api_call()
           break
       except RateLimitError:
           wait_time = 2 ** retry  # 1, 2, 4, 8, 16 seconds
           time.sleep(wait_time)
   ```

---

### Error: "No module named 'backend'"

**Symptom:**
```
ModuleNotFoundError: No module named 'backend'
```

**Cause:** Python path not set correctly

**Solution:**

1. **Check current directory:**
   ```bash
   pwd  # Should be /path/to/DWnews
   ```

2. **Run from project root:**
   ```bash
   cd /path/to/DWnews
   python3 -m backend.agents.<agent_name>
   ```

3. **Or set PYTHONPATH:**
   ```bash
   export PYTHONPATH=/path/to/DWnews:$PYTHONPATH
   python3 backend/agents/<agent_name>.py
   ```

---

### Error: "Connection refused" (Database)

**Symptom:**
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) unable to open database file
```

**Cause:** Database file doesn't exist or wrong path

**Solution:**

1. **Check database path:**
   ```bash
   ls -la dwnews.db
   ```

2. **Create database if missing:**
   ```bash
   python3 database/init_db.py
   ```

3. **Verify database URL in config:**
   ```python
   # backend/config.py
   database_url = "sqlite:///./dwnews.db"  # Relative path
   # OR
   database_url = "sqlite:////absolute/path/to/dwnews.db"
   ```

---

### Error: "Article generation failed - LLM timeout"

**Symptom:**
```
TimeoutError: LLM request timed out after 60 seconds
```

**Cause:** LLM API slow or unresponsive

**Solution:**

1. **Increase timeout:**
   ```python
   # In backend/agents/enhanced_journalist_agent.py
   LLM_TIMEOUT = 120  # Increase from 60 to 120 seconds
   ```

2. **Check LLM API status:**
   ```bash
   curl -I https://api.openai.com/v1/models
   ```

3. **Retry with exponential backoff:**
   ```python
   for attempt in range(3):
       try:
           article = agent.generate_article(topic_id)
           break
       except TimeoutError:
           if attempt < 2:
               time.sleep(5 * (attempt + 1))
           else:
               raise
   ```

---

## Agent-Specific Issues

### Signal Intake Agent

**Issue: Low event count (<20 events/day)**

**Diagnostics:**
```bash
python3 -m backend.agents.signal_intake_agent --debug
tail -100 logs/signal_intake.log | grep "discovered"
```

**Common causes:**
1. **RSS feeds down:**
   - Check feed URLs manually
   - Verify feed parser working
   - Review `logs/signal_intake.log` for HTTP errors

2. **Twitter API credentials expired:**
   - Verify API keys in `.env` file
   - Test credentials: `python3 scripts/test_api_connections.py`
   - Renew keys at developer.twitter.com

3. **Reddit API rate limits:**
   - Check Reddit API dashboard
   - Reduce request frequency
   - Add delays between requests

**Solution:**
```python
# Test each feed source individually
from backend.agents.feeds.rss_feeds import RSSFeedAggregator
from backend.agents.feeds.twitter_feed import TwitterFeedMonitor

rss = RSSFeedAggregator()
print(f"RSS events: {len(rss.fetch_latest())}")

twitter = TwitterFeedMonitor()
print(f"Twitter events: {len(twitter.fetch_latest())}")
```

---

### Evaluation Agent

**Issue: Approval rate too high/low**

**Diagnostics:**
```sql
SELECT
    AVG(final_newsworthiness_score) as avg_score,
    COUNT(*) as total,
    SUM(CASE WHEN status='approved' THEN 1 ELSE 0 END) as approved
FROM event_candidates
WHERE evaluated_at >= DATE('now', '-7 days');
```

**If approval rate >20%:**
- Scores too lenient
- Increase `MIN_APPROVAL_SCORE` threshold:
  ```python
  # In backend/agents/evaluation_agent.py
  MIN_APPROVAL_SCORE = 70.0  # Increase from 65.0
  ```

**If approval rate <10%:**
- Scores too strict
- Review scoring weights:
  ```python
  WEIGHTS = {
      'worker_impact': 0.35,      # Increase from 0.30
      'timeliness': 0.20,
      'verifiability': 0.15,      # Decrease from 0.20
      'regional_relevance': 0.15,
      'conflict': 0.10,
      'novelty': 0.05
  }
  ```

---

### Verification Agent

**Issue: Many topics failing verification**

**Diagnostics:**
```sql
SELECT
    verification_status,
    COUNT(*) as count
FROM topics
WHERE discovery_date >= DATE('now', '-7 days')
GROUP BY verification_status;
```

**Common causes:**
1. **Web search API down:**
   ```bash
   python3 scripts/test_api_connections.py --test-search
   ```

2. **Source threshold too high:**
   ```python
   # Temporarily lower threshold
   MIN_CREDIBLE_SOURCES = 2  # Reduce from 3
   ```

3. **Source identification failing:**
   - Check source database has entries
   - Verify source URLs are accessible
   - Review source credibility scores

**Solution:**
```python
# Test verification for specific topic
from backend.agents.verification_agent import VerificationAgent
from backend.database import SessionLocal

session = SessionLocal()
agent = VerificationAgent(session)
result = agent.verify_topic(topic_id=123)
print(result)
```

---

### Enhanced Journalist Agent

**Issue: Articles failing self-audit**

**Diagnostics:**
```sql
SELECT
    COUNT(*) as total_articles,
    SUM(CASE WHEN self_audit_passed=1 THEN 1 ELSE 0 END) as passed
FROM articles
WHERE created_at >= DATE('now', '-7 days');
```

**Review failed audits:**
```python
from backend.database import SessionLocal
from database.models import Article

session = SessionLocal()
failed = session.query(Article).filter_by(self_audit_passed=False).all()

for article in failed:
    print(f"Article {article.id}: {article.title}")
    # Review audit report (if stored)
```

**Common failures:**
1. **Source attribution missing:**
   - Verify `source_plan` in topic
   - Check attribution engine logic
   - Review article body for citations

2. **Reading level too high/low:**
   ```python
   # Adjust generation prompt
   READING_LEVEL_TARGET = "8th grade"  # Make more explicit
   ```

3. **Bias detected:**
   - Review bias scan parameters
   - Adjust language model temperature
   - Add more balanced source requirements

---

### Editorial Coordinator Agent

**Issue: Emails not sending**

**Diagnostics:**
```bash
tail -50 logs/editorial.log | grep -i "email"
```

**Common causes:**
1. **SMTP not configured:**
   ```python
   # Check .env file
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

2. **Test email manually:**
   ```python
   from backend.agents.email_notifications import send_assignment_email
   send_assignment_email(
       editor_email="test@example.com",
       article_id=123,
       article_title="Test Article"
   )
   ```

**Issue: Articles stuck in review**

**Diagnostics:**
```sql
SELECT
    id,
    title,
    assigned_editor,
    review_deadline,
    status
FROM articles
WHERE status='under_review'
    AND review_deadline < datetime('now')
ORDER BY review_deadline;
```

**Solution:**
- Send reminder emails to editors
- Escalate overdue articles to senior editor
- Reassign if editor unavailable

---

### Publication Agent

**Issue: Approved articles not publishing**

**Diagnostics:**
```sql
SELECT COUNT(*) FROM articles WHERE status='approved';
```

**Check publication logs:**
```bash
tail -50 logs/publication.log | grep ERROR
```

**Common causes:**
1. **Database transaction failing:**
   - Check database locks
   - Verify disk space
   - Review error logs

2. **Web server API unavailable:**
   - Test API endpoint manually
   - Check server status
   - Verify authentication tokens

---

### Monitoring Agent

**Issue: Not detecting corrections**

**Diagnostics:**
```bash
tail -100 logs/monitoring.log | grep "correction"
```

**Common causes:**
1. **Social media API access issues:**
   - Verify Twitter API credentials
   - Check Reddit API status
   - Test API connections

2. **Cross-reference logic too strict:**
   - Review threshold settings
   - Check source reliability scores
   - Adjust confidence requirements

---

## Database Issues

### Slow Queries

**Symptom:** Agents taking much longer than expected

**Diagnose:**
```sql
EXPLAIN QUERY PLAN
SELECT * FROM event_candidates WHERE status='discovered';
```

**Solutions:**

1. **Add missing indexes:**
   ```sql
   CREATE INDEX idx_events_status ON event_candidates(status);
   CREATE INDEX idx_articles_status ON articles(status);
   CREATE INDEX idx_topics_verification ON topics(verification_status);
   ```

2. **Vacuum database:**
   ```bash
   sqlite3 dwnews.db "VACUUM;"
   ```

3. **Analyze query patterns:**
   ```sql
   ANALYZE;
   ```

---

### Database Growing Too Large

**Check database size:**
```bash
du -h dwnews.db
```

**Clean up old data:**
```sql
-- Archive old events (>90 days)
DELETE FROM event_candidates
WHERE discovery_date < DATE('now', '-90 days')
    AND status IN ('rejected', 'converted');

-- Archive old articles (>1 year)
UPDATE articles
SET status='archived'
WHERE published_at < DATE('now', '-365 days')
    AND status='published';

-- Vacuum to reclaim space
VACUUM;
```

---

### Data Integrity Issues

**Check for orphaned records:**
```sql
-- Topics without categories
SELECT COUNT(*) FROM topics WHERE category_id IS NULL;

-- Articles without categories
SELECT COUNT(*) FROM articles WHERE category_id IS NULL;

-- Corrections without articles
SELECT COUNT(*) FROM corrections c
LEFT JOIN articles a ON c.article_id = a.id
WHERE a.id IS NULL;
```

**Fix orphaned records:**
```sql
-- Assign default category
UPDATE topics SET category_id=1 WHERE category_id IS NULL;
UPDATE articles SET category_id=1 WHERE category_id IS NULL;

-- Delete orphaned corrections
DELETE FROM corrections
WHERE article_id NOT IN (SELECT id FROM articles);
```

---

## API Connection Problems

### Test All API Connections

```bash
python3 scripts/test_api_connections.py
```

**Expected output:**
```
✓ Database: Connected
✓ Twitter API: Connected
✓ Reddit API: Connected
✓ OpenAI API: Connected
✓ Web Search API: Connected
```

---

### Twitter API Issues

**Error: "Invalid or expired token"**

**Solution:**
1. Regenerate API keys at developer.twitter.com
2. Update `.env` file:
   ```env
   TWITTER_API_KEY=your_new_key
   TWITTER_API_SECRET=your_new_secret
   TWITTER_BEARER_TOKEN=your_new_bearer_token
   ```
3. Restart agents

---

### OpenAI API Issues

**Error: "You exceeded your current quota"**

**Check usage:**
```bash
curl https://api.openai.com/v1/usage \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Solutions:**
1. **Increase API quota** (upgrade plan)
2. **Reduce article generation count:**
   ```python
   MAX_DAILY_ARTICLES = 5  # Reduce from 10
   ```
3. **Switch to cheaper model:**
   ```python
   MODEL = "gpt-3.5-turbo"  # Instead of gpt-4
   ```

---

## Performance Issues

### Agent Running Slowly

**Profile agent execution:**
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Run agent
agent.discover_events()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 slowest functions
```

**Common bottlenecks:**
1. **Network requests:** Add caching, batch requests
2. **Database queries:** Add indexes, optimize queries
3. **LLM calls:** Reduce prompt size, use faster model
4. **File I/O:** Use in-memory processing where possible

---

### High Memory Usage

**Monitor memory:**
```bash
ps aux | grep python | awk '{print $2, $6/1024 "MB", $11}'
```

**Common causes:**
1. **Large result sets:** Use pagination
   ```python
   for offset in range(0, total, BATCH_SIZE):
       batch = session.query(Model).limit(BATCH_SIZE).offset(offset).all()
       process_batch(batch)
   ```

2. **Memory leaks:** Close database sessions
   ```python
   try:
       session = SessionLocal()
       # ... do work ...
   finally:
       session.close()
   ```

3. **Large LLM responses:** Limit output tokens
   ```python
   max_tokens=1500  # Limit response size
   ```

---

## Quality Gate Failures

### Debug Quality Gate Failures

```bash
python3 scripts/verify_quality_gates.py --verbose
```

**Review failures by gate:**

1. **Newsworthiness failures:**
   ```sql
   SELECT id, title, final_newsworthiness_score
   FROM event_candidates
   WHERE status='approved' AND final_newsworthiness_score < 65;
   ```

2. **Source verification failures:**
   ```sql
   SELECT id, title, source_count, academic_citation_count
   FROM topics
   WHERE verification_status='verified'
       AND source_count < 3
       AND academic_citation_count < 2;
   ```

3. **Self-audit failures:**
   ```sql
   SELECT id, title
   FROM articles
   WHERE self_audit_passed=0;
   ```

4. **Bias scan failures:**
   ```sql
   SELECT id, title, bias_scan_report
   FROM articles
   WHERE bias_scan_report NOT LIKE '%"overall_score": "PASS"%';
   ```

5. **Reading level failures:**
   ```sql
   SELECT id, title, reading_level
   FROM articles
   WHERE reading_level < 7.5 OR reading_level > 8.5;
   ```

---

## Diagnostic Tools

### Health Check Script

Create `scripts/health_check.sh`:

```bash
#!/bin/bash

echo "=== DWnews System Health Check ==="
echo ""

# Check database
echo "Database:"
if [ -f "dwnews.db" ]; then
    echo "  ✓ Database file exists"
    echo "  Size: $(du -h dwnews.db | cut -f1)"
else
    echo "  ✗ Database file missing!"
fi

# Check agents
echo ""
echo "Running Agents:"
ps aux | grep "backend.agents" | grep -v grep | wc -l | xargs echo "  Count:"

# Check logs
echo ""
echo "Recent Errors:"
grep -i error logs/*.log 2>/dev/null | tail -5

# Check API credentials
echo ""
echo "API Configuration:"
[ -f ".env" ] && echo "  ✓ .env file exists" || echo "  ✗ .env file missing!"

# Check disk space
echo ""
echo "Disk Space:"
df -h . | tail -1 | awk '{print "  Available:", $4}'

echo ""
echo "=== Health Check Complete ==="
```

Usage:
```bash
chmod +x scripts/health_check.sh
./scripts/health_check.sh
```

---

### Log Analysis

**Find most common errors:**
```bash
grep ERROR logs/*.log | sed 's/.*ERROR - //' | sort | uniq -c | sort -rn | head -10
```

**Find slow operations:**
```bash
grep "took.*seconds" logs/*.log | awk '{print $NF}' | sort -rn | head -10
```

**Find failed API calls:**
```bash
grep -i "api.*failed\|timeout\|connection refused" logs/*.log | tail -20
```

---

### Database Inspection

**Interactive SQL session:**
```bash
sqlite3 dwnews.db
```

**Useful queries:**
```sql
-- Recent activity
SELECT 'Events', COUNT(*) FROM event_candidates WHERE discovery_date >= DATE('now', '-1 day')
UNION ALL
SELECT 'Articles', COUNT(*) FROM articles WHERE created_at >= DATE('now', '-1 day')
UNION ALL
SELECT 'Published', COUNT(*) FROM articles WHERE published_at >= DATE('now', '-1 day');

-- Pipeline status
SELECT status, COUNT(*) FROM event_candidates GROUP BY status;
SELECT status, COUNT(*) FROM articles GROUP BY status;

-- Quality metrics
SELECT
    AVG(final_newsworthiness_score) as avg_newsworthiness,
    AVG(reading_level) as avg_reading_level,
    SUM(self_audit_passed) * 100.0 / COUNT(*) as audit_pass_rate
FROM articles
WHERE created_at >= DATE('now', '-7 days');
```

---

## Getting Help

If you've tried all troubleshooting steps and the issue persists:

1. **Collect diagnostics:**
   ```bash
   ./scripts/health_check.sh > diagnostics.txt
   grep ERROR logs/*.log > error_logs.txt
   ```

2. **Create detailed bug report:**
   - What you were trying to do
   - What happened instead
   - Error messages (full stack trace)
   - Steps to reproduce
   - System information (OS, Python version, etc.)

3. **Contact support:**
   - Technical issues: `sysadmin@dailyworker.news`
   - Editorial issues: `senior-editor@dailyworker.news`
   - Emergency: [PHONE_NUMBER]

4. **Include in report:**
   - diagnostics.txt
   - error_logs.txt
   - Relevant configuration files (redact secrets!)
   - Screenshots if applicable

---

**Document Revision History:**
- v1.0 (2026-01-01): Initial version - Batch 6 completion
