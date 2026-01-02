#!/bin/bash

# autonomous_agent.sh
# Launches Claude Code to autonomously execute roadmap workstreams using TDD

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🤖 Autonomous Agent Starting...${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Step 1: Execute TDD workstream
echo -e "${YELLOW}📋 Step 1: Executing next roadmap workstream with TDD...${NC}\n"

claude --print --dangerously-skip-permissions \
  "Please look at the roadmap at projects/DWnews/plans/roadmap.md and use the Task tool with subagent_type='tdd-workstream-executor' to claim and execute the next available workstream from the roadmap using test-driven development practices."

echo -e "\n${GREEN}✅ Workstream execution complete${NC}\n"

# Step 2: Check if working tree is dirty and commit if needed
echo -e "${YELLOW}🔍 Step 2: Checking for uncommitted changes...${NC}\n"

if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo -e "${GREEN}📝 Working tree has changes. Spawning Claude Code to commit...${NC}\n"

    claude --print --dangerously-skip-permissions \
      "Please create a git commit for all changes in the working tree. Review the changes with git status and git diff, then create an appropriate commit message that accurately reflects the work done and commit the changes."

    echo -e "\n${GREEN}✅ Changes committed successfully${NC}\n"
else
    echo -e "${GREEN}✨ Working tree is clean. No commit needed.${NC}\n"
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🎉 Autonomous Agent Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
