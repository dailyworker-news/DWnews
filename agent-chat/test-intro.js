#!/usr/bin/env node

/**
 * Test agent introduction to #general channel
 */

import { connect, JSONCodec } from 'nats';

const jc = JSONCodec();
const NATS_SERVER = 'nats://localhost:4222';

async function testIntroduction() {
  console.log('🎭 Testing Agent Introduction\n');

  try {
    const nc = await connect({ servers: NATS_SERVER });
    console.log('✅ Connected to NATS\n');

    const js = nc.jetstream();

    // Alex (journalist) introduces themselves
    console.log('👋 Alex (journalist) is joining the team...\n');

    await js.publish('chat.general', jc.encode({
      handle: 'journalist',
      message: "Hey folks! I'm Alex, journalist for The Daily Worker. I write the news articles that make it to our readers - always centering workers' perspectives and material impacts. I love a well-crafted lede and a story that actually matters to people's lives. If you find a great topic or story angle, send it my way!",
      timestamp: new Date().toISOString(),
    }));

    console.log('✅ Introduction posted to #general\n');

    // Wait a moment
    await new Promise(resolve => setTimeout(resolve, 500));

    // Read back from #general to verify
    const jsm = await nc.jetstreamManager();

    // Create a temporary consumer to read #general messages
    try {
      await jsm.consumers.delete('AGENT_CHAT', 'general-reader');
    } catch (e) {
      // Consumer might not exist, that's OK
    }

    const consumer = await jsm.consumers.add('AGENT_CHAT', {
      deliver_policy: 'all',
      filter_subjects: ['chat.general'],
      ack_policy: 'none',
      durable_name: 'general-reader',
    });

    const c = await js.consumers.get('AGENT_CHAT', 'general-reader');
    const messages = await c.fetch({ max_messages: 10 });

    console.log('📖 Messages in #general:\n');
    for await (const msg of messages) {
      const payload = jc.decode(msg.data);
      console.log(`  [${new Date(payload.timestamp).toLocaleTimeString()}] ${payload.handle}:`);
      console.log(`  ${payload.message}\n`);
    }

    await nc.close();

    console.log('✨ Test complete!\n');
    console.log('💡 View in dashboard: http://localhost:3000 → Click #general channel\n');

  } catch (err) {
    console.error('❌ Error:', err.message);
    process.exit(1);
  }
}

testIntroduction();
