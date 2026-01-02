#!/usr/bin/env python3
"""
Run the REAL automated journalism pipeline with live data.
No hallucinations - only real events from real sources.
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from database.models import EventCandidate, Topic, Article
from backend.agents.signal_intake_agent import SignalIntakeAgent
from backend.agents.evaluation_agent import EvaluationAgent
from backend.agents.verification_agent import VerificationAgent
from backend.agents.enhanced_journalist_agent import EnhancedJournalistAgent
from datetime import datetime

def main():
    print("\n" + "="*80)
    print("  THE DAILY WORKER - AUTOMATED JOURNALISM PIPELINE")
    print("  Running with REAL data from REAL sources")
    print("="*80)
    
    session = SessionLocal()
    
    try:
        # PHASE 1: Signal Intake - Discover real events
        print("\n[PHASE 1] SIGNAL INTAKE - Discovering real events...")
        print("-" * 80)
        
        signal_agent = SignalIntakeAgent(max_age_hours=48)
        discovery_results = signal_agent.discover_events()
        
        print(f"✓ Discovered events from live sources:")
        print(f"  Total fetched: {discovery_results.get('total_fetched', 0)}")
        print(f"  Unique events: {discovery_results.get('unique_count', 0)}")
        print(f"  Duplicates removed: {discovery_results.get('duplicates_removed', 0)}")
        
        # Show sample events
        events = session.query(EventCandidate).filter_by(status='discovered').limit(5).all()
        if events:
            print("\n  Sample discovered events:")
            for i, event in enumerate(events, 1):
                print(f"  {i}. {event.title[:70]}...")
                print(f"     Source: {event.discovered_from}")
        
        # PHASE 2: Evaluation - Score for newsworthiness
        print("\n[PHASE 2] EVALUATION - Scoring events for newsworthiness...")
        print("-" * 80)
        
        eval_agent = EvaluationAgent(session)
        eval_results = eval_agent.process_discovered_events(limit=50)
        
        print(f"✓ Evaluation complete:")
        print(f"  Processed: {eval_results.get('processed', 0)}")
        print(f"  Approved (≥65): {eval_results.get('approved', 0)}")
        print(f"  Held (30-64): {eval_results.get('hold', 0)}")
        print(f"  Rejected (<30): {eval_results.get('rejected', 0)}")
        
        if eval_results.get('approved', 0) == 0:
            print("\n⚠  No events scored ≥65 (this is normal - strict quality threshold)")
            print("  The 10-20% approval rate means most events are correctly filtered out.")
            print("\n  To see articles, either:")
            print("  1. Wait for more newsworthy events to be discovered")
            print("  2. Lower the approval threshold temporarily for testing")
            return
        
        # PHASE 3: Verification - Verify sources
        print("\n[PHASE 3] VERIFICATION - Verifying sources for approved topics...")
        print("-" * 80)
        
        verify_agent = VerificationAgent(session)
        verify_results = verify_agent.verify_all_approved_topics()
        
        print(f"✓ Verification complete:")
        print(f"  Topics verified: {verify_results.get('successful', 0)}")
        print(f"  Average sources: {verify_results.get('avg_sources', 0):.1f}")
        
        if verify_results.get('successful', 0) == 0:
            print("\n⚠  No topics passed verification (need ≥3 credible sources)")
            return
        
        # PHASE 4: Article Generation - Create articles with real sources
        print("\n[PHASE 4] ARTICLE GENERATION - Creating articles from verified topics...")
        print("-" * 80)
        
        journalist_agent = EnhancedJournalistAgent(session)
        
        verified_topics = session.query(Topic).filter_by(
            verification_status='verified'
        ).limit(5).all()
        
        print(f"  Found {len(verified_topics)} verified topics to write about\n")
        
        articles_created = 0
        for topic in verified_topics:
            print(f"  Generating: {topic.title[:60]}...")
            
            try:
                article = journalist_agent.generate_article(topic.id)
                articles_created += 1
                
                print(f"  ✓ Created: {article.title}")
                print(f"    Word count: {article.word_count}")
                print(f"    Reading level: {article.reading_level:.1f}")
                print(f"    Self-audit: {'PASSED' if article.self_audit_passed else 'FAILED'}")
                print(f"    Status: {article.status}")
                print()
                
            except Exception as e:
                print(f"  ✗ Error: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Summary
        print("\n" + "="*80)
        print("  PIPELINE COMPLETE")
        print("="*80)
        print(f"\nResults:")
        print(f"  Events discovered: {discovery_results.get('unique_count', 0)}")
        print(f"  Events approved: {eval_results.get('approved', 0)}")
        print(f"  Topics verified: {verify_results.get('successful', 0)}")
        print(f"  Articles created: {articles_created}")
        print(f"\n🌐 View articles at: http://localhost:8080")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n✗ PIPELINE ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        session.close()

if __name__ == '__main__':
    main()
