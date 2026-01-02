#!/bin/bash

# GitHub Actions Deployment Script
# Run this to push all GitHub Actions configurations to your repository

set -e

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║           Deploy GitHub Actions CI/CD to Repository                 ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${YELLOW}Error: Not in a git repository${NC}"
    echo "Please run this script from your repository root"
    exit 1
fi

# Show what will be committed
echo -e "${BLUE}Files to be committed:${NC}"
echo ""
git status --short .github/ GITHUB_ACTIONS_COMPLETE.md 2>/dev/null || true
echo ""

# Confirm
read -p "Do you want to commit and push these files? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Stage files
echo ""
echo -e "${BLUE}Staging GitHub Actions files...${NC}"
git add .github/
git add GITHUB_ACTIONS_COMPLETE.md

# Show staged files
echo ""
echo -e "${GREEN}Staged files:${NC}"
git diff --cached --name-only

# Create commit
echo ""
echo -e "${BLUE}Creating commit...${NC}"
git commit -m "feat: Add comprehensive GitHub Actions CI/CD

- Add backend API testing workflow (39 tests, Python 3.9-3.11)
- Add code quality checks (Black, isort, Flake8, Pylint, Bandit)
- Add CI pipeline orchestration
- Add weekly dependency update automation
- Add comprehensive documentation
- Add pull request template

Features:
✅ Automated testing on every push/PR
✅ Code quality enforcement
✅ Security vulnerability scanning
✅ Weekly dependency audits
✅ Build validation
✅ Multiple Python version testing
✅ Coverage reporting (Codecov ready)

All workflows validated and ready to run.
"

# Get current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Push
echo ""
echo -e "${BLUE}Pushing to origin/${BRANCH}...${NC}"
git push origin "$BRANCH"

# Success
echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ DEPLOYMENT COMPLETE                            ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Next Steps:${NC}"
echo ""
echo "1. Go to your GitHub repository"
echo "2. Click the 'Actions' tab"
echo "3. You should see 4 workflows:"
echo "   • Backend Tests"
echo "   • Code Quality"
echo "   • CI Pipeline"
echo "   • Dependency Updates"
echo ""
echo "4. Trigger a test run:"
echo "   • Make any change to backend code and push, OR"
echo "   • Manually trigger from Actions tab → CI Pipeline → Run workflow"
echo ""
echo "5. Optional: Configure branch protection"
echo "   • Settings → Branches → Add rule for 'main'"
echo "   • Require status checks: Backend Tests (Python 3.11), Build Check"
echo ""
echo "6. Optional: Add status badges to README.md"
echo "   See .github/README.md for badge markdown"
echo ""
echo -e "${GREEN}📚 Documentation:${NC}"
echo "   • .github/README.md - Workflows overview"
echo "   • .github/GITHUB_ACTIONS_SETUP.md - Complete setup guide"
echo "   • .github/WORKFLOWS_SUMMARY.md - Detailed specs"
echo "   • GITHUB_ACTIONS_COMPLETE.md - Summary of everything"
echo ""
echo -e "${GREEN}🎉 Your repository now has enterprise-grade CI/CD!${NC}"
echo ""
