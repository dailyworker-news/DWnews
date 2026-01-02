#!/usr/bin/env python3
"""
Test Script for Evaluation Agent

Creates sample event candidates with various characteristics and runs
the Evaluation Agent to verify scoring logic and approval rates.

Target: 10-20% approval rate
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from database.models import EventCandidate, Topic, Category, Region
from backend.agents.evaluation_agent import EvaluationAgent


def get_session():
    """Get database session"""
    return SessionLocal()


def create_sample_events(session):
    """Create diverse sample event candidates for testing"""

    print("Creating sample event candidates...")

    # Get a category and region for testing
    category = session.query(Category).first()
    region = session.query(Region).first()

    sample_events = [
        # HIGH-SCORING EVENTS (should be APPROVED)
        {
            'title': 'Amazon Warehouse Workers in NYC Launch Strike Over Safety Violations',
            'description': 'More than 3,000 Amazon warehouse workers at the JFK8 fulfillment center in Staten Island walked off the job today, citing multiple OSHA violations and unsafe working conditions. The strike, organized by the Amazon Labor Union, began at 6am and workers are demanding immediate safety improvements. Reuters confirmed the action with multiple worker interviews and company statements.',
            'source_url': 'https://reuters.com/amazon-strike',
            'discovered_from': 'RSS:Reuters',
            'event_date': datetime.utcnow(),
            'is_national': False,
            'is_local': True,
            'region_id': region.id if region else None,
            'status': 'discovered'
        },
        {
            'title': 'Federal Court Rules Starbucks Illegally Fired Union Organizers Nationwide',
            'description': 'A federal judge ruled today that Starbucks violated federal labor law by firing 12 union organizers across multiple states. The National Labor Relations Board presented evidence of retaliation against workers attempting to unionize. The ruling affects stores in California, New York, Tennessee, and Texas. Starbucks must rehire the workers with back pay.',
            'source_url': 'https://apnews.com/starbucks-ruling',
            'discovered_from': 'RSS:AP',
            'event_date': datetime.utcnow() - timedelta(hours=5),
            'is_national': True,
            'is_local': False,
            'status': 'discovered'
        },
        {
            'title': 'Historic UAW Strike at Ford, GM, and Stellantis Enters Second Week',
            'description': 'The United Auto Workers strike affecting 150,000 workers at the Big Three automakers continues into its second week. Workers are demanding 40% wage increases over four years, elimination of wage tiers, and restoration of cost-of-living adjustments. The strike is the first simultaneous walkout at all three companies. Bloomberg reports negotiations continue but remain far apart.',
            'source_url': 'https://bloomberg.com/uaw-strike',
            'discovered_from': 'RSS:Bloomberg',
            'event_date': datetime.utcnow() - timedelta(days=7),
            'is_national': True,
            'is_local': False,
            'status': 'discovered'
        },
        {
            'title': 'Nurses at Major Hospital Chain Win 30% Raise After 10-Day Strike',
            'description': 'Breaking: Nurses at HCA Healthcare hospitals in California reached a tentative agreement today after a 10-day strike. The deal includes a 30% raise over three years, improved staffing ratios, and enhanced safety protections. Over 12,000 nurses participated in the walkout. California Nurses Association confirmed the agreement.',
            'source_url': 'https://propublica.org/nurses-strike-victory',
            'discovered_from': 'RSS:ProPublica',
            'event_date': datetime.utcnow() - timedelta(hours=2),
            'is_national': False,
            'is_local': True,
            'region_id': region.id if region else None,
            'status': 'discovered'
        },

        # MEDIUM-SCORING EVENTS (should be ON HOLD)
        {
            'title': 'Small Coffee Shop Employees Vote to Unionize in Portland',
            'description': 'Workers at Blue Sky Coffee in Portland, Oregon voted 8-3 to join the Industrial Workers of the World union yesterday. The shop has 12 employees total. Workers cited low wages and lack of health benefits as reasons for organizing. Local news outlet Portland Tribune reported the vote.',
            'source_url': 'https://portland-tribune.com/coffee-union',
            'discovered_from': 'RSS:Local',
            'event_date': datetime.utcnow() - timedelta(days=1),
            'is_national': False,
            'is_local': True,
            'status': 'discovered'
        },
        {
            'title': 'Tech Company Announces New Remote Work Policy',
            'description': 'Salesforce announced a new hybrid work policy allowing employees to work remotely 2-3 days per week. The policy affects approximately 70,000 employees worldwide. Company memo states the change comes after employee feedback surveys. No mention of wage or benefit changes.',
            'source_url': 'https://techcrunch.com/salesforce-remote',
            'discovered_from': 'RSS:TechCrunch',
            'event_date': datetime.utcnow() - timedelta(days=3),
            'is_national': True,
            'is_local': False,
            'status': 'discovered'
        },
        {
            'title': 'Restaurant Workers File Wage Theft Complaint Against Local Chain',
            'description': 'Several workers at a Chicago restaurant chain filed a complaint with the Illinois Department of Labor alleging systematic wage theft. Workers claim unpaid overtime and illegal tip pooling. The investigation is ongoing. Chicago Tribune covered the story based on court documents.',
            'source_url': 'https://chicagotribune.com/wage-theft',
            'discovered_from': 'RSS:Local',
            'event_date': datetime.utcnow() - timedelta(days=5),
            'is_national': False,
            'is_local': True,
            'status': 'discovered'
        },

        # LOW-SCORING EVENTS (should be REJECTED)
        {
            'title': 'CEO Announces Record Profits for Tech Company',
            'description': 'Apple Inc. reported record quarterly profits today during their earnings call. CEO Tim Cook highlighted strong iPhone sales and services growth. Stock price increased 3% after hours. No mention of employee compensation changes.',
            'source_url': 'https://cnbc.com/apple-earnings',
            'discovered_from': 'RSS:CNBC',
            'event_date': datetime.utcnow() - timedelta(days=1),
            'is_national': True,
            'is_local': False,
            'status': 'discovered'
        },
        {
            'title': 'Company Hosts Annual Employee Appreciation Day',
            'description': 'Microsoft held its annual employee appreciation day yesterday with free lunch and gift cards. The event is a yearly tradition. Employees reportedly enjoyed the recognition. No labor disputes or policy changes announced.',
            'source_url': 'https://geekwire.com/microsoft-event',
            'discovered_from': 'RSS:GeekWire',
            'event_date': datetime.utcnow() - timedelta(days=2),
            'is_national': False,
            'is_local': False,
            'status': 'discovered'
        },
        {
            'title': 'Historical Look at 1960s Labor Movement',
            'description': 'A new book examines the labor movement of the 1960s, highlighting key strikes and organizing campaigns from that era. The author is a labor historian at Cornell University. The book is receiving positive reviews.',
            'source_url': 'https://theguardian.com/book-review',
            'discovered_from': 'RSS:Guardian',
            'event_date': datetime.utcnow() - timedelta(days=365),
            'is_national': False,
            'is_local': False,
            'status': 'discovered'
        },
        {
            'title': 'Startup Founder Discusses Company Culture',
            'description': 'A tech startup founder was interviewed about company culture and employee perks. The company offers ping pong tables and free snacks. No discussion of wages, benefits, or labor rights.',
            'source_url': 'https://medium.com/startup-culture',
            'discovered_from': 'Social:Twitter',
            'event_date': datetime.utcnow() - timedelta(days=4),
            'is_national': False,
            'is_local': False,
            'status': 'discovered'
        },

        # EDGE CASES
        {
            'title': 'Unverified Social Media Claim About Workplace Conditions',
            'description': 'An anonymous Twitter account posted claims about unsafe conditions at a warehouse. No corroborating sources. No specific details like company name, location, or dates. The post has been retweeted several times.',
            'source_url': 'https://twitter.com/anonymous/status/123',
            'discovered_from': 'Social:Twitter',
            'event_date': datetime.utcnow() - timedelta(hours=12),
            'is_national': False,
            'is_local': False,
            'status': 'discovered'
        },
        {
            'title': 'Construction Workers Win Safety Improvements After Protests',
            'description': 'Construction workers at a Chicago building site successfully protested for improved safety equipment and training. The contractor agreed to provide harnesses, hard hats, and weekly safety briefings. About 50 workers participated in the one-day work stoppage.',
            'source_url': 'https://chicagosuntimes.com/construction-safety',
            'discovered_from': 'RSS:Local',
            'event_date': datetime.utcnow() - timedelta(days=2),
            'is_national': False,
            'is_local': True,
            'status': 'discovered'
        },
        {
            'title': 'Gig Workers Organize Nationwide Protests for Better Pay',
            'description': 'DoorDash, Uber Eats, and Instacart drivers staged coordinated protests in 15 major cities demanding higher pay and better working conditions. Organizers estimate over 10,000 workers participated. The companies have not responded to worker demands.',
            'source_url': 'https://theverge.com/gig-worker-protests',
            'discovered_from': 'RSS:TheVerge',
            'event_date': datetime.utcnow() - timedelta(hours=8),
            'is_national': True,
            'is_local': False,
            'status': 'discovered'
        },
        {
            'title': 'Teachers Union Reaches Agreement Avoiding Strike',
            'description': 'The Los Angeles teachers union reached a tentative agreement with the school district late last night, averting a planned strike. The deal includes a 7% raise over two years and reduced class sizes. Union members will vote on ratification next week.',
            'source_url': 'https://latimes.com/teachers-agreement',
            'discovered_from': 'RSS:Local',
            'event_date': datetime.utcnow() - timedelta(hours=10),
            'is_national': False,
            'is_local': True,
            'status': 'discovered'
        },
    ]

    # Clear ALL existing event candidates and topics to start fresh
    session.query(Topic).delete()
    session.query(EventCandidate).delete()
    session.commit()

    # Create new test events
    for event_data in sample_events:
        event = EventCandidate(**event_data)
        session.add(event)

    session.commit()
    print(f"Created {len(sample_events)} sample event candidates")
    return len(sample_events)


def print_detailed_results(session, agent):
    """Print detailed results for each event"""

    print("\n" + "=" * 80)
    print("DETAILED SCORING RESULTS")
    print("=" * 80)

    # Get all evaluated events
    events = session.query(EventCandidate).filter(
        EventCandidate.status.in_(['approved', 'rejected', 'evaluated'])
    ).order_by(EventCandidate.final_newsworthiness_score.desc()).all()

    for event in events:
        print(f"\n{'-' * 80}")
        print(f"TITLE: {event.title}")
        print(f"STATUS: {event.status.upper()}")
        print(f"\nScores:")
        print(f"  Worker Impact:      {event.worker_impact_score:.2f}/10 (weight: 30%)")
        print(f"  Timeliness:         {event.timeliness_score:.2f}/10 (weight: 20%)")
        print(f"  Verifiability:      {event.verifiability_score:.2f}/10 (weight: 20%)")
        print(f"  Regional Relevance: {event.regional_relevance_score:.2f}/10 (weight: 15%)")
        print(f"  FINAL SCORE:        {event.final_newsworthiness_score:.2f}/100")

        if event.status == 'approved':
            print(f"  ✅ APPROVED - Topic created (ID: {event.topic_id})")
        elif event.status == 'evaluated':
            print(f"  ⏸️  ON HOLD - {event.rejection_reason}")
        else:
            print(f"  ❌ REJECTED - {event.rejection_reason}")


def main():
    """Main test function"""
    print("=" * 80)
    print("EVALUATION AGENT TEST SUITE")
    print("=" * 80)

    session = get_session()

    try:
        # Step 1: Create sample events
        total_events = create_sample_events(session)

        # Step 2: Initialize evaluation agent
        print("\nInitializing Evaluation Agent...")
        agent = EvaluationAgent(session)

        # Step 3: Run evaluation
        print("\nRunning evaluation on all discovered events...")
        results = agent.process_discovered_events()

        # Step 4: Display results
        print("\n" + "=" * 80)
        print("SUMMARY RESULTS")
        print("=" * 80)
        print(f"Total processed:    {results['total_processed']}")
        print(f"Approved:           {results['approved']} ({results['approval_rate']}%)")
        print(f"On hold:            {results['hold']}")
        print(f"Rejected:           {results['rejected']}")

        # Step 5: Check if approval rate is in target range
        print("\n" + "=" * 80)
        print("QUALITY CHECK")
        print("=" * 80)
        approval_rate = results['approval_rate']

        if 10 <= approval_rate <= 20:
            print(f"✅ PASS: Approval rate {approval_rate}% is within target range (10-20%)")
        elif approval_rate < 10:
            print(f"⚠️  WARNING: Approval rate {approval_rate}% is below target (10-20%)")
            print("   Scorers may be too strict. Consider reviewing thresholds.")
        else:
            print(f"⚠️  WARNING: Approval rate {approval_rate}% is above target (10-20%)")
            print("   Scorers may be too lenient. Consider raising approval threshold.")

        # Step 6: Get detailed stats
        stats = agent.get_evaluation_stats()

        if stats['approved'] > 0:
            print("\n" + "=" * 80)
            print("AVERAGE SCORES FOR APPROVED EVENTS")
            print("=" * 80)
            print(f"Worker Impact:      {stats['avg_approved_scores']['worker_impact']:.2f}/10")
            print(f"Timeliness:         {stats['avg_approved_scores']['timeliness']:.2f}/10")
            print(f"Verifiability:      {stats['avg_approved_scores']['verifiability']:.2f}/10")
            print(f"Regional Relevance: {stats['avg_approved_scores']['regional_relevance']:.2f}/10")
            print(f"Final Score:        {stats['avg_approved_scores']['final_newsworthiness']:.2f}/100")

        # Step 7: Print detailed results for each event
        print_detailed_results(session, agent)

        # Step 8: Verify topic creation
        print("\n" + "=" * 80)
        print("TOPIC CREATION VERIFICATION")
        print("=" * 80)

        approved_events = session.query(EventCandidate).filter(
            EventCandidate.status == 'approved'
        ).all()

        topics_created = 0
        for event in approved_events:
            if event.topic_id:
                topic = session.query(Topic).get(event.topic_id)
                if topic:
                    topics_created += 1
                    print(f"✅ Topic created for: {event.title[:60]}...")
                else:
                    print(f"❌ Topic missing for: {event.title[:60]}...")

        print(f"\nTopics created: {topics_created}/{len(approved_events)}")

        if topics_created == len(approved_events):
            print("✅ PASS: All approved events have topic records")
        else:
            print("❌ FAIL: Some approved events missing topic records")

        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()

    finally:
        session.close()


if __name__ == '__main__':
    main()
