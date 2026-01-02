#!/bin/bash

# test_autonomous_simple.sh
# Simple test of autonomous agent with a specific small task

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🤖 Testing Autonomous Agent (Simple)${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${YELLOW}📋 Executing Phase 7.1: Database Schema...${NC}\n"

claude --print --dangerously-skip-permissions \
  "Please work on Phase 7.1: Database Schema for Subscriptions from projects/DWnews/plans/roadmap.md.

Tasks:
1. Read the phase requirements
2. Create database migration files for subscription tables
3. Update the roadmap to mark Phase 7.1 as complete
4. Provide a summary of what was created

Be concise and focused."

echo -e "\n${GREEN}✅ Task complete${NC}\n"

# Check if working tree is dirty
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo -e "${GREEN}📝 Changes detected. Creating commit...${NC}\n"

    claude --print --dangerously-skip-permissions \
      "Create a git commit for all changes. Use git status and git diff to review, then commit with an appropriate message."

    echo -e "\n${GREEN}✅ Committed${NC}\n"
else
    echo -e "${GREEN}✨ No changes to commit${NC}\n"
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🎉 Test Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
