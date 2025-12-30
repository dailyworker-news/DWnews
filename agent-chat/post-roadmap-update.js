#!/usr/bin/env node

import { connect, JSONCodec } from 'nats';

const NATS_SERVER = 'nats://localhost:4222';
const jc = JSONCodec();

async function postMessage() {
  try {
    const nc = await connect({ servers: NATS_SERVER });
    console.log('Connected to NATS server');

    const js = nc.jetstream();

    const message = {
      handle: 'project-manager',
      message: `ROADMAP UPDATE v2.0: Restructured to LOCAL-FIRST development approach.

Changes:
• Batches 1-4: Complete local development & testing (ZERO cloud costs)
• Batch 5: GCP deployment ONLY after local validation
• Batches 6-7: Cloud operations & production launch
• All features built/tested locally before spending on cloud

Why: Validate complete MVP functionality without cloud costs. Reduce financial risk. Only pay for cloud after confirming app works.

Development sequence:
1. Local dev environment, database, git (Batch 1)
2. Local content pipeline - discovery, filtering, generation (Batch 2)
3. Local web portal & admin interface (Batch 3)
4. Complete local testing & validation (Batch 4)
5. Deploy to GCP only after local validation (Batch 5)
6. Cloud ops - CI/CD, monitoring, automation (Batch 6)
7. Production testing & soft launch (Batch 7)

Next steps: Begin Batch 1 - Local Development Setup`,
      timestamp: new Date().toISOString()
    };

    await js.publish('chat.roadmap', jc.encode(message));
    console.log('Message published to #roadmap channel');

    await nc.close();
    console.log('Connection closed');
  } catch (err) {
    console.error('Error:', err);
    process.exit(1);
  }
}

postMessage();
