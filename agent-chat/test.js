#!/usr/bin/env node

/**
 * Simple test script to demonstrate agent chat functionality
 * This simulates what agents will do when using the MCP tools
 */

import { connect, JSONCodec } from 'nats';

const jc = JSONCodec();
const NATS_SERVER = 'nats://localhost:4222';

async function testAgentChat() {
  console.log('🤖 Agent Chat System Test\n');

  try {
    // Connect to NATS
    const nc = await connect({ servers: NATS_SERVER });
    console.log('✅ Connected to NATS server\n');

    const js = nc.jetstream();
    const jsm = await nc.jetstreamManager();

    // Create stream if it doesn't exist
    try {
      await jsm.streams.add({
        name: 'AGENT_CHAT',
        subjects: ['chat.roadmap', 'chat.coordination', 'chat.errors'],
        retention: 'limits',
        max_msgs_per_subject: 1000,
        max_bytes: 100 * 1024 * 1024,
        max_age: 7 * 24 * 60 * 60 * 1_000_000_000,
        storage: 'file',
      });
      console.log('✅ Created AGENT_CHAT stream\n');
    } catch (err) {
      if (err.message.includes('stream name already in use')) {
        console.log('✅ AGENT_CHAT stream already exists\n');
      } else {
        throw err;
      }
    }

    // Simulate Agent 1: Project Manager
    console.log('📝 Agent: project-manager');
    await js.publish('chat.coordination', jc.encode({
      handle: 'project-manager',
      message: 'Starting Phase 1.1 - GCP Infrastructure setup. ETA: 2 hours',
      timestamp: new Date().toISOString(),
    }));
    console.log('  → Posted to #coordination\n');

    // Simulate Agent 2: Developer
    console.log('👨‍💻 Agent: dev-agent-01');
    await js.publish('chat.coordination', jc.encode({
      handle: 'dev-agent-01',
      message: 'Acknowledged. I\'ll start on database schema design in parallel.',
      timestamp: new Date().toISOString(),
    }));
    console.log('  → Posted to #coordination\n');

    // Post to roadmap channel
    console.log('📊 Agent: business-analyst');
    await js.publish('chat.roadmap', jc.encode({
      handle: 'business-analyst',
      message: 'Updated roadmap.md to reflect quality-over-quantity approach',
      timestamp: new Date().toISOString(),
    }));
    console.log('  → Posted to #roadmap\n');

    // Post an error
    console.log('🚨 Agent: dev-agent-02');
    await js.publish('chat.errors', jc.encode({
      handle: 'dev-agent-02',
      message: 'Failed to connect to external API. Retrying with exponential backoff...',
      timestamp: new Date().toISOString(),
    }));
    console.log('  → Posted to #errors\n');

    // Wait a bit for messages to persist
    await new Promise(resolve => setTimeout(resolve, 500));

    // Read messages from coordination channel
    console.log('📖 Reading messages from #coordination:\n');

    const consumer = await jsm.consumers.add('AGENT_CHAT', {
      deliver_policy: 'all',
      filter_subjects: ['chat.coordination'],
      ack_policy: 'none',
      durable_name: 'test-reader',
    });

    const c = await js.consumers.get('AGENT_CHAT', 'test-reader');
    const messages = await c.fetch({ max_messages: 10 });

    for await (const msg of messages) {
      const payload = jc.decode(msg.data);
      console.log(`  [${payload.timestamp}] ${payload.handle}: ${payload.message}`);
    }

    console.log('\n✨ Test completed successfully!\n');
    console.log('💡 Next steps:');
    console.log('   1. Start the MCP server: npm start');
    console.log('   2. Configure it in your MCP client');
    console.log('   3. Use the tools: set_handle, publish_message, read_messages, list_channels\n');

    await nc.close();
  } catch (err) {
    console.error('❌ Error:', err.message);
    console.error('\n💡 Make sure NATS is running:');
    console.error('   docker-compose up -d\n');
    process.exit(1);
  }
}

testAgentChat();
