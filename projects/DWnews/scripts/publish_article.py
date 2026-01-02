#!/usr/bin/env python3
"""Publish an article for viewing"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from database.models import Article

def main():
    db = SessionLocal()

    # Update article to published status
    article = db.query(Article).filter_by(id=1).first()
    if article:
        article.status = 'published'
        db.commit()
        print(f'✓ Article 1 updated to published status')
        print(f'  Title: {article.title}')
        print(f'  Editorial notes: {article.editorial_notes}')
    else:
        print('Article 1 not found')

    db.close()

if __name__ == '__main__':
    main()
