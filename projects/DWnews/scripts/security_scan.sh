#!/bin/bash
# Security Scan Script
# Performs automated security checks on The Daily Worker codebase

set -e

echo "========================================"
echo "The Daily Worker - Security Scan"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

ISSUES_FOUND=0

# Navigate to project root
cd "$(dirname "$0")/.."

echo "Scan 1: Check for Hardcoded Secrets"
echo "------------------------------------"

# Check for common secret patterns
SECRETS_FOUND=0

# API Keys
if grep -r "sk-ant-[a-zA-Z0-9]" --include="*.py" --include="*.js" . 2>/dev/null; then
    echo -e "${RED}✗ Found hardcoded Anthropic API key${NC}"
    SECRETS_FOUND=$((SECRETS_FOUND + 1))
fi

if grep -r "sk-[a-zA-Z0-9]" --include="*.py" --include="*.js" . 2>/dev/null | grep -v "example" | grep -v "SECURITY.md"; then
    echo -e "${YELLOW}⚠ Possible OpenAI API key found${NC}"
    SECRETS_FOUND=$((SECRETS_FOUND + 1))
fi

# AWS/GCP Keys
if grep -r "AKIA[0-9A-Z]{16}" --include="*.py" --include="*.js" --include="*.env" . 2>/dev/null; then
    echo -e "${RED}✗ Found AWS access key${NC}"
    SECRETS_FOUND=$((SECRETS_FOUND + 1))
fi

# Database URLs with credentials
if grep -r "postgresql://.*:.*@" --include="*.py" . 2>/dev/null | grep -v "example"; then
    echo -e "${YELLOW}⚠ Found database URL with credentials${NC}"
    SECRETS_FOUND=$((SECRETS_FOUND + 1))
fi

if [ $SECRETS_FOUND -eq 0 ]; then
    echo -e "${GREEN}✓ No hardcoded secrets found${NC}"
else
    echo -e "${RED}✗ Found $SECRETS_FOUND potential secret(s)${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + SECRETS_FOUND))
fi

echo ""
echo "Scan 2: Check for SQL Injection Risks"
echo "--------------------------------------"

# Check for raw SQL
SQL_RISKS=0

if grep -r "\.execute(.*f\"" --include="*.py" backend/ database/ scripts/ 2>/dev/null; then
    echo -e "${RED}✗ Found f-string in SQL execute (SQL injection risk)${NC}"
    SQL_RISKS=$((SQL_RISKS + 1))
fi

if grep -r "\.execute(.*%.*)" --include="*.py" backend/ database/ scripts/ 2>/dev/null; then
    echo -e "${YELLOW}⚠ Found string formatting in SQL execute${NC}"
    SQL_RISKS=$((SQL_RISKS + 1))
fi

if [ $SQL_RISKS -eq 0 ]; then
    echo -e "${GREEN}✓ No SQL injection risks found${NC}"
else
    echo -e "${RED}✗ Found $SQL_RISKS potential SQL injection risk(s)${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + SQL_RISKS))
fi

echo ""
echo "Scan 3: Check for XSS Risks"
echo "---------------------------"

# Check for dangerous JavaScript
XSS_RISKS=0

if grep -r "innerHTML.*=.*" --include="*.js" frontend/ 2>/dev/null | grep -v "// SAFE" | grep -v "//" | grep -v "template"; then
    echo -e "${YELLOW}⚠ Found innerHTML usage (potential XSS risk)${NC}"
    XSS_RISKS=$((XSS_RISKS + 1))
fi

if grep -r "eval(" --include="*.js" frontend/ 2>/dev/null; then
    echo -e "${RED}✗ Found eval() usage (XSS risk)${NC}"
    XSS_RISKS=$((XSS_RISKS + 1))
fi

if grep -r "dangerouslySetInnerHTML" --include="*.js" --include="*.jsx" frontend/ 2>/dev/null; then
    echo -e "${RED}✗ Found dangerouslySetInnerHTML (XSS risk)${NC}"
    XSS_RISKS=$((XSS_RISKS + 1))
fi

if [ $XSS_RISKS -eq 0 ]; then
    echo -e "${GREEN}✓ No XSS risks found${NC}"
else
    echo -e "${RED}✗ Found $XSS_RISKS potential XSS risk(s)${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + XSS_RISKS))
fi

echo ""
echo "Scan 4: Check .env File Security"
echo "---------------------------------"

if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file exists${NC}"

    # Check if .env is in .gitignore
    if grep -q "^\.env$" .gitignore 2>/dev/null; then
        echo -e "${GREEN}✓ .env is in .gitignore${NC}"
    else
        echo -e "${RED}✗ .env is NOT in .gitignore!${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi

    # Check if .env is committed to git
    if git ls-files --error-unmatch .env 2>/dev/null; then
        echo -e "${RED}✗ .env is committed to git!${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo -e "${GREEN}✓ .env is not committed to git${NC}"
    fi
else
    echo -e "${YELLOW}⚠ .env file not found (expected for fresh clone)${NC}"
fi

if [ -f ".env.example" ]; then
    echo -e "${GREEN}✓ .env.example exists${NC}"

    # Check if .env.example has real secrets
    if grep -q "sk-ant-[a-zA-Z0-9]" .env.example 2>/dev/null; then
        echo -e "${RED}✗ .env.example contains real secrets!${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo -e "${GREEN}✓ .env.example has no real secrets${NC}"
    fi
fi

echo ""
echo "Scan 5: Check Dependencies"
echo "--------------------------"

# Check if pip-audit is available
if command -v pip-audit &> /dev/null; then
    echo "Running pip-audit..."
    if pip-audit -r backend/requirements.txt 2>&1 | grep -i "No known vulnerabilities found"; then
        echo -e "${GREEN}✓ No known vulnerabilities in dependencies${NC}"
    else
        echo -e "${YELLOW}⚠ Vulnerabilities found in dependencies${NC}"
        pip-audit -r backend/requirements.txt
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
else
    echo -e "${YELLOW}⚠ pip-audit not installed (run: pip install pip-audit)${NC}"
fi

echo ""
echo "Scan 6: Check CORS Configuration"
echo "---------------------------------"

# Check for wildcard CORS
if grep -r "allow_origins=\[\".*\*.*\"\]" --include="*.py" backend/ 2>/dev/null; then
    echo -e "${RED}✗ Found wildcard CORS origin (security risk)${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓ No wildcard CORS origins${NC}"
fi

# Check for localhost restriction
if grep -r "localhost" backend/main.py 2>/dev/null | grep -q "allow_origins"; then
    echo -e "${GREEN}✓ CORS restricted to localhost${NC}"
else
    echo -e "${YELLOW}⚠ CORS configuration should be reviewed${NC}"
fi

echo ""
echo "Scan 7: Check Authentication"
echo "-----------------------------"

# Check for plaintext passwords
if grep -r "password.*=.*\".*\"" --include="*.py" backend/ 2>/dev/null | grep -v "hash" | grep -v "#"; then
    echo -e "${RED}✗ Found plaintext password${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓ No plaintext passwords found${NC}"
fi

# Check for password hashing
if grep -r "bcrypt\|argon2\|scrypt" backend/ 2>/dev/null; then
    echo -e "${GREEN}✓ Password hashing implemented${NC}"
else
    echo -e "${RED}✗ No password hashing found${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

echo ""
echo "Scan 8: Check File Permissions"
echo "-------------------------------"

# Check for overly permissive files
if [ -f ".env" ]; then
    PERMS=$(stat -f "%A" .env 2>/dev/null || stat -c "%a" .env 2>/dev/null)
    if [ "$PERMS" == "600" ] || [ "$PERMS" == "400" ]; then
        echo -e "${GREEN}✓ .env has correct permissions ($PERMS)${NC}"
    else
        echo -e "${YELLOW}⚠ .env permissions are $PERMS (should be 600 or 400)${NC}"
    fi
fi

# Check for executable scripts
EXEC_SCRIPTS=$(find . -name "*.sh" -type f -executable 2>/dev/null | wc -l | tr -d ' ')
echo -e "${GREEN}✓ Found $EXEC_SCRIPTS executable scripts${NC}"

echo ""
echo "========================================"
echo "Security Scan Complete"
echo "========================================"
echo ""

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ No security issues found!${NC}"
    echo ""
    echo "Summary:"
    echo "  ✓ No hardcoded secrets"
    echo "  ✓ No SQL injection risks"
    echo "  ✓ No XSS vulnerabilities"
    echo "  ✓ Environment variables secure"
    echo "  ✓ Dependencies checked"
    echo "  ✓ CORS configured correctly"
    echo "  ✓ Authentication secure"
    exit 0
else
    echo -e "${RED}⚠️  Found $ISSUES_FOUND security issue(s)${NC}"
    echo ""
    echo "Please review the issues above and fix them before deploying."
    exit 1
fi
