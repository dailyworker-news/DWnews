#!/usr/bin/env python3
"""
Daily Cadence Simulation - Automated Journalism Pipeline

Simulates a typical operational day for the DWnews automated journalism system.
Runs all agents sequentially with realistic timing to demonstrate the daily workflow.

Daily Schedule (Simulated):
- 06:00 AM: Signal Intake Agent discovers events
- 08:00 AM: Evaluation Agent scores events
- 09:00 AM: Verification Agent verifies approved events
- 10:00 AM: Journalist Agent drafts articles
- 12:00 PM: Editorial Coordinator assigns to editors
- 02:00 PM: (Simulated) Editors review and approve
- 05:00 PM: Publication Agent publishes approved articles
- Next 7 days: Monitoring Agent tracks mentions/corrections

For testing, this runs in ~5 minutes with delays between phases.

Usage:
    python scripts/simulate_daily_cadence.py [--fast]

    --fast: Skip delays between phases (for quick testing)
"""

import sys
import os
import time
import argparse
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from database.models import EventCandidate, Topic, Article
from backend.database import SessionLocal
from backend.agents.signal_intake_agent import SignalIntakeAgent
from backend.agents.evaluation_agent import EvaluationAgent
from backend.agents.verification_agent import VerificationAgent
from backend.agents.enhanced_journalist_agent import EnhancedJournalistAgent
from backend.agents.editorial_coordinator_agent import EditorialCoordinator
from backend.agents.publication_agent import PublicationAgent
from backend.agents.monitoring_agent import MonitoringAgent


class DailyCadenceSimulator:
    """Simulates a full day of automated journalism operations"""

    def __init__(self, fast_mode: bool = False):
        self.session = SessionLocal()
        self.fast_mode = fast_mode
        self.start_time = datetime.now()

        # Simulation timing (seconds)
        self.phase_delays = {
            'signal_to_eval': 120 if not fast_mode else 5,      # 2 hours → 2 min
            'eval_to_verify': 60 if not fast_mode else 3,       # 1 hour → 1 min
            'verify_to_journalist': 60 if not fast_mode else 3, # 1 hour → 1 min
            'journalist_to_editorial': 120 if not fast_mode else 5,  # 2 hours → 2 min
            'editorial_to_publication': 180 if not fast_mode else 5, # 3 hours → 3 min
        }

        self.stats = {
            'phase_times': {},
            'phase_results': {}
        }

    def print_header(self, text: str, sim_time: str):
        """Print formatted section header with simulated time"""
        print("\n" + "=" * 70)
        print(f"  [{sim_time}] {text}")
        print("=" * 70)

    def get_simulated_time(self, hours_offset: int) -> str:
        """Get simulated time of day"""
        base_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
        sim_time = base_time + timedelta(hours=hours_offset)
        return sim_time.strftime("%I:%M %p")

    def wait_for_phase(self, phase_name: str):
        """Wait between phases with progress indicator"""
        if phase_name not in self.phase_delays:
            return

        delay = self.phase_delays[phase_name]
        if delay == 0:
            return

        print(f"\n⏳ Waiting {delay}s until next phase", end="", flush=True)

        for i in range(delay):
            if i % 5 == 0:
                print(".", end="", flush=True)
            time.sleep(1)

        print(" Done!\n")

    def phase_1_signal_intake(self):
        """06:00 AM - Signal Intake Agent"""
        sim_time = self.get_simulated_time(0)
        self.print_header("PHASE 1: Signal Intake - Event Discovery", sim_time)

        phase_start = time.time()

        agent = SignalIntakeAgent()
        print("🔍 Scanning RSS feeds, Twitter, Reddit, Government sources...")
        results = agent.discover_events()

        phase_duration = time.time() - phase_start
        self.stats['phase_times']['signal_intake'] = phase_duration
        self.stats['phase_results']['signal_intake'] = results

        print(f"\n📊 Discovery Results:")
        print(f"   Total events discovered: {results.get('total_discovered', 0)}")
        print(f"   RSS feeds: {results.get('rss_count', 0)}")
        print(f"   Twitter: {results.get('twitter_count', 0)}")
        print(f"   Reddit: {results.get('reddit_count', 0)}")
        print(f"   Government: {results.get('government_count', 0)}")
        print(f"   Duplicates removed: {results.get('duplicates_removed', 0)}")
        print(f"\n⏱ Phase completed in {phase_duration:.1f}s")

        return results

    def phase_2_evaluation(self):
        """08:00 AM - Evaluation Agent"""
        sim_time = self.get_simulated_time(2)
        self.print_header("PHASE 2: Evaluation - Newsworthiness Scoring", sim_time)

        phase_start = time.time()

        agent = EvaluationAgent(self.session)
        print("📊 Scoring events on newsworthiness (target: 10-20% approval)...")
        results = agent.evaluate_all_discovered_events()

        phase_duration = time.time() - phase_start
        self.stats['phase_times']['evaluation'] = phase_duration
        self.stats['phase_results']['evaluation'] = results

        total = results.get('evaluated', 0)
        approved = results.get('approved', 0)
        approval_rate = (approved / total * 100) if total > 0 else 0

        print(f"\n📊 Evaluation Results:")
        print(f"   Events evaluated: {total}")
        print(f"   Events approved: {approved}")
        print(f"   Events rejected: {results.get('rejected', 0)}")
        print(f"   Approval rate: {approval_rate:.1f}%")
        print(f"\n⏱ Phase completed in {phase_duration:.1f}s")

        return results

    def phase_3_verification(self):
        """09:00 AM - Verification Agent"""
        sim_time = self.get_simulated_time(3)
        self.print_header("PHASE 3: Verification - Source Verification", sim_time)

        phase_start = time.time()

        agent = VerificationAgent(self.session)
        print("🔍 Verifying sources for approved topics (≥3 credible sources)...")
        results = agent.verify_all_approved_topics()

        phase_duration = time.time() - phase_start
        self.stats['phase_times']['verification'] = phase_duration
        self.stats['phase_results']['verification'] = results

        print(f"\n📊 Verification Results:")
        print(f"   Topics processed: {results.get('total', 0)}")
        print(f"   Successfully verified: {results.get('successful', 0)}")
        print(f"   Failed verification: {results.get('failed', 0)}")
        print(f"\n⏱ Phase completed in {phase_duration:.1f}s")

        return results

    def phase_4_journalist(self):
        """10:00 AM - Enhanced Journalist Agent"""
        sim_time = self.get_simulated_time(4)
        self.print_header("PHASE 4: Journalist - Article Generation", sim_time)

        phase_start = time.time()

        agent = EnhancedJournalistAgent(self.session)

        # Get verified topics
        verified_topics = self.session.query(Topic).filter_by(
            verification_status='verified'
        ).all()

        print(f"✍️ Generating articles from {len(verified_topics)} verified topics...")

        articles_generated = 0
        for topic in verified_topics:
            try:
                article = agent.generate_article(topic.id)
                articles_generated += 1
                print(f"   ✓ Generated: {article.title[:50]}...")
            except Exception as e:
                print(f"   ✗ Failed for topic {topic.id}: {e}")

        phase_duration = time.time() - phase_start
        self.stats['phase_times']['journalist'] = phase_duration
        self.stats['phase_results']['journalist'] = {'generated': articles_generated}

        print(f"\n📊 Article Generation Results:")
        print(f"   Articles generated: {articles_generated}")
        print(f"\n⏱ Phase completed in {phase_duration:.1f}s")

        return {'generated': articles_generated}

    def phase_5_editorial(self):
        """12:00 PM - Editorial Coordinator"""
        sim_time = self.get_simulated_time(6)
        self.print_header("PHASE 5: Editorial - Assignment & Review", sim_time)

        phase_start = time.time()

        coordinator = EditorialCoordinator(self.session)

        # Get draft articles
        draft_articles = self.session.query(Article).filter_by(status='draft').all()

        print(f"📝 Assigning {len(draft_articles)} articles to editors...")

        test_editors = [
            "editor1@dailyworker.news",
            "editor2@dailyworker.news",
            "editor3@dailyworker.news"
        ]

        assigned = 0
        for i, article in enumerate(draft_articles):
            try:
                editor = test_editors[i % len(test_editors)]
                coordinator.assign_article(article.id, editor)
                assigned += 1
                print(f"   ✓ Assigned to {editor}: {article.title[:40]}...")
            except Exception as e:
                print(f"   ✗ Failed: {e}")

        phase_duration = time.time() - phase_start
        self.stats['phase_times']['editorial'] = phase_duration
        self.stats['phase_results']['editorial'] = {'assigned': assigned}

        print(f"\n📊 Editorial Assignment Results:")
        print(f"   Articles assigned: {assigned}")
        print(f"\n⏱ Phase completed in {phase_duration:.1f}s")

        return {'assigned': assigned}

    def phase_5b_editorial_review(self):
        """02:00 PM - Simulated Editorial Review"""
        sim_time = self.get_simulated_time(8)
        self.print_header("PHASE 5b: Editorial Review (Simulated)", sim_time)

        phase_start = time.time()

        print("📝 Simulating human editor review process...")

        # Get articles under review
        under_review = self.session.query(Article).filter_by(status='under_review').all()

        approved = 0
        revision_requested = 0

        for article in under_review:
            # Simulate: 80% approval, 20% revision request
            import random
            if random.random() < 0.8:
                article.status = 'approved'
                article.editorial_notes = "Approved - ready for publication"
                approved += 1
                print(f"   ✓ Approved: {article.title[:40]}...")
            else:
                article.status = 'revision_requested'
                article.editorial_notes = "Please clarify source attribution in paragraph 3"
                revision_requested += 1
                print(f"   📝 Revision requested: {article.title[:40]}...")

        self.session.commit()

        phase_duration = time.time() - phase_start
        self.stats['phase_times']['editorial_review'] = phase_duration
        self.stats['phase_results']['editorial_review'] = {
            'approved': approved,
            'revision_requested': revision_requested
        }

        print(f"\n📊 Editorial Review Results:")
        print(f"   Articles approved: {approved}")
        print(f"   Revisions requested: {revision_requested}")
        print(f"\n⏱ Phase completed in {phase_duration:.1f}s")

        return {'approved': approved, 'revision_requested': revision_requested}

    def phase_6_publication(self):
        """05:00 PM - Publication Agent"""
        sim_time = self.get_simulated_time(11)
        self.print_header("PHASE 6: Publication - Article Publishing", sim_time)

        phase_start = time.time()

        agent = PublicationAgent(self.session)
        print("📰 Publishing approved articles...")
        published = agent.publish_approved_articles()

        phase_duration = time.time() - phase_start
        self.stats['phase_times']['publication'] = phase_duration
        self.stats['phase_results']['publication'] = {'published': len(published)}

        print(f"\n📊 Publication Results:")
        print(f"   Articles published: {len(published)}")

        for article in published:
            print(f"   ✓ Published: {article.title[:50]}...")

        print(f"\n⏱ Phase completed in {phase_duration:.1f}s")

        return {'published': len(published)}

    def phase_7_monitoring(self):
        """Ongoing - Monitoring Agent"""
        sim_time = "Next 7 days"
        self.print_header("PHASE 7: Monitoring - Post-Publication Tracking", sim_time)

        phase_start = time.time()

        agent = MonitoringAgent(self.session)
        print("👀 Monitoring published articles (7-day window)...")
        results = agent.monitor_published_articles()

        phase_duration = time.time() - phase_start
        self.stats['phase_times']['monitoring'] = phase_duration
        self.stats['phase_results']['monitoring'] = {'monitored': len(results)}

        print(f"\n📊 Monitoring Results:")
        print(f"   Articles being monitored: {len(results)}")

        for result in results[:3]:  # Show first 3
            print(f"   👁 {result['title'][:40]}... (published {result['published_at']})")

        print(f"\n⏱ Phase completed in {phase_duration:.1f}s")

        return {'monitored': len(results)}

    def print_final_summary(self):
        """Print final daily summary"""
        total_duration = time.time() - self.start_time.timestamp()

        print("\n" + "=" * 70)
        print("  DAILY CADENCE COMPLETE - SUMMARY")
        print("=" * 70)

        print(f"\n📅 Simulated Day Summary:")
        print(f"   06:00 AM - Signal Intake discovered {self.stats['phase_results']['signal_intake'].get('total_discovered', 0)} events")
        print(f"   08:00 AM - Evaluation approved {self.stats['phase_results']['evaluation'].get('approved', 0)} events")
        print(f"   09:00 AM - Verification verified {self.stats['phase_results']['verification'].get('successful', 0)} topics")
        print(f"   10:00 AM - Journalist generated {self.stats['phase_results']['journalist'].get('generated', 0)} articles")
        print(f"   12:00 PM - Editorial assigned {self.stats['phase_results']['editorial'].get('assigned', 0)} articles")
        print(f"   02:00 PM - Editors approved {self.stats['phase_results']['editorial_review'].get('approved', 0)} articles")
        print(f"   05:00 PM - Publication published {self.stats['phase_results']['publication'].get('published', 0)} articles")
        print(f"   Ongoing  - Monitoring {self.stats['phase_results']['monitoring'].get('monitored', 0)} articles")

        print(f"\n⏱ Phase Execution Times:")
        for phase, duration in self.stats['phase_times'].items():
            print(f"   {phase:20s}: {duration:6.1f}s")

        print(f"\n⏱ Total simulation time: {total_duration:.1f}s")

        # Calculate daily throughput
        events_in = self.stats['phase_results']['signal_intake'].get('total_discovered', 0)
        articles_out = self.stats['phase_results']['publication'].get('published', 0)

        if events_in > 0:
            conversion = (articles_out / events_in) * 100
            print(f"\n📈 Daily Throughput:")
            print(f"   Input:  {events_in} events discovered")
            print(f"   Output: {articles_out} articles published")
            print(f"   Conversion rate: {conversion:.1f}%")

        print(f"\n✓ Daily cadence simulation completed successfully")

    def run(self):
        """Run the complete daily cadence simulation"""
        print("\n" + "=" * 70)
        print("  DWnews Automated Journalism Pipeline")
        print("  Daily Cadence Simulation")
        print("=" * 70)

        if self.fast_mode:
            print("\n⚡ FAST MODE: Running with reduced delays")
        else:
            print("\n🕐 NORMAL MODE: Running with realistic timing (~5 minutes)")

        print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Run all phases with delays
        self.phase_1_signal_intake()
        self.wait_for_phase('signal_to_eval')

        self.phase_2_evaluation()
        self.wait_for_phase('eval_to_verify')

        self.phase_3_verification()
        self.wait_for_phase('verify_to_journalist')

        self.phase_4_journalist()
        self.wait_for_phase('journalist_to_editorial')

        self.phase_5_editorial()
        self.wait_for_phase('editorial_to_publication')

        self.phase_5b_editorial_review()

        self.phase_6_publication()

        self.phase_7_monitoring()

        # Print summary
        self.print_final_summary()

        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Close session
        self.session.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Simulate daily journalism pipeline cadence')
    parser.add_argument('--fast', action='store_true', help='Run in fast mode (skip delays)')
    args = parser.parse_args()

    simulator = DailyCadenceSimulator(fast_mode=args.fast)
    simulator.run()


if __name__ == "__main__":
    main()
