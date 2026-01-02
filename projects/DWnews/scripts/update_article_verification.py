#!/usr/bin/env python3
"""Update article with verification information from topic"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from database.models import Article, Topic

def main():
    db = SessionLocal()

    # Get article and topic
    article = db.query(Article).filter_by(id=1).first()
    if not article:
        print('Article 1 not found')
        db.close()
        return

    print('Article editorial notes:', article.editorial_notes)
    print()

    # Find the topic that created this article
    topic = db.query(Topic).filter_by(article_id=1).first()
    if topic:
        print('Topic verification_status:', topic.verification_status)
        print('Topic source_count:', topic.source_count)

        # Update article editorial notes with verification info
        article.editorial_notes = f'Generated from topic_id={topic.id}. Verification: {topic.verification_status.upper()} ({topic.source_count or 0} sources)'
        db.commit()
        print()
        print('✓ Updated article editorial notes:', article.editorial_notes)
    else:
        print('No topic found for this article')

    db.close()

if __name__ == '__main__':
    main()
