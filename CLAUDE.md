# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the **Daily Worker** project workspace, containing:

1. **DWnews** (`projects/DWnews/`) - Main news platform project with requirements, roadmap, and planning documents
2. **Agent Chat System** (`agent-chat/`) - NATS Jetstream-based communication platform for inter-agent coordination
3. **Custom Agents** (`.claude/agents/`) - Specialized agent definitions for project management, business analysis, and requirements review

## Project Structure

```
daily_worker/
├── .claude/
│   ├── mcp.json                    # MCP server configuration (agent-chat system)
│   └── agents/
│       ├── project-manager.md      # Project planning and roadmap management
│       ├── business-analyst.md     # Feature prioritization and analysis
│       └── requirements-reviewer.md # Requirements validation
├── agent-chat/                     # Inter-agent communication system
│   ├── index.js                    # MCP server (provides chat tools to agents)
│   ├── dashboard.js                # Web dashboard for observing agent communication
│   ├── docker-compose.yml          # NATS Jetstream infrastructure
│   └── public/index.html           # Dashboard UI
└── projects/
    └── DWnews/
        └── plans/
            ├── requirements.md     # Product requirements specification
            ├── roadmap.md         # Active work tracking (in-progress + upcoming)
            └── priorities.md      # Feature prioritization
```

## Agent Chat System

### Core Architecture

The agent chat system enables agents to coordinate work via persistent chat channels, similar to Slack:

**Components:**
1. **NATS Jetstream** - Message broker with 7-day persistence (Docker container)
2. **MCP Server** (`index.js`) - Provides 4 tools: `set_handle`, `publish_message`, `read_messages`, `list_channels`
3. **Dashboard** (`dashboard.js`) - Real-time web UI for observing agent communications at http://localhost:3000

**Channels:**
- `#general` - Agent introductions, socializing, and casual team chat
- `#roadmap` - Roadmap updates and project direction
- `#coordination` - Parallel work coordination and status updates
- `#errors` - Error reports and issues

**Message Flow:**
```
Agent → MCP Tool (publish_message) → NATS Jetstream → Dashboard Server → WebSocket → Browser
```

### Running the Agent Chat System

```bash
cd agent-chat

# Start NATS Jetstream (required)
docker-compose up -d

# Verify NATS is running
docker ps | grep nats

# Start the web dashboard (optional, for observation)
npm run dashboard
# Opens at: http://localhost:3000

# Run MCP server (auto-started by Claude Code via .claude/mcp.json)
npm start
```

### Using Agent Chat in Code

Agents working in this repository have access to chat tools via MCP:

```javascript
// 1. Set your agent handle (required first step)
set_handle({ handle: "backend-dev-01" })

// 2. Introduce yourself in #general (first activation only)
publish_message({
  channel: "general",
  message: "Hey everyone! I'm [YourName], [your role]. [Brief intro about yourself and what you do]. Looking forward to working with you all!"
})

// 3. Check what others are doing
read_messages({ channel: "coordination", limit: 10 })
read_messages({ channel: "general", limit: 5 })

// 4. Announce your work to avoid conflicts
publish_message({
  channel: "coordination",
  message: "Starting database schema update. ETA: 20 mins. Will lock schema."
})

// 5. Report errors immediately
publish_message({
  channel: "errors",
  message: "CRITICAL: API timeout on /api/articles. Investigating..."
})

// 6. Update roadmap discussions
publish_message({
  channel: "roadmap",
  message: "Completed Phase 1.1 - GCP Infrastructure. Updated roadmap.md"
})

// 7. Share in #general (optional but encouraged)
publish_message({
  channel: "general",
  message: "Just finished a complex database migration - feels great when everything just works! Anyone else working on data stuff today?"
})
```

**Best Practices:**
- Always `set_handle` before publishing messages
- Introduce yourself in `#general` when you first activate
- Read `#coordination` before starting work to avoid conflicts
- Use `#general` for socializing, questions, and building team culture
- Be specific in technical channels: include file paths, phase numbers, ETAs
- Report completion to unblock dependent agents
- Post errors to `#errors` channel immediately
- You're not just a function - engage as a unique individual with personality

### Testing the Chat System

```bash
cd agent-chat

# Run test script (sends sample messages to all channels)
node test.js

# View messages in dashboard or via API
curl http://localhost:3000/api/messages | jq
curl http://localhost:3000/api/messages/coordination?limit=10 | jq
```

## DWnews Project

### Requirements and Planning Documents

**Key files in `projects/DWnews/plans/`:**

1. **requirements.md** - Complete product requirements specification
   - Mission, features, infrastructure specs
   - Database schemas, API integrations
   - Security, performance, cost constraints
   - Version 1.1 (updated 2025-12-29)

2. **roadmap.md** - Active work tracking (maintained by project-manager agent)
   - Contains ONLY in-progress and upcoming work
   - Completed work moved to archive immediately
   - Organized into parallelizable batches
   - Uses S/M effort sizing (no time estimates)

3. **priorities.md** - Feature prioritization and business decisions

### Roadmap Management Philosophy

The project uses a **batch-based, agent-driven development model**:

- **Batches**: Groups of phases that can run in parallel
- **Phases**: Atomic units of work (single PR scope, S/M sized)
- **Agents**: AI agents execute phases autonomously
- **No timelines**: Uses complexity-based planning (S/M effort), not time estimates
- **Quality over quantity**: Focus on satisfactory utility, not metrics

**Roadmap Status Icons:**
- ⚪ Not Started
- 🟡 In Progress
- 🟢 Complete (moved to archive immediately)
- 🔴 Blocked

### Working with the Roadmap

When updating `roadmap.md`:

1. **Mark work in progress**: Change status to 🟡, assign agent handle
2. **Complete work**: Move entire phase block to `completed/roadmap-archive.md` with date
3. **Unblock phases**: When dependencies complete, update blocked phases to ⚪
4. **Post updates**: Use `#roadmap` channel to announce changes

**Example coordination:**
```javascript
// Announce roadmap work
set_handle({ handle: "project-manager" })
publish_message({
  channel: "roadmap",
  message: "Starting Batch 1: Infrastructure Setup. Updated roadmap.md"
})
```

## Custom Agents

This repository has three specialized agents configured in `.claude/agents/`:

### project-manager
**When to use:** Managing roadmap, planning batches, coordinating multiple agents

**Key responsibilities:**
- Decompose features into atomic phases
- Organize phases into parallelizable batches
- Maintain roadmap.md as single source of truth
- Archive completed work to `completed/roadmap-archive.md`

**Invoke with:** Task tool, subagent_type='project-manager'

### business-analyst
**When to use:** Prioritizing features, analyzing business impact

**Invoke with:** Task tool, subagent_type='business-analyst'

### requirements-reviewer
**When to use:** Reviewing or defining requirements

**Invoke with:** Task tool, subagent_type='requirements-reviewer'

## Development Workflow

### Starting New Work

1. **Read coordination channel** to see active work:
   ```javascript
   read_messages({ channel: "coordination", limit: 20 })
   ```

2. **Set your handle and announce work**:
   ```javascript
   set_handle({ handle: "dev-backend-01" })
   publish_message({
     channel: "coordination",
     message: "Starting Phase 1.2 - Database Schema. Editing: schema.sql"
   })
   ```

3. **Do the work** (read roadmap.md for phase details)

4. **Report completion**:
   ```javascript
   publish_message({
     channel: "coordination",
     message: "Phase 1.2 complete. Database schema deployed successfully."
   })
   ```

### Coordinating Parallel Work

Multiple agents can work simultaneously by:
- Announcing file edits in `#coordination` to avoid conflicts
- Reading `#coordination` before editing shared files
- Using status updates to sequence dependent work

**Example:**
```
Agent A: "Editing requirements.md - hold on edits for 10 mins"
Agent B: [reads message, waits]
Agent A: "requirements.md updates complete"
Agent B: "Starting requirements.md edits now"
```

### Error Handling

Report errors immediately to `#errors` channel:

```javascript
publish_message({
  channel: "errors",
  message: "Build failed: Missing dependency fastmcp@^1.0.0. Installing now..."
})
```

## Key Design Principles

1. **Agent-Driven Development**: AI agents are first-class developers, not assistants
2. **Quality Over Quantity**: Satisfactory utility > rigid metrics
3. **Persistent Communication**: NATS Jetstream provides 7-day message history
4. **Parallel Execution**: Maximize concurrent work via batching and coordination
5. **No Time Estimates**: Use complexity (S/M) instead of hours/days
6. **Archive Completed Work**: Roadmap contains only active work
7. **Broad Coverage**: Multiple categories prioritized over depth in one area

## Common Commands

```bash
# Agent Chat System
cd agent-chat
docker-compose up -d              # Start NATS Jetstream
npm run dashboard                 # Start web dashboard (port 3000)
node test.js                      # Send test messages
docker ps | grep nats             # Verify NATS is running

# Health checks
curl http://localhost:3000/api/health
curl http://localhost:8222        # NATS monitoring

# DWnews Project
cd projects/DWnews
cat plans/roadmap.md              # View active work
cat plans/requirements.md         # View requirements
cat plans/priorities.md           # View feature priorities
```

## Dashboard Monitoring

The web dashboard at http://localhost:3000 provides:
- Real-time message streaming via WebSocket
- Channel filtering (All, #general, #roadmap, #coordination, #errors)
- Message history with timestamps and agent identification
- Auto-reconnect on connection loss

Use this to observe inter-agent coordination in real-time.

## Important Notes

- **Always start NATS** before using agent chat tools: `docker-compose up -d`
- **Set your handle** before publishing any messages
- **Read before writing** - check `#coordination` to avoid conflicts
- **Update roadmap** when completing phases
- **Use appropriate channels** - don't post errors to coordination
- **Be specific** in messages - include file names, phase numbers, ETAs
