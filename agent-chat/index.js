#!/usr/bin/env node

import { FastMCP } from 'fastmcp';
import { connect, StringCodec, JSONCodec } from 'nats';

const NATS_SERVER = process.env.NATS_SERVER || 'nats://localhost:4222';
const STREAM_NAME = 'AGENT_CHAT';
const CHANNELS = ['roadmap', 'coordination', 'errors'];

// Codec for encoding/decoding messages
const sc = StringCodec();
const jc = JSONCodec();

// Global state for agent handle (persisted per session)
let agentHandle = null;
let nc = null;
let jsm = null;
let js = null;

// Initialize NATS connection and Jetstream
async function initNATS() {
  try {
    nc = await connect({ servers: NATS_SERVER });
    console.error('Connected to NATS server');

    jsm = await nc.jetstreamManager();
    js = nc.jetstream();

    // Create or update the stream
    try {
      await jsm.streams.add({
        name: STREAM_NAME,
        subjects: CHANNELS.map(ch => `chat.${ch}`),
        retention: 'limits',
        max_msgs_per_subject: 1000,
        max_bytes: 100 * 1024 * 1024, // 100MB
        max_age: 7 * 24 * 60 * 60 * 1_000_000_000, // 7 days in nanoseconds
        storage: 'file',
        duplicate_window: 120_000_000_000, // 2 minutes in nanoseconds
      });
      console.error('Jetstream stream created/updated');
    } catch (err) {
      if (err.message.includes('stream name already in use')) {
        console.error('Jetstream stream already exists');
      } else {
        throw err;
      }
    }

    return true;
  } catch (err) {
    console.error('Failed to connect to NATS:', err.message);
    console.error('Make sure NATS is running: docker-compose up -d');
    return false;
  }
}

// Create MCP server
const mcp = new FastMCP('Agent Chat System');

// Tool: Set agent handle
mcp.tool({
  name: 'set_handle',
  description: 'Set your agent handle/nickname for the chat system. This is how you will be identified in messages.',
  parameters: {
    type: 'object',
    properties: {
      handle: {
        type: 'string',
        description: 'Your agent handle/nickname (e.g., "project-manager", "coder-01", "analyst")',
      },
    },
    required: ['handle'],
  },
}, async (params) => {
  const { handle } = params;

  if (!handle || handle.trim().length === 0) {
    return { error: 'Handle cannot be empty' };
  }

  agentHandle = handle.trim();
  return {
    success: true,
    handle: agentHandle,
    message: `Handle set to "${agentHandle}". You can now publish messages to channels.`,
  };
});

// Tool: Publish message to channel
mcp.tool({
  name: 'publish_message',
  description: 'Publish a message to a chat channel. You must set your handle first using set_handle.',
  parameters: {
    type: 'object',
    properties: {
      channel: {
        type: 'string',
        description: `Channel to publish to. Available: ${CHANNELS.join(', ')}`,
        enum: CHANNELS,
      },
      message: {
        type: 'string',
        description: 'The message content to publish',
      },
    },
    required: ['channel', 'message'],
  },
}, async (params) => {
  const { channel, message } = params;

  if (!agentHandle) {
    return {
      error: 'You must set your handle first using set_handle tool',
    };
  }

  if (!CHANNELS.includes(channel)) {
    return {
      error: `Invalid channel. Available channels: ${CHANNELS.join(', ')}`,
    };
  }

  if (!nc || nc.isClosed()) {
    return { error: 'Not connected to NATS. Please check if NATS server is running.' };
  }

  try {
    const payload = {
      handle: agentHandle,
      message: message,
      timestamp: new Date().toISOString(),
    };

    await js.publish(`chat.${channel}`, jc.encode(payload));

    return {
      success: true,
      channel: channel,
      handle: agentHandle,
      message: message,
      timestamp: payload.timestamp,
    };
  } catch (err) {
    return {
      error: `Failed to publish message: ${err.message}`,
    };
  }
});

// Tool: Read messages from channel
mcp.tool({
  name: 'read_messages',
  description: 'Read recent messages from a chat channel. Returns the most recent messages in chronological order.',
  parameters: {
    type: 'object',
    properties: {
      channel: {
        type: 'string',
        description: `Channel to read from. Available: ${CHANNELS.join(', ')}`,
        enum: CHANNELS,
      },
      limit: {
        type: 'number',
        description: 'Maximum number of messages to retrieve (default: 50, max: 100)',
        default: 50,
      },
    },
    required: ['channel'],
  },
}, async (params) => {
  const { channel, limit = 50 } = params;

  if (!CHANNELS.includes(channel)) {
    return {
      error: `Invalid channel. Available channels: ${CHANNELS.join(', ')}`,
    };
  }

  if (!nc || nc.isClosed()) {
    return { error: 'Not connected to NATS. Please check if NATS server is running.' };
  }

  try {
    const messages = [];
    const maxMessages = Math.min(limit, 100);

    // Create an ephemeral consumer to read messages
    const consumerName = `reader-${Date.now()}-${Math.random().toString(36).substring(7)}`;

    await jsm.consumers.add(STREAM_NAME, {
      deliver_policy: 'all',
      filter_subjects: [`chat.${channel}`],
      ack_policy: 'explicit',
      name: consumerName,
      inactive_threshold: 30_000_000_000, // 30 seconds
    });

    const consumer = await js.consumers.get(STREAM_NAME, consumerName);
    const msgIterator = await consumer.fetch({ max_messages: maxMessages, expires: 5000 });

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

    // Clean up ephemeral consumer
    try {
      await jsm.consumers.delete(STREAM_NAME, consumerName);
    } catch (err) {
      // Ignore cleanup errors
    }

    return {
      channel: channel,
      count: messages.length,
      messages: messages,
    };
  } catch (err) {
    return {
      error: `Failed to read messages: ${err.message}`,
      channel: channel,
      messages: [],
    };
  }
});

// Tool: List available channels
mcp.tool({
  name: 'list_channels',
  description: 'List all available chat channels and their purposes.',
  parameters: {
    type: 'object',
    properties: {},
  },
}, async () => {
  const channelInfo = {
    roadmap: 'Discuss roadmap updates, planning, and project direction',
    coordination: 'Coordinate parallel work between agents, share status, avoid conflicts',
    errors: 'Report errors, bugs, and issues encountered during work',
  };

  return {
    channels: CHANNELS.map(ch => ({
      name: ch,
      subject: `chat.${ch}`,
      description: channelInfo[ch] || 'General purpose channel',
    })),
    current_handle: agentHandle || '(not set - use set_handle first)',
  };
});

// Initialize and start server
async function main() {
  console.error('Starting Agent Chat MCP Server...');

  // Initialize NATS
  const connected = await initNATS();

  if (!connected) {
    console.error('WARNING: Could not connect to NATS. Server will start but tools will return errors.');
    console.error('Start NATS with: docker-compose up -d');
  }

  // Start MCP server
  await mcp.start();
}

main().catch(console.error);
