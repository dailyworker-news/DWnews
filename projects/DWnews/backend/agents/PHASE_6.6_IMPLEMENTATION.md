# Phase 6.6: Editorial Workflow Integration - Implementation Summary

**Status:** ✅ Complete
**Date:** 2026-01-01
**Test Results:** 8/8 tests passing

## Overview

Successfully implemented human editorial oversight into the automated journalism pipeline. The Editorial Coordinator Agent now manages the complete workflow from article assignment through review, revision, and final approval.

## Components Implemented

### 1. Editorial Coordinator Agent
**File:** `/backend/agents/editorial_coordinator_agent.py`

**Core Functions:**
- `assign_article()` - Assign articles to editors based on category and workload
- `set_review_deadline()` - Set SLA-based deadlines (24-72 hours based on category)
- `notify_editor()` - Send email notifications to assigned editors
- `process_revision_request()` - Handle editorial revision requests
- `approve_article()` - Approve articles for publication
- `reject_article()` - Reject articles
- `check_overdue_reviews()` - Track SLA compliance
- `send_overdue_alerts()` - Send overdue email alerts
- `get_editor_workload()` - Calculate editor assignments
- `auto_assign_pending_articles()` - Batch assign drafts to editors

**Editor Assignment Algorithm:**
1. Find editors who specialize in article category
2. Select editor with lowest current workload
3. Fallback to general editors if no specialist

**SLA Configuration:**
```python
SLA_DEADLINES = {
    "labor": 24,      # News articles: 24 hours
    "politics": 24,
    "housing": 48,    # Analysis: 48 hours
    "culture": 72,
    "default": 48
}
```

### 2. Email Notification System
**File:** `/backend/agents/email_notifications.py`

**Features:**
- Test mode (logs to console, default for development)
- SendGrid integration (production)
- SMTP fallback (optional)
- HTML email templates with styling

**Email Templates:**
1. **Article Assignment** - Sent when article assigned to editor
2. **Revision Complete** - Sent when AI journalist completes revision
3. **Overdue Alert** - Sent when review passes deadline

**Configuration:**
```bash
EMAIL_MODE=test                              # test, sendgrid, or smtp
SENDGRID_API_KEY=SG.xxxxx                   # For production
FROM_EMAIL=editorial@dailyworker.news
ADMIN_URL=http://localhost:3000/admin
```

### 3. Editorial API Routes
**File:** `/backend/routes/editorial.py`

**Endpoints:**
- `GET /api/editorial/pending` - List articles pending review
- `GET /api/editorial/review/{id}` - Get complete review data
- `POST /api/editorial/{id}/approve` - Approve article
- `POST /api/editorial/{id}/request-revision` - Request changes
- `POST /api/editorial/{id}/reject` - Reject article
- `GET /api/editorial/overdue` - List overdue reviews
- `GET /api/editorial/workload/{email}` - Get editor workload
- `POST /api/editorial/auto-assign` - Batch assign articles (scheduled job)
- `POST /api/editorial/send-overdue-alerts` - Send alerts (scheduled job)

**Review Data Includes:**
- Complete article content
- Self-audit checklist (10 items with pass/fail)
- Bias scan report (hallucination checks, propaganda flags)
- Verified sources list (with credibility scores)
- Revision history
- Editorial metadata (deadline, assigned editor, notes)

### 4. Admin Portal Enhancement
**Files:**
- `/frontend/admin/review-article.html` - Full review interface
- `/frontend/admin/admin.js` - Updated dashboard with review links

**Review Interface Features:**
- Full article display with formatting
- Self-audit checklist visualization (green/red indicators)
- Bias scan results display
- Sources list with credibility stars (1-5)
- Revision history timeline
- Editorial notes textarea
- Action buttons: Approve, Request Revision, Reject, Back

**Dashboard Integration:**
- Added "Review" button to article cards
- Maintains existing "Quick View" functionality
- Navigates to review-article.html?id={article_id}

### 5. Database Migration
**Files:**
- `/database/migrations/002_editorial_workflow_statuses.sql` - SQL migration
- `/database/migrations/run_migration_002.py` - Migration script

**Changes:**
- Updated article status constraint to include:
  - `under_review` - Assigned to editor
  - `revision_requested` - Editor requested changes
  - `needs_senior_review` - Max revisions reached
- Preserved all existing data
- Created database backup before migration

**Status Workflow:**
```
draft → under_review → revision_requested → draft → under_review → approved → published
                                    ↑______________|
                                    (revision loop)
```

### 6. Agent Definition
**File:** `/.claude/agents/editorial-coordinator.md`

Complete documentation including:
- API reference
- Configuration guide
- Email template examples
- Database schema
- Testing procedures
- Troubleshooting guide
- Usage examples

### 7. End-to-End Testing
**File:** `/scripts/test_editorial_workflow.py`

**Test Coverage:**
1. ✅ Auto-assignment - Article assigned to appropriate editor
2. ✅ Email notification - Notifications sent successfully
3. ✅ Revision request - Editorial notes logged, status updated
4. ✅ Max revisions - Third revision blocked, status = needs_senior_review
5. ✅ Article approval - Status changed to approved
6. ✅ Article rejection - Status changed to archived, reason saved
7. ✅ Overdue tracking - Overdue articles identified correctly
8. ✅ Workload calculation - Editor assignments calculated

**Test Results:**
```
Total: 8/8 tests passed
🎉 ALL TESTS PASSED!
```

## Workflow States

### Draft → Under Review
1. Article created with `status='draft'` and `self_audit_passed=True`
2. Editorial Coordinator auto-assigns to editor based on category
3. Status changed to `under_review`
4. Review deadline set (24-72 hours based on category)
5. Assignment email sent to editor

### Under Review → Revision Requested
1. Editor reviews article in admin portal
2. Editor fills editorial notes textarea with specific feedback
3. POST to `/api/editorial/{id}/request-revision`
4. Status changed to `revision_requested`
5. ArticleRevision record created with editorial notes
6. Revision counter incremented

### Revision Requested → Draft (Manual Step)
**Note:** This step requires manual trigger of Enhanced Journalist Agent
1. Call Enhanced Journalist Agent with article_id and editorial_notes
2. Agent regenerates article addressing all feedback
3. Agent updates article content and status back to `draft`
4. Editorial Coordinator detects updated draft
5. Re-assigns to same editor
6. "Revision complete" email sent

### Under Review → Approved
1. Editor satisfied with article quality
2. POST to `/api/editorial/{id}/approve`
3. Status changed to `approved`
4. Article ready for publication

### Under Review → Rejected
1. Editor determines article doesn't meet standards
2. POST to `/api/editorial/{id}/reject` with reason
3. Status changed to `archived`
4. Rejection reason saved in editorial_notes

### Max Revisions Reached
1. After 2 revision requests (3 total attempts)
2. Third revision request blocked
3. Status changed to `needs_senior_review`
4. Requires senior editor manual review

## Configuration

### Editor Pool
```python
EDITORS = [
    {"email": "labor@dailyworker.news", "categories": ["labor", "unions"]},
    {"email": "housing@dailyworker.news", "categories": ["housing", "community"]},
    {"email": "politics@dailyworker.news", "categories": ["politics", "government"]},
    {"email": "general@dailyworker.news", "categories": []},  # All categories
]
```

### Environment Variables
```bash
# Email settings
EMAIL_MODE=test
SENDGRID_API_KEY=SG.xxxxx
FROM_EMAIL=editorial@dailyworker.news
ADMIN_URL=http://localhost:3000/admin

# SMTP (optional)
SMTP_SERVER=localhost
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
```

### Scheduled Jobs (Recommended)
```bash
# Auto-assign pending articles (every 10 minutes)
*/10 * * * * curl -X POST http://localhost:8000/api/editorial/auto-assign

# Send overdue alerts (every 4 hours)
0 */4 * * * curl -X POST http://localhost:8000/api/editorial/send-overdue-alerts
```

## Database Schema Updates

### Articles Table
New status values supported:
- `draft` - Generated, awaiting assignment
- `pending_review` - (legacy, unused)
- `under_review` - Assigned to editor
- `revision_requested` - Changes requested
- `approved` - Approved for publication
- `published` - Live on site
- `archived` - Rejected or old
- `needs_senior_review` - Max revisions reached

Existing columns used:
- `bias_scan_report` (JSON) - From Phase 6.5
- `self_audit_passed` (boolean) - From Phase 6.5
- `editorial_notes` (text) - Editor feedback
- `assigned_editor` (text) - Editor email
- `review_deadline` (datetime) - Due date

### Article Revisions Table
Already exists from Phase 6.1, used to track:
- `revision_number` - Attempt number (1, 2, etc.)
- `revised_by` - Editor email
- `revision_type` - 'human_edit' for editorial revisions
- `change_reason` - Editorial notes
- `reading_level_before/after` - Track improvements

## Integration Points

### With Enhanced Journalist Agent
**Current:** Manual trigger required after revision request
**Future:** Auto-trigger journalist agent from revision request

**Manual Workflow:**
```python
from backend.agents.enhanced_journalist_agent import EnhancedJournalistAgent

journalist = EnhancedJournalistAgent()
journalist.regenerate_with_feedback(
    article_id=article_id,
    editorial_notes=editorial_notes,
    attempt_number=2
)
```

### With Existing Admin Portal
- Seamlessly integrated into existing admin dashboard
- Preserves existing "Quick View" preview functionality
- New "Review" button for full editorial interface
- Uses existing authentication (from Batch 3, Phase 3.1)

### With Bias Detection System (Phase 6.5)
- Displays self-audit checklist in review interface
- Shows bias scan report results
- Only assigns articles with `self_audit_passed=True`

### With Verification System (Phase 6.4)
- Displays verified sources in review interface
- Shows credibility scores (1-5 stars)
- Links to source plan from topics table

## Quality Assurance

### SLA Compliance
- News articles: 24-hour review deadline
- Analysis articles: 48-hour review deadline
- Overdue alerts at deadline + 4 hours
- Escalation flag at deadline + 12 hours (manual)

### Editorial Quality
- Editorial notes must be specific and actionable
- Journalist agent must address ALL notes in revision
- Maximum 2 revisions per article (3 total attempts)
- Complete revision history preserved

### Admin Interface
- All 10 self-audit criteria visible
- Bias scan results clearly displayed
- Sources with credibility tiers
- One-click actions (Approve/Revise/Reject)
- Mobile-responsive design

## Success Metrics

### Test Coverage
- 8/8 end-to-end tests passing
- All core workflows validated
- Database integrity maintained
- No regressions in existing functionality

### Code Quality
- Clean separation of concerns
- Comprehensive error handling
- Detailed logging throughout
- Type hints in Python code
- Pydantic models for API validation

### Documentation
- Complete agent definition document
- API reference with examples
- Configuration guide
- Troubleshooting section
- Migration instructions

## Known Limitations

### Manual Journalist Agent Trigger
The journalist agent regeneration after revision request is currently a manual step. This requires:
1. Detecting revision_requested status
2. Calling Enhanced Journalist Agent with editorial notes
3. Agent updating article and status back to draft

**Future Enhancement:** Auto-trigger journalist agent from revision request endpoint

### Email Test Mode Default
Email system defaults to test mode (console logging) for development. Production deployment requires:
1. Set `EMAIL_MODE=sendgrid`
2. Configure `SENDGRID_API_KEY`
3. Verify `FROM_EMAIL` domain

### No Slack Integration
Currently only supports email notifications. Future enhancement could add:
- Slack webhooks for editor notifications
- Real-time assignment alerts
- Overdue warnings in Slack channels

### Simple Editor Assignment
Current algorithm uses round-robin by workload. Could be enhanced with:
- Editor expertise scores
- Time zone considerations
- Priority queues for urgent articles
- Smart load balancing

## Future Enhancements

### 1. Automated Journalist Trigger
```python
# In editorial.py request-revision endpoint
coordinator.process_revision_request(article_id, editorial_notes)

# Auto-trigger journalist agent
journalist = EnhancedJournalistAgent(db)
journalist.regenerate_with_feedback(
    article_id=article_id,
    editorial_notes=editorial_notes
)

# Re-assign to same editor
coordinator.assign_article(article_id, editor_email=original_editor)
coordinator.notify_editor(article_id)
```

### 2. Revision Diff View
Show what changed between versions:
- Side-by-side comparison
- Highlighted changes
- Specific sections addressing editorial notes

### 3. Editor Performance Metrics
Track and display:
- Average review time per editor
- Approval vs. revision rate
- Specialty accuracy
- Workload distribution

### 4. Senior Editor Escalation
Automated workflow for `needs_senior_review` status:
- Auto-assign to senior editor pool
- Higher priority in queue
- Special notification template

### 5. Slack Integration
```python
def send_slack_assignment(article, editor):
    slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
    message = {
        "text": f"New article assigned to {editor}",
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{article.title}*"},
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Review"},
                        "url": f"{ADMIN_URL}/review/{article.id}"
                    }
                ]
            }
        ]
    }
    requests.post(slack_webhook, json=message)
```

## Usage Examples

### Running Scheduled Jobs
```bash
# Start scheduler (using cron or supervisor)
*/10 * * * * curl -X POST http://localhost:8000/api/editorial/auto-assign
0 */4 * * * curl -X POST http://localhost:8000/api/editorial/send-overdue-alerts
```

### Python Integration
```python
from backend.database import get_db
from backend.agents.editorial_coordinator_agent import EditorialCoordinator

db = next(get_db())
coordinator = EditorialCoordinator(db)

# Batch assign all pending articles
count = coordinator.auto_assign_pending_articles()
print(f"Assigned {count} articles")

# Check for overdue reviews
overdue = coordinator.check_overdue_reviews()
print(f"Found {len(overdue)} overdue articles")

# Send alerts
alerts_sent = coordinator.send_overdue_alerts()
print(f"Sent {alerts_sent} alerts")
```

### API Usage
```bash
# Get pending articles
curl http://localhost:8000/api/editorial/pending?status=draft

# Get article for review
curl http://localhost:8000/api/editorial/review/123

# Approve article
curl -X POST http://localhost:8000/api/editorial/123/approve \
  -H "Content-Type: application/json" \
  -d '{"approved_by": "editor@dailyworker.news"}'

# Request revision
curl -X POST http://localhost:8000/api/editorial/123/request-revision \
  -H "Content-Type: application/json" \
  -d '{
    "editorial_notes": "Add more worker quotes",
    "requested_by": "editor@dailyworker.news"
  }'
```

## Files Created/Modified

### New Files
- `/backend/agents/editorial_coordinator_agent.py` (479 lines)
- `/backend/agents/email_notifications.py` (381 lines)
- `/backend/routes/editorial.py` (438 lines)
- `/frontend/admin/review-article.html` (684 lines)
- `/database/migrations/002_editorial_workflow_statuses.sql` (91 lines)
- `/database/migrations/run_migration_002.py` (145 lines)
- `/.claude/agents/editorial-coordinator.md` (834 lines)
- `/scripts/test_editorial_workflow.py` (549 lines)

### Modified Files
- `/backend/main.py` - Added editorial routes import
- `/frontend/admin/admin.js` - Added review button and navigation
- `/database/models.py` - Updated status constraint

**Total Lines of Code:** ~3,600 lines

## Deployment Checklist

- [x] Run database migration 002
- [x] Update environment variables (EMAIL_MODE, etc.)
- [x] Configure editor pool in editorial_coordinator_agent.py
- [x] Set up scheduled jobs for auto-assignment and alerts
- [x] Test email notifications (start with test mode)
- [x] Verify admin portal accessibility
- [x] Run end-to-end tests
- [ ] Configure SendGrid for production (if using)
- [ ] Set up monitoring for overdue reviews
- [ ] Train editors on new review interface
- [ ] Document editor workflows

## Support & Troubleshooting

See complete troubleshooting guide in:
`/.claude/agents/editorial-coordinator.md` (lines 700-750)

Common issues:
- Emails not sending → Check EMAIL_MODE environment variable
- Articles not auto-assigning → Verify self_audit_passed=True
- Revision loop not working → Ensure journalist agent triggered
- Admin interface not loading → Check API endpoint URL and CORS

## Conclusion

Phase 6.6 successfully integrates human editorial oversight into the automated journalism pipeline. All core functionality is implemented and tested. The system provides a complete workflow for human editors to review, revise, and approve AI-generated articles while maintaining quality standards and SLA compliance.

**Next Steps:**
1. Deploy to staging environment
2. Train editorial team on new interface
3. Monitor initial usage and gather feedback
4. Implement auto-trigger for journalist agent regeneration
5. Add Slack integration for real-time notifications
