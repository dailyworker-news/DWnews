#!/usr/bin/env node

/**
 * Agent Chat Dashboard
 * Real-time web dashboard for observing inter-agent communication
 */

import express from 'express';
import { WebSocketServer } from 'ws';
import { connect, JSONCodec } from 'nats';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import http from 'http';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const NATS_SERVER = process.env.NATS_SERVER || 'nats://localhost:4222';
const PORT = process.env.PORT || 3000;
const STREAM_NAME = 'AGENT_CHAT';
const CHANNELS = ['general', 'roadmap', 'coordination', 'errors'];

const jc = JSONCodec();

// Express app
const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

// Serve static files
app.use(express.static(join(__dirname, 'public')));

// API: Get recent messages from a channel
app.get('/api/messages/:channel', async (req, res) => {
  const { channel } = req.params;
  const limit = parseInt(req.query.limit) || 50;

  if (!CHANNELS.includes(channel)) {
    return res.status(400).json({ error: 'Invalid channel' });
  }

  try {
    const messages = await getRecentMessages(channel, limit);
    res.json({ channel, messages });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Get messages from all channels
app.get('/api/messages', async (req, res) => {
  const limit = parseInt(req.query.limit) || 20;

  try {
    const allMessages = await Promise.all(
      CHANNELS.map(async (channel) => {
        const messages = await getRecentMessages(channel, limit);
        return messages.map(msg => ({ ...msg, channel }));
      })
    );

    // Flatten and sort by timestamp
    const sorted = allMessages
      .flat()
      .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    res.json({ messages: sorted });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Health check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    nats: nc && !nc.isClosed() ? 'connected' : 'disconnected',
    channels: CHANNELS,
  });
});

let nc = null;
let jsm = null;
let js = null;

// Initialize NATS connection
async function initNATS() {
  try {
    nc = await connect({ servers: NATS_SERVER });
    console.log('✅ Connected to NATS server');

    jsm = await nc.jetstreamManager();
    js = nc.jetstream();

    // Subscribe to all channels for real-time updates
    for (const channel of CHANNELS) {
      subscribeToChannel(channel);
    }

    return true;
  } catch (err) {
    console.error('❌ Failed to connect to NATS:', err.message);
    return false;
  }
}

// Subscribe to a channel and broadcast to WebSocket clients
async function subscribeToChannel(channel) {
  try {
    const consumerName = `dashboard-${channel}`;

    // Create durable consumer for this channel
    try {
      await jsm.consumers.add(STREAM_NAME, {
        durable_name: consumerName,
        deliver_policy: 'new',
        filter_subjects: [`chat.${channel}`],
        ack_policy: 'explicit',
      });
    } catch (err) {
      if (!err.message.includes('consumer name already in use')) {
        throw err;
      }
    }

    const consumer = await js.consumers.get(STREAM_NAME, consumerName);
    const messages = await consumer.consume();

    console.log(`📡 Subscribed to #${channel}`);

    (async () => {
      for await (const msg of messages) {
        try {
          const payload = jc.decode(msg.data);

          // Broadcast to all connected WebSocket clients
          const message = {
            type: 'message',
            channel: channel,
            handle: payload.handle,
            message: payload.message,
            timestamp: payload.timestamp,
          };

          broadcastToClients(message);
          msg.ack();
        } catch (err) {
          console.error('Error processing message:', err);
        }
      }
    })();

  } catch (err) {
    console.error(`Failed to subscribe to #${channel}:`, err.message);
  }
}

// Get recent messages from a channel
async function getRecentMessages(channel, limit = 50) {
  if (!nc || nc.isClosed()) {
    throw new Error('Not connected to NATS');
  }

  const messages = [];
  const consumerName = `reader-${Date.now()}-${Math.random().toString(36).substring(7)}`;

  try {
    await jsm.consumers.add(STREAM_NAME, {
      deliver_policy: 'all',
      filter_subjects: [`chat.${channel}`],
      ack_policy: 'explicit',
      name: consumerName,
      inactive_threshold: 30_000_000_000,
    });

    const consumer = await js.consumers.get(STREAM_NAME, consumerName);
    const msgIterator = await consumer.fetch({
      max_messages: Math.min(limit, 100),
      expires: 5000
    });

    for await (const msg of msgIterator) {
      try {
        const payload = jc.decode(msg.data);
        messages.push({
          handle: payload.handle,
          message: payload.message,
          timestamp: payload.timestamp,
        });
        msg.ack();
      } catch (err) {
        console.error('Failed to decode message:', err);
      }
    }

    // Clean up
    try {
      await jsm.consumers.delete(STREAM_NAME, consumerName);
    } catch (err) {
      // Ignore cleanup errors
    }

    return messages;
  } catch (err) {
    console.error(`Error fetching messages from ${channel}:`, err.message);
    return [];
  }
}

// WebSocket connection handler
wss.on('connection', (ws) => {
  console.log('👤 Dashboard client connected');

  // Send current status
  ws.send(JSON.stringify({
    type: 'connected',
    channels: CHANNELS,
    message: 'Connected to Agent Chat Dashboard',
  }));

  ws.on('close', () => {
    console.log('👤 Dashboard client disconnected');
  });

  ws.on('error', (err) => {
    console.error('WebSocket error:', err);
  });
});

// Broadcast message to all connected WebSocket clients
function broadcastToClients(message) {
  wss.clients.forEach((client) => {
    if (client.readyState === 1) { // OPEN state
      try {
        client.send(JSON.stringify(message));
      } catch (err) {
        console.error('Failed to send to client:', err);
      }
    }
  });
}

// Start the server
async function main() {
  console.log('🚀 Starting Agent Chat Dashboard...\n');

  // Initialize NATS
  const connected = await initNATS();
  if (!connected) {
    console.error('\n⚠️  Dashboard will start but real-time updates disabled');
    console.error('   Start NATS with: docker-compose up -d\n');
  }

  // Start HTTP server
  server.listen(PORT, () => {
    console.log(`\n✨ Dashboard running at http://localhost:${PORT}`);
    console.log(`📊 Open your browser to view agent communications\n`);
  });
}

main().catch(console.error);
