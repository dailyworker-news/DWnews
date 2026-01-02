# Editorial Workflow Enhancements Implementation Plan

## Document Information

**Version:** 1.0
**Date:** 2026-01-01
**Project:** The Daily Worker (Project Code: DWnews)
**Batch:** 6.10 (Phases 6.10.4 and 6.10.5)
**Status:** Planning
**Priority:** High (Phase 6.10.4), Medium (Phase 6.10.5)

---

## Summary

This plan implements two critical editorial workflow enhancements discovered during user testing:

1. **Pull Back Approved Stories (Phase 6.10.4):** Allows editors to reverse approval and return articles to revision before publication
2. **Right of Reply Email Workflow (Phase 6.10.5):** Automated email system to request comments from referenced entities before publication

Both features improve editorial quality control and journalistic standards while reducing legal risk.

---

## User Stories

### Story 1: Pull Back Approved Stories

**As an editor,**
I want to pull back an approved article before publication
So that I can fix errors I discovered after approval without the article going live

**Scenario:**
1. Editor reviews article about labor strike
2. Article passes quality checks, editor approves
3. Before publication, editor discovers factual error in strike date
4. Editor pulls back article, requests revision
5. Journalist agent rewrites with correct date
6. Editor re-approves, article publishes correctly

**Current Problem:**
Once article status = 'approved', there's no way to reverse it. Article goes to publication with errors.

**Impact:**
- Editorial mistakes go live
- Reader trust damaged by factual errors
- No recourse for editors who catch errors between approval and publication

### Story 2: Right of Reply Email Workflow

**As an editor,**
I want to automatically email referenced entities for comment
So that I meet journalistic standards and reduce defamation risk

**Scenario:**
1. Article about Goldman Sachs voting record enters review
2. Editor identifies Goldman Sachs as referenced entity
3. System sends automated email to press@goldmansachs.com
4. Email: "You are mentioned in an upcoming article. Please comment by [deadline]."
5. Goldman responds with statement
6. Editor includes response in article before publication
7. Article publishes with balanced perspective

**Current Problem:**
No workflow for offering right of reply. Breaking stories publish without giving referenced parties opportunity to respond.

**Impact:**
- Potential defamation liability
- One-sided reporting
- Journalistic standards not met
- Legal risk from published allegations without comment opportunity

---

## Affected Systems

### Phase 6.10.4: Pull Back Approved Stories
- **Backend API:** `/backend/routes/editorial.py` (new endpoint)
- **Database:** No schema changes (uses existing article_revisions table)
- **Frontend:** `/frontend/admin/review-article.html` (new button)
- **Email System:** `/backend/agents/email_notifications.py` (new template)

### Phase 6.10.5: Right of Reply Email Workflow
- **Database:** New table `right_of_reply_requests`
- **Backend API:** `/backend/routes/right_of_reply.py` (new routes)
- **Database Models:** New SQLAlchemy model `RightOfReplyRequest`
- **Frontend:** `/frontend/admin/right-of-reply.html` (new UI)
- **Email System:** `/backend/agents/email_notifications.py` (new template)
- **Article Schema:** New field `right_of_reply_response` (JSON)

---

## Dependencies

**Phase 6.10.4:**
- Batch 6.6 complete (Editorial Workflow Integration) ✅
- Batch 6.10.3 complete (Category-based assignment)
- `article_revisions` table exists ✅
- Email notification system functional ✅

**Phase 6.10.5:**
- Batch 6.6 complete (Editorial Workflow Integration) ✅
- Batch 6.10.3 complete (Category-based assignment)
- SendGrid or AWS SES email service configured ✅
- Article status field extensible (can add 'awaiting_reply') ✅

---

## Assumptions

1. **Pull Back:**
   - Editors sometimes approve articles in error
   - Time window between approval and publication allows for pull back
   - Pull back should NOT work after publication (immutability)
   - Existing revision workflow can handle pull back articles

2. **Right of Reply:**
   - Editors can identify referenced entities (people, organizations, governments)
   - Entity contact emails are available or researchable
   - 48-72 hour response window is acceptable
   - Not all categories require right of reply (e.g., Sports, Celebrity Gossip)
   - Some editors may manually contact entities (bypass workflow needed)

---

## Risks

### Phase 6.10.4 Risks

**Risk 1: Pull back abuse**
- **Mitigation:** Limit pull backs to 1-2 per article, log all pull backs for audit

**Risk 2: Pull back after auto-publication**
- **Mitigation:** Validate status != 'published' before allowing pull back

**Risk 3: Notification failure**
- **Mitigation:** Log email failures, show error in UI, require manual editor notification

### Phase 6.10.5 Risks

**Risk 1: Email delivery failure**
- **Mitigation:** Use SendGrid with delivery tracking, retry failed sends, log all attempts

**Risk 2: Entity never responds**
- **Mitigation:** Auto-clear 'awaiting_reply' status after deadline, publish with "No response" note

**Risk 3: Invalid email addresses**
- **Mitigation:** Validate email format, allow editor to update contact info, bounce tracking

**Risk 4: Legal liability for not offering reply**
- **Mitigation:** Make right of reply workflow mandatory for Politics, Labor, Economics categories

**Risk 5: Response comes after publication**
- **Mitigation:** Accept late responses, publish as follow-up correction or update

---

## Batch Execution Plan

### Batch 6.10: Multi-Editor User Management + Editorial Workflow Enhancements

| Phase | Goal | Effort | Depends On | Priority |
|-------|------|--------|------------|----------|
| 6.10.1 | Database Schema & Authentication Backend | M | None | High |
| 6.10.2 | User Management API & Admin Interface | M | 6.10.1 | High |
| 6.10.3 | Category-Based Assignment & Editorial Queue | M | 6.10.1, 6.10.2 | High |
| **6.10.4** | **Pull Back Approved Stories** | **S** | **6.10.3** | **High** |
| **6.10.5** | **Right of Reply Email Workflow** | **M** | **6.10.3** | **Medium** |

**Parallel Execution:**
- Phases 6.10.1-6.10.2 can run simultaneously
- Phase 6.10.3 must complete before 6.10.4 and 6.10.5
- Phases 6.10.4 and 6.10.5 can run simultaneously (different systems)

---

## Detailed Phases

### Phase 6.10.4: Pull Back Approved Stories

**Effort:** S (Small - 1-2 days, ~500 lines of code)

**Tasks:**
1. Add pull back API endpoint: `POST /api/editorial/articles/{id}/pull-back`
2. Implement validation logic (status == 'approved', status != 'published')
3. Update article status: 'approved' → 'revision_requested'
4. Append pull back reason to editorial_notes
5. Create article_revision record (type='pull_back', notes=reason)
6. Send email notification to assigned editor
7. Add "Pull Back" button to admin review interface
8. Test pull back workflow end-to-end

**Done When:**
- Editors can pull back approved articles via admin portal
- Pull back blocked for published articles
- Email notifications sent successfully
- Revision tracking logs pull back events
- All validation tests pass

**Deliverables:**
- Pull back API endpoint in `/backend/routes/editorial.py`
- Frontend button and confirmation dialog in `/frontend/admin/review-article.html`
- JavaScript handler in `/frontend/admin/scripts/review.js`
- Email template in `/backend/agents/email_notifications.py`
- Test suite in `/scripts/test_pull_back_workflow.py`
- Documentation in `/docs/EDITORIAL_WORKFLOWS.md`

**Technical Implementation:**

```python
# /backend/routes/editorial.py

@router.post("/articles/{article_id}/pull-back")
async def pull_back_article(
    article_id: int,
    pull_back_request: PullBackRequest,
    db: Session = Depends(get_db)
):
    """
    Pull back an approved article before publication

    Only works for articles in 'approved' status.
    Cannot pull back published articles (immutability).
    """
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Validation
    if article.status == 'published':
        raise HTTPException(
            status_code=400,
            detail="Cannot pull back published articles. Articles are immutable once live."
        )

    if article.status != 'approved':
        raise HTTPException(
            status_code=400,
            detail="Can only pull back approved articles. Current status: " + article.status
        )

    # Update article status
    article.status = 'revision_requested'
    article.editorial_notes = f"PULLED BACK: {pull_back_request.reason}\n\n{article.editorial_notes or ''}"

    # Create revision record
    revision = ArticleRevision(
        article_id=article_id,
        revision_type='pull_back',
        revision_notes=pull_back_request.reason,
        requested_by=pull_back_request.editor_name,
        created_at=datetime.utcnow()
    )
    db.add(revision)

    # Send email notification to assigned editor
    if article.assigned_editor:
        send_pull_back_notification(
            editor_email=article.assigned_editor,
            article_title=article.title,
            reason=pull_back_request.reason
        )

    db.commit()

    return {
        "status": "success",
        "message": "Article pulled back successfully",
        "article_id": article_id,
        "new_status": article.status
    }
```

**Frontend Implementation:**

```javascript
// /frontend/admin/scripts/review.js

async function pullBackArticle(articleId) {
    const reason = prompt("Please provide a reason for pulling back this article:");

    if (!reason || reason.trim() === '') {
        alert("Pull back cancelled. Reason is required.");
        return;
    }

    if (!confirm(`Are you sure you want to pull back this article?\n\nReason: ${reason}\n\nThis will return the article to revision status and notify the assigned editor.`)) {
        return;
    }

    try {
        const response = await fetch(`/api/editorial/articles/${articleId}/pull-back`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                reason: reason,
                editor_name: getCurrentEditorName()
            })
        });

        if (response.ok) {
            alert("Article pulled back successfully. Editor has been notified.");
            window.location.reload();
        } else {
            const error = await response.json();
            alert(`Failed to pull back article: ${error.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}
```

---

### Phase 6.10.5: Right of Reply Email Workflow

**Effort:** M (Medium - 3-5 days, ~1,500 lines of code)

**Tasks:**
1. Create `right_of_reply_requests` database table
2. Add 'awaiting_reply' to article status CheckConstraint
3. Build request reply API: `POST /api/editorial/articles/{id}/request-reply`
4. Build reply recording API: `POST /api/editorial/articles/{id}/record-reply`
5. Build reply status API: `GET /api/editorial/articles/{id}/reply-status`
6. Create email template for right of reply request
7. Build entity identification UI (manual tagging)
8. Build reply recording UI
9. Implement deadline logic (auto-clear after deadline)
10. Add "Awaiting Response" indicator in review interface
11. Test complete workflow end-to-end

**Done When:**
- Right of reply emails sent automatically
- Email delivery tracked (sent, opened, replied, no_response)
- Responses recorded and included in articles
- Deadline logic auto-clears awaiting status
- Manual bypass workflow functional
- All validation tests pass

**Deliverables:**
- Database migration: `/database/migrations/005_right_of_reply.sql`
- SQLAlchemy model: Updated `/database/models.py`
- API routes: `/backend/routes/right_of_reply.py`
- Email template: `/backend/agents/email_templates/right_of_reply.html`
- Frontend UI: `/frontend/admin/right-of-reply.html`
- JavaScript: `/frontend/admin/scripts/right-of-reply.js`
- Test suite: `/scripts/test_right_of_reply_workflow.py`
- Documentation: `/docs/RIGHT_OF_REPLY.md`

**Database Schema:**

```sql
-- /database/migrations/005_right_of_reply.sql

CREATE TABLE right_of_reply_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    entity_name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('person', 'organization', 'government')),
    contact_email VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'sent' CHECK (status IN ('sent', 'opened', 'replied', 'no_response', 'bypassed')),
    deadline TIMESTAMP NOT NULL,
    response_text TEXT,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,
    requested_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_right_of_reply_article_id ON right_of_reply_requests(article_id);
CREATE INDEX idx_right_of_reply_status ON right_of_reply_requests(status);
CREATE INDEX idx_right_of_reply_deadline ON right_of_reply_requests(deadline);

-- Add new article status for awaiting reply
-- (Requires manual update to Article model CheckConstraint)
-- status IN ('draft', 'pending_review', 'under_review', 'revision_requested', 'approved', 'published', 'archived', 'needs_senior_review', 'awaiting_reply')

-- Add optional field to articles for storing responses
ALTER TABLE articles ADD COLUMN right_of_reply_response TEXT;
```

**Email Template:**

```html
<!-- /backend/agents/email_templates/right_of_reply.html -->

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Request for Comment - The Daily Worker</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <h2 style="color: #c41e3a;">Request for Comment</h2>

    <p>Dear {{entity_name}},</p>

    <p>We are preparing an article for publication at <strong>The Daily Worker</strong> that mentions {{entity_type_text}}. In the interest of fairness and accuracy, we would like to offer you an opportunity to comment before publication.</p>

    <div style="background-color: #f5f5f5; padding: 15px; margin: 20px 0; border-left: 4px solid #c41e3a;">
        <h3 style="margin-top: 0;">Article Context:</h3>
        <p><strong>Topic:</strong> {{article_topic}}</p>
        <p><strong>Summary:</strong> {{article_summary}}</p>
        <p><strong>Mention Context:</strong> {{mention_context}}</p>
    </div>

    <p><strong>Response Deadline:</strong> {{deadline_formatted}}</p>

    <p>If you would like to provide a statement or comment, please reply to this email with your response. We will include your statement in the article before publication.</p>

    <p>If you have any questions or concerns, please contact our editorial team.</p>

    <p>Best regards,<br>
    The Daily Worker Editorial Team<br>
    <a href="mailto:editorial@dailyworker.com">editorial@dailyworker.com</a></p>

    <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">

    <p style="font-size: 12px; color: #666;">
        This email was sent as part of our editorial process to ensure balanced reporting.
        If you believe this email was sent in error, please contact us immediately.
    </p>
</body>
</html>
```

**API Implementation:**

```python
# /backend/routes/right_of_reply.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from database.models import Article, RightOfReplyRequest
from backend.database import get_db
from backend.agents.email_notifications import send_right_of_reply_email

router = APIRouter()


@router.post("/articles/{article_id}/request-reply")
async def request_right_of_reply(
    article_id: int,
    request: RequestReplyRequest,
    db: Session = Depends(get_db)
):
    """
    Send right of reply email to referenced entity

    Sets article status to 'awaiting_reply' and sends automated email.
    """
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if article.status == 'published':
        raise HTTPException(status_code=400, detail="Cannot request reply for published article")

    # Calculate deadline (default 48-72 hours based on urgency)
    deadline_hours = 48 if request.urgency == 'high' else 72
    deadline = datetime.utcnow() + timedelta(hours=deadline_hours)

    # Create reply request record
    reply_request = RightOfReplyRequest(
        article_id=article_id,
        entity_name=request.entity_name,
        entity_type=request.entity_type,
        contact_email=request.contact_email,
        status='sent',
        deadline=deadline,
        requested_by=request.editor_name,
        created_at=datetime.utcnow()
    )
    db.add(reply_request)

    # Update article status
    article.status = 'awaiting_reply'

    # Send email
    email_sent = send_right_of_reply_email(
        entity_name=request.entity_name,
        entity_type=request.entity_type,
        contact_email=request.contact_email,
        article_title=article.title,
        article_summary=article.summary,
        mention_context=request.mention_context,
        deadline=deadline
    )

    if not email_sent:
        reply_request.status = 'failed'
        raise HTTPException(status_code=500, detail="Failed to send email")

    db.commit()

    return {
        "status": "success",
        "message": "Right of reply email sent",
        "request_id": reply_request.id,
        "deadline": deadline.isoformat()
    }


@router.post("/articles/{article_id}/record-reply")
async def record_right_of_reply(
    article_id: int,
    reply: RecordReplyRequest,
    db: Session = Depends(get_db)
):
    """
    Record response from referenced entity

    Stores response and clears 'awaiting_reply' status.
    """
    reply_request = db.query(RightOfReplyRequest).filter(
        RightOfReplyRequest.article_id == article_id,
        RightOfReplyRequest.entity_name == reply.entity_name
    ).first()

    if not reply_request:
        raise HTTPException(status_code=404, detail="Reply request not found")

    # Update reply request
    reply_request.response_text = reply.response_text
    reply_request.status = 'replied'
    reply_request.responded_at = datetime.utcnow()

    # Update article
    article = db.query(Article).filter(Article.id == article_id).first()

    # Store response in article
    if article.right_of_reply_response:
        responses = json.loads(article.right_of_reply_response)
    else:
        responses = []

    responses.append({
        "entity": reply.entity_name,
        "response": reply.response_text,
        "timestamp": datetime.utcnow().isoformat()
    })

    article.right_of_reply_response = json.dumps(responses)

    # Check if all pending replies are resolved
    pending_requests = db.query(RightOfReplyRequest).filter(
        RightOfReplyRequest.article_id == article_id,
        RightOfReplyRequest.status.in_(['sent', 'opened'])
    ).count()

    if pending_requests == 0:
        # All replies received or deadlines passed, clear awaiting status
        article.status = 'under_review'

    db.commit()

    return {
        "status": "success",
        "message": "Response recorded successfully",
        "article_status": article.status
    }
```

---

## Stakeholders

**Primary:**
- Editorial team (benefits from pull back and right of reply workflows)
- Journalists (articles pulled back for revision, right of reply responses integrated)
- Legal team (reduced defamation risk from right of reply)

**Secondary:**
- Readers (higher quality articles, balanced reporting)
- Referenced entities (opportunity to comment before publication)

---

## Critical Path

**Phase 6.10.4 (Pull Back) blocks:**
- Nothing (independent feature)

**Phase 6.10.5 (Right of Reply) blocks:**
- Nothing (independent feature)

**Both phases enhance:**
- Editorial quality control
- Journalistic standards compliance
- Legal risk reduction

---

## Suggested First Action

After Batch 6.10.3 completes (Category-Based Assignment):

1. **Start Phase 6.10.4 immediately** (high priority, small effort)
   - Implement pull back API endpoint
   - Add frontend button
   - Test pull back workflow
   - Deploy to staging

2. **Start Phase 6.10.5 in parallel** (medium priority, medium effort)
   - Create database migration
   - Implement right of reply API
   - Build email template
   - Test email workflow

**Rationale:**
- Phase 6.10.4 is small (S) and high priority - quick win
- Phase 6.10.5 is independent, can proceed in parallel
- Both improve editorial quality before production launch

---

## Testing Strategy

### Phase 6.10.4 Testing

**Unit Tests:**
- Pull back API validation (status checks)
- Pull back blocked for published articles
- Editorial notes append correctly
- Revision record creation

**Integration Tests:**
- End-to-end pull back workflow
- Email notification delivery
- Frontend button visibility logic

**Manual Testing:**
- Approve article → pull back → verify status change
- Attempt pull back on published article → verify error
- Verify editor receives email notification

### Phase 6.10.5 Testing

**Unit Tests:**
- Reply request creation
- Email template rendering
- Deadline calculation
- Response recording
- Status transitions

**Integration Tests:**
- End-to-end right of reply workflow
- Email delivery tracking
- Multiple entities per article
- Deadline auto-clear logic

**Manual Testing:**
- Send right of reply email → verify delivery
- Record response → verify article update
- Test deadline expiration → verify status clear
- Test manual bypass workflow

---

## Operational Procedures

### Pull Back Procedure

1. Editor reviews approved article
2. Editor discovers error/issue
3. Editor clicks "Pull Back" button
4. System prompts for reason
5. System validates article status (approved, not published)
6. System updates status to 'revision_requested'
7. System logs revision record
8. System sends email to assigned editor
9. Editor receives notification
10. Journalist agent rewrites article
11. Editor re-reviews and approves

### Right of Reply Procedure

1. Article enters review with referenced entity
2. Editor identifies entity (name, type, email)
3. Editor clicks "Request Right of Reply"
4. System sends email to entity
5. System sets article status to 'awaiting_reply'
6. Entity responds (or deadline passes)
7. Editor records response in system
8. System includes response in article
9. Article proceeds to publication

---

## Success Criteria

**Phase 6.10.4:**
- [ ] Pull back API endpoint functional
- [ ] Pull back blocked for published articles
- [ ] Frontend button visible only for approved articles
- [ ] Email notifications sent successfully
- [ ] Revision tracking logs pull back events
- [ ] All tests passing (unit, integration, manual)

**Phase 6.10.5:**
- [ ] Right of reply emails sent automatically
- [ ] Email delivery tracked accurately
- [ ] Responses recorded and stored in articles
- [ ] Deadline logic auto-clears awaiting status
- [ ] Manual bypass workflow functional
- [ ] All tests passing (unit, integration, manual)

**Overall Batch 6.10:**
- [ ] Multi-editor authentication working
- [ ] Category-based assignment functional
- [ ] Pull back workflow prevents editorial mistakes
- [ ] Right of reply workflow meets journalistic standards
- [ ] Editorial team trained on new features
- [ ] Ready for production deployment

---

## Version History

**Version 1.0 (2026-01-01):**
- Initial plan created
- Two new phases added to Batch 6.10
- User-requested features based on editorial workflow gaps
