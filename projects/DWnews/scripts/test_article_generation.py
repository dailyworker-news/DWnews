#!/usr/bin/env python3
"""Test article generation with 3-tier verification system"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.agents.enhanced_journalist_agent import EnhancedJournalistAgent

def main():
    db = SessionLocal()

    print('Testing article generation with UNVERIFIED topic...\n')
    print('='*80)

    # Generate article
    journalist = EnhancedJournalistAgent(db)
    article = journalist.generate_article(topic_id=1)

    print('\n' + '='*80)
    if article:
        print('✓ ARTICLE GENERATED SUCCESSFULLY!')
        print('='*80)
        print(f'  ID: {article.id}')
        print(f'  Title: {article.title}')
        print(f'  Word count: {article.word_count}')
        print(f'  Reading level: {article.reading_level:.1f}')
        print(f'  Self-audit passed: {article.self_audit_passed}')
        print(f'  Status: {article.status}')
        print(f'  Editorial notes: {article.editorial_notes}')
        print()
        print('Article body:')
        print('-' * 80)
        print(article.body)
        print('-' * 80)
    else:
        print('✗ Article generation failed')

    db.close()

if __name__ == '__main__':
    main()
