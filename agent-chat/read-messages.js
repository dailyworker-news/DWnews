#!/usr/bin/env node

import { connect, JSONCodec } from 'nats';

const NATS_SERVER = 'nats://localhost:4222';
const jc = JSONCodec();

async function readMessages() {
  try {
    const nc = await connect({ servers: NATS_SERVER });
    console.log('Connected to NATS server');

    const jsm = await nc.jetstreamManager();
    const js = nc.jetstream();

    // Create a temporary consumer
    const consumerName = `temp-reader-${Date.now()}`;

    try {
      await jsm.consumers.add('AGENT_CHAT', {
        durable_name: consumerName,
        ack_policy: 'explicit',
        deliver_policy: 'all',
        filter_subject: 'chat.roadmap',
      });

      const consumer = await js.consumers.get('AGENT_CHAT', consumerName);
      const messages = await consumer.fetch({ max_messages: 10 });

      console.log('\n=== Recent Messages from #roadmap ===\n');

      for await (const msg of messages) {
        const payload = jc.decode(msg.data);
        const date = new Date(payload.timestamp);
        console.log(`[${date.toLocaleString()}] @${payload.handle}:`);
        console.log(`${payload.message}\n`);
        msg.ack();
      }

      // Clean up consumer
      await jsm.consumers.delete('AGENT_CHAT', consumerName);
    } catch (err) {
      console.error('Error reading messages:', err.message);
    }

    await nc.close();
  } catch (err) {
    console.error('Error:', err);
    process.exit(1);
  }
}

readMessages();
