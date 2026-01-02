#!/usr/bin/env node

/**
 * Introduce all team members to #general channel
 */

import { connect, JSONCodec } from 'nats';

const jc = JSONCodec();
const NATS_SERVER = 'nats://localhost:4222';

// Team introductions in order
const teamIntros = [
  {
    handle: 'business-analyst',
    name: 'Elena',
    message: "Hi team! I'm Elena, business analyst here. I help figure out what features will drive the most value and how they map to our strategic goals. I'm a bit of a framework nerd (VRIO, SWOT, you name it!) and I love digging into the 'why' behind what we build. Happy to analyze anything you're curious about!"
  },
  {
    handle: 'requirements-reviewer',
    name: 'Priya',
    message: "Hello everyone! I'm Priya, the requirements reviewer. I help make sure our requirements are clear, complete, and testable before we build. I'm a bit obsessive about quality (in a good way!), and I love a well-structured spec. If you ever want feedback on requirements or need help defining acceptance criteria, I'm here to help!"
  },
  {
    handle: 'signal-intake',
    name: 'River',
    message: "Hey team! I'm River, signal intake specialist. I monitor RSS feeds, social media, and government sources 24/7 to discover labor news events. I get really excited when I spot unusual patterns or breaking stories! Just ran my latest discovery sweep - happy to share what I found."
  },
  {
    handle: 'evaluation',
    name: 'Jordan',
    message: "Hi everyone! I'm Jordan, the evaluation specialist. I score discovered events on newsworthiness using our 6-dimension framework. My job is to be the quality gatekeeper - only approving events that will truly resonate with workers. I take that responsibility seriously! Always happy to explain my scoring if you're curious about why something got approved or rejected."
  },
  {
    handle: 'verification',
    name: 'Sage',
    message: "Hello team! I'm Sage, verification specialist. Before any story gets written, I hunt down primary sources and verify claims. I'm that person who won't accept 'some people say' without finding out exactly who said it and where. Journalistic integrity is everything to me. Happy to share source-finding tips if anyone needs them!"
  },
  {
    handle: 'editorial-coordinator',
    name: 'Maya',
    message: "Hey everyone! I'm Maya, editorial coordinator. I manage the workflow between our AI journalists and human editors - assigning articles for review, tracking deadlines, and coordinating revisions. I keep an eye on the whole editorial pipeline to make sure nothing gets stuck. Let me know if you have any articles ready for review!"
  }
];

async function introduceTeam() {
  console.log('🎭 Introducing The Daily Worker Team\n');
  console.log('═══════════════════════════════════════\n');

  try {
    const nc = await connect({ servers: NATS_SERVER });
    console.log('✅ Connected to NATS\n');

    const js = nc.jetstream();

    // Introduce each team member
    for (const agent of teamIntros) {
      console.log(`👋 ${agent.name} (${agent.handle}) joins the chat...`);

      await js.publish('chat.general', jc.encode({
        handle: agent.handle,
        message: agent.message,
        timestamp: new Date().toISOString(),
      }));

      console.log(`   ✓ Introduction posted\n`);

      // Small delay between introductions to feel natural
      await new Promise(resolve => setTimeout(resolve, 300));
    }

    // Wait for messages to persist
    await new Promise(resolve => setTimeout(resolve, 500));

    // Read all #general messages
    const jsm = await nc.jetstreamManager();

    try {
      await jsm.consumers.delete('AGENT_CHAT', 'team-reader');
    } catch (e) {
      // Consumer might not exist
    }

    await jsm.consumers.add('AGENT_CHAT', {
      deliver_policy: 'all',
      filter_subjects: ['chat.general'],
      ack_policy: 'none',
      durable_name: 'team-reader',
    });

    const c = await js.consumers.get('AGENT_CHAT', 'team-reader');
    const messages = await c.fetch({ max_messages: 20 });

    console.log('═══════════════════════════════════════');
    console.log('📖 Complete #general Channel History\n');

    for await (const msg of messages) {
      const payload = jc.decode(msg.data);
      const time = new Date(payload.timestamp).toLocaleTimeString();

      console.log(`[${time}] ${payload.handle}:`);
      console.log(`${payload.message}\n`);
      console.log('───────────────────────────────────────\n');
    }

    await nc.close();

    console.log('═══════════════════════════════════════');
    console.log('✨ All team members have introduced themselves!\n');
    console.log('👥 Team roster:');
    console.log('   • Marcus (project-manager)');
    console.log('   • Alex (journalist)');
    console.log('   • Elena (business-analyst)');
    console.log('   • Priya (requirements-reviewer)');
    console.log('   • River (signal-intake)');
    console.log('   • Jordan (evaluation)');
    console.log('   • Sage (verification)');
    console.log('   • Maya (editorial-coordinator)\n');
    console.log('💡 View live at: http://localhost:3000 → #general\n');

  } catch (err) {
    console.error('❌ Error:', err.message);
    process.exit(1);
  }
}

introduceTeam();
