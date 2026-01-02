# Cloud Security Configuration - DWnews

## Document Information

**Version:** 1.0
**Date:** 2026-01-01
**Project:** The Daily Worker (Project Code: DWnews)
**Status:** Active
**Implementation Priority:** CRITICAL - Must complete before Batch 8 (GCP Deployment)

---

## Executive Summary

This document defines security configuration requirements for the DWnews platform, with emphasis on securing API credentials, cloud infrastructure, and production deployment. The project currently has **UNRESTRICTED** API keys that require immediate scoping before production deployment.

**Critical Issues Identified:**
1. GCP API key (Gemini) has unrestricted permissions - HIGH RISK
2. No secret management strategy defined for production
3. API keys exposed in development environment
4. No access control policies defined for cloud resources
5. No security monitoring or alerting configured

**Target Completion:** Before Batch 8 (GCP Infrastructure Deployment)

---

## 1. API Key Security and Scoping

### 1.1 Current API Credentials Status

The project currently uses the following API credentials:

| API Service | Status | Risk Level | Action Required |
|-------------|--------|------------|-----------------|
| GCP API (Gemini) | UNRESTRICTED | 🔴 CRITICAL | Immediate scoping required |
| Claude API | Active | 🟡 MEDIUM | Implement rate limiting |
| OpenAI API | Active | 🟡 MEDIUM | Implement rate limiting |
| Twitter Bearer Token | Active | 🟢 LOW | Monitor usage |
| Reddit API | Pending approval | 🟢 LOW | Apply restrictions on approval |

### 1.2 GCP API Key Scoping Requirements

**CRITICAL:** The current GCP API key must be scoped before production deployment.

#### Recommended Restrictions

**API Restrictions:**
```yaml
Allowed APIs:
  - Vertex AI API (aiplatform.googleapis.com)
  - Cloud Storage API (storage.googleapis.com)
  - Cloud SQL Admin API (sqladmin.googleapis.com)
  - Cloud Run API (run.googleapis.com)
  - Cloud Logging API (logging.googleapis.com)
  - Cloud Monitoring API (monitoring.googleapis.com)

BLOCKED APIs:
  - Compute Engine API (compute.googleapis.com) - Use service accounts instead
  - IAM API (iam.googleapis.com) - Prevent privilege escalation
  - Billing API (cloudbilling.googleapis.com) - Prevent cost manipulation
  - Cloud Functions API - Not used in this project
  - BigQuery API - Not used in this project
```

**Application Restrictions:**
```yaml
HTTP Referrers:
  - https://dailyworker.com/*
  - https://www.dailyworker.com/*
  - https://admin.dailyworker.com/*

IP Restrictions (Production):
  - GCP Cloud Run IP range (dynamic, use VPC egress)
  - Office/Admin IPs: [CONFIGURE_ADMIN_IPS]
  - BLOCK: 0.0.0.0/0 (no public access)

IP Restrictions (Development):
  - Development team IPs only
  - Temporary whitelist for testing
```

**Quota Restrictions:**
```yaml
Vertex AI (Gemini Image Generation):
  - Max requests per day: 1000
  - Max requests per minute: 10
  - Alert at 80% usage

Cloud Storage:
  - Max requests per day: 10000
  - Max bandwidth: 100 GB/day
  - Alert at 80% usage

Cloud SQL:
  - Max connections: 100
  - Alert at 80% usage
```

#### Implementation Steps

1. **Create New Scoped API Key** (Recommended):
   ```bash
   # In GCP Console or via gcloud CLI
   gcloud alpha services api-keys create \
     --display-name="DWnews Production API Key" \
     --api-target=service=aiplatform.googleapis.com \
     --api-target=service=storage.googleapis.com \
     --api-target=service=sqladmin.googleapis.com \
     --api-target=service=run.googleapis.com \
     --allowed-referrers="https://dailyworker.com/*,https://www.dailyworker.com/*" \
     --project=[PROJECT_ID]
   ```

2. **Rotate Unrestricted Key**:
   - Create new scoped key
   - Update all environments with new key
   - Delete unrestricted key within 24 hours
   - Document rotation in security log

3. **Verify Restrictions**:
   - Test API calls with new key
   - Attempt blocked API calls (should fail)
   - Verify referrer restrictions work
   - Test quota limits

### 1.3 Service Account Strategy (Preferred)

**Replace API keys with service accounts** for production deployment:

**Service Account Architecture:**
```
dailyworker-production@[project].iam.gserviceaccount.com
├── Roles:
│   ├── Vertex AI User (roles/aiplatform.user)
│   ├── Storage Object Creator (roles/storage.objectCreator)
│   ├── Cloud SQL Client (roles/cloudsql.client)
│   └── Logging Writer (roles/logging.logWriter)
├── Bound to: Cloud Run service
└── No exported keys (metadata server authentication)
```

**Benefits over API keys:**
- Automatic credential rotation
- No hardcoded secrets
- Granular IAM permissions
- Audit trail in Cloud Logging
- No accidental exposure risk

**Implementation:**
```bash
# Create service account
gcloud iam service-accounts create dailyworker-production \
  --display-name="DWnews Production Service Account" \
  --project=[PROJECT_ID]

# Grant minimal permissions
gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member="serviceAccount:dailyworker-production@[PROJECT_ID].iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member="serviceAccount:dailyworker-production@[PROJECT_ID].iam.gserviceaccount.com" \
  --role="roles/storage.objectCreator"

# Bind to Cloud Run service
gcloud run deploy dailyworker \
  --service-account=dailyworker-production@[PROJECT_ID].iam.gserviceaccount.com \
  --region=us-central1
```

### 1.4 Third-Party API Security

#### Claude API
```yaml
Configuration:
  - Store in secret manager (not environment variables)
  - Rate limit: 100 requests/minute
  - Cost alert: $50/day threshold
  - Usage monitoring: Daily logs
  - Rotation schedule: Every 90 days
```

#### OpenAI API
```yaml
Configuration:
  - Store in secret manager
  - Rate limit: 100 requests/minute
  - Cost alert: $50/day threshold
  - Usage monitoring: Daily logs
  - Rotation schedule: Every 90 days
  - Organization ID: Restrict to DWnews org only
```

#### Twitter Bearer Token
```yaml
Configuration:
  - Read-only permissions (no tweet posting until post-MVP)
  - Store in secret manager
  - Rate limit: Twitter's free tier limits
  - Usage monitoring: Track API calls
  - Rotation schedule: Every 180 days
```

#### Reddit API
```yaml
Configuration:
  - Read-only permissions
  - Store in secret manager
  - Rate limit: 60 requests/minute (Reddit limit)
  - Usage monitoring: Track subreddit scraping
  - Rotation schedule: Every 180 days
```

---

## 2. Secret Management Strategy

### 2.1 Development Environment

**Current State:** API keys stored in `.env.local` (NOT committed to git)

**Required Configuration:**
```bash
# .env.local (local development only)
GCP_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
CLAUDE_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
TWITTER_BEARER_TOKEN=AAAA...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
DATABASE_URL=postgresql://localhost:5432/dailyworker_dev
```

**Security Controls:**
- `.env.local` in `.gitignore` (VERIFY)
- Service account keys stored outside project directory
- Separate keys for dev/staging/production
- Never commit secrets to version control
- Use git-secrets or similar to prevent accidental commits

### 2.2 Production Environment (GCP Secret Manager)

**Mandatory:** Use GCP Secret Manager for all production secrets.

**Implementation:**
```bash
# Create secrets
echo -n "your-claude-api-key" | gcloud secrets create claude-api-key \
  --data-file=- \
  --replication-policy=automatic \
  --project=[PROJECT_ID]

echo -n "your-openai-api-key" | gcloud secrets create openai-api-key \
  --data-file=- \
  --replication-policy=automatic \
  --project=[PROJECT_ID]

# Grant access to Cloud Run service account
gcloud secrets add-iam-policy-binding claude-api-key \
  --member="serviceAccount:dailyworker-production@[PROJECT_ID].iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Access in application code
from google.cloud import secretmanager

def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

claude_key = get_secret("claude-api-key")
```

**Secret Manager Configuration:**
```yaml
Secrets to Store:
  - claude-api-key
  - openai-api-key
  - twitter-bearer-token
  - reddit-client-id
  - reddit-client-secret
  - database-password
  - jwt-secret (for admin authentication)
  - session-secret

Access Control:
  - Production service account: secretAccessor role
  - Admin users: secretVersionManager role (for rotation)
  - CI/CD pipeline: secretAccessor role (deployment only)

Rotation Policy:
  - Critical secrets (API keys): 90 days
  - Database credentials: 180 days
  - Session secrets: 365 days
  - Automatic rotation reminders via monitoring alerts
```

### 2.3 Environment Separation

**Strict separation between environments:**

| Environment | GCP Project | Database | Service Account | API Keys |
|-------------|-------------|----------|-----------------|----------|
| Development | dailyworker-dev | Local PostgreSQL | dev-service-account | Development keys |
| Staging | dailyworker-staging | Cloud SQL (dev tier) | staging-service-account | Staging keys |
| Production | dailyworker-prod | Cloud SQL (production) | prod-service-account | Production keys |

**Key Principle:** Never use production credentials in development or staging.

---

## 3. Access Control and IAM Configuration

### 3.1 GCP IAM Roles and Policies

**Principle of Least Privilege:** Grant minimum permissions required for each role.

#### Production IAM Structure

```yaml
Project: dailyworker-prod

Service Accounts:
  dailyworker-production@:
    roles:
      - roles/aiplatform.user (Vertex AI access)
      - roles/storage.objectCreator (upload images)
      - roles/cloudsql.client (database connection)
      - roles/logging.logWriter (application logs)
      - roles/monitoring.metricWriter (custom metrics)
      - roles/secretmanager.secretAccessor (read secrets)
    bound_to: Cloud Run service

  dailyworker-ci-cd@:
    roles:
      - roles/run.developer (deploy Cloud Run)
      - roles/storage.admin (manage Cloud Storage)
      - roles/cloudbuild.builds.editor (CI/CD builds)
      - roles/secretmanager.secretAccessor (read secrets for deployment)
    bound_to: GitHub Actions

  dailyworker-backup@:
    roles:
      - roles/cloudsql.admin (database backups)
      - roles/storage.admin (backup storage)
    bound_to: Scheduled backup jobs

Human Users:
  admin@dailyworker.com:
    roles:
      - roles/owner (full project access)
    mfa_required: true

  editor@dailyworker.com:
    roles:
      - roles/cloudsql.client (database access)
      - roles/storage.objectViewer (view images)
      - roles/logging.viewer (view logs)
      - roles/monitoring.viewer (view metrics)
    mfa_required: true

  developer@dailyworker.com:
    roles:
      - roles/cloudsql.client (database access)
      - roles/run.developer (deploy services)
      - roles/storage.admin (manage storage)
      - roles/logging.viewer (view logs)
    mfa_required: true
```

#### IAM Best Practices

1. **Enable Multi-Factor Authentication (MFA):**
   - Required for all human user accounts
   - Use Google Authenticator or hardware security keys
   - Enforce via GCP Organization Policies

2. **Use Groups for Role Assignment:**
   ```yaml
   Groups:
     dwn-admins@dailyworker.com:
       - admin@dailyworker.com
       roles: roles/owner

     dwn-editors@dailyworker.com:
       - editor1@dailyworker.com
       - editor2@dailyworker.com
       roles: roles/cloudsql.client, roles/storage.objectViewer

     dwn-developers@dailyworker.com:
       - dev1@dailyworker.com
       - dev2@dailyworker.com
       roles: roles/run.developer, roles/logging.viewer
   ```

3. **Audit IAM Changes:**
   - Enable Cloud Audit Logs (Admin Activity)
   - Alert on IAM policy changes
   - Monthly review of permissions

4. **Remove Unused Accounts:**
   - Quarterly audit of user accounts
   - Disable accounts inactive for 90 days
   - Remove accounts inactive for 180 days

### 3.2 Database Access Control

**PostgreSQL (Cloud SQL) Security:**

```sql
-- Production database users
CREATE USER dailyworker_app WITH PASSWORD '[SECRET_MANAGER]';
GRANT CONNECT ON DATABASE dailyworker_prod TO dailyworker_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO dailyworker_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dailyworker_app;

-- Read-only user for reporting
CREATE USER dailyworker_readonly WITH PASSWORD '[SECRET_MANAGER]';
GRANT CONNECT ON DATABASE dailyworker_prod TO dailyworker_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dailyworker_readonly;

-- Admin user (for migrations and schema changes)
CREATE USER dailyworker_admin WITH PASSWORD '[SECRET_MANAGER]';
GRANT ALL PRIVILEGES ON DATABASE dailyworker_prod TO dailyworker_admin;

-- Revoke public access
REVOKE ALL ON SCHEMA public FROM PUBLIC;
```

**Cloud SQL IAM Authentication (Recommended):**
```bash
# Enable Cloud SQL IAM authentication
gcloud sql instances patch dailyworker-prod \
  --database-flags=cloudsql_iam_authentication=on

# Grant IAM login to service account
gcloud sql users create dailyworker-production@[PROJECT_ID].iam \
  --instance=dailyworker-prod \
  --type=CLOUD_IAM_SERVICE_ACCOUNT

# Connection string in application
postgresql://dailyworker-production@[PROJECT_ID].iam:@/dailyworker_prod?host=/cloudsql/[CONNECTION_NAME]
```

**Cloud SQL Access Controls:**
```yaml
Authorized Networks: NONE (use Cloud SQL Proxy only)
SSL/TLS: Required (enforce_ssl=on)
Public IP: Disabled (private IP only)
Backup: Automated daily backups (7-day retention)
Point-in-Time Recovery: Enabled
High Availability: Enabled (if budget allows)
```

---

## 4. Network Security Requirements

### 4.1 VPC Configuration

**Virtual Private Cloud (VPC) Design:**

```yaml
VPC: dailyworker-vpc
Region: us-central1
Subnets:
  - webapp-subnet:
      IP Range: 10.0.1.0/24
      Purpose: Cloud Run services

  - database-subnet:
      IP Range: 10.0.2.0/24
      Purpose: Cloud SQL private IP

  - admin-subnet:
      IP Range: 10.0.3.0/24
      Purpose: Admin access, bastion hosts
```

**VPC Peering:**
- Cloud SQL Private IP connected to webapp-subnet
- No public database access
- Use Cloud SQL Proxy for local development

### 4.2 Firewall Rules

**Production Firewall Configuration:**

```yaml
Ingress Rules:
  - allow-https:
      priority: 1000
      direction: INGRESS
      source: 0.0.0.0/0
      ports: 443
      target: Cloud Run services

  - allow-health-checks:
      priority: 1010
      direction: INGRESS
      source: 35.191.0.0/16, 130.211.0.0/22 (GCP health check ranges)
      ports: 443
      target: Cloud Run services

  - allow-admin-ssh:
      priority: 1020
      direction: INGRESS
      source: [ADMIN_IP_RANGES]
      ports: 22
      target: bastion-host (if used)

  - deny-all-ingress:
      priority: 65535
      direction: INGRESS
      source: 0.0.0.0/0
      action: DENY

Egress Rules:
  - allow-database:
      priority: 1000
      direction: EGRESS
      destination: 10.0.2.0/24 (database-subnet)
      ports: 5432

  - allow-apis:
      priority: 1010
      direction: EGRESS
      destination: 0.0.0.0/0
      ports: 443
      description: Allow HTTPS to external APIs (Claude, OpenAI, Twitter, etc.)

  - allow-dns:
      priority: 1020
      direction: EGRESS
      destination: 0.0.0.0/0
      ports: 53

  - deny-all-egress:
      priority: 65535
      direction: EGRESS
      destination: 0.0.0.0/0
      action: DENY
```

### 4.3 DDoS Protection

**Cloud Armor Configuration:**

```yaml
Cloud Armor Policy: dailyworker-protection

Rate Limiting Rules:
  - global-rate-limit:
      requests_per_ip: 100 requests/minute
      action: throttle (return 429)

  - api-rate-limit:
      path: /api/*
      requests_per_ip: 50 requests/minute
      action: throttle

  - admin-rate-limit:
      path: /admin/*
      requests_per_ip: 20 requests/minute
      action: throttle

Geographic Restrictions:
  - allow-regions: US, CA, UK, AU, EU
  - block-regions: Known high-abuse countries (configurable)

Bot Protection:
  - Challenge suspicious traffic
  - Block known bad bots
  - Allow verified search engine bots (Googlebot, Bingbot)

OWASP Top 10 Protection:
  - SQL injection detection: BLOCK
  - XSS detection: BLOCK
  - LFI/RFI detection: BLOCK
  - Scanner detection: BLOCK
```

### 4.4 SSL/TLS Configuration

**Certificate Management:**
```yaml
Certificate: dailyworker.com
Provider: Google-managed SSL certificate (automatic renewal)
Protocols: TLS 1.2, TLS 1.3 only
Cipher Suites: Strong ciphers only (no weak/export ciphers)
HSTS: Enabled (max-age=31536000; includeSubDomains; preload)
Certificate Transparency: Enabled
```

**HTTPS Enforcement:**
- Automatic HTTP → HTTPS redirect
- HSTS header on all responses
- No mixed content (all resources via HTTPS)

---

## 5. Monitoring and Alerting

### 5.1 Security Monitoring

**Cloud Logging Configuration:**

```yaml
Log Sinks:
  - security-logs:
      destination: Cloud Storage bucket (security-logs-bucket)
      filter: |
        severity >= ERROR OR
        protoPayload.methodName =~ ".*iam.*" OR
        protoPayload.methodName =~ ".*sql.*" OR
        resource.type = "cloud_run_revision"
      retention: 365 days

  - audit-logs:
      destination: BigQuery (audit_logs dataset)
      filter: |
        logName =~ ".*cloudaudit.googleapis.com.*"
      retention: 1095 days (3 years)
```

**Key Logs to Monitor:**
1. **Admin Activity Logs:** All IAM changes, resource creation/deletion
2. **Data Access Logs:** Database queries, sensitive data access
3. **Cloud Run Logs:** Application errors, API failures
4. **VPC Flow Logs:** Network traffic patterns, anomalies
5. **Cloud Storage Access Logs:** Image uploads, unauthorized access attempts

### 5.2 Security Alerts

**Alert Policies:**

```yaml
Critical Alerts (Immediate Response):
  - unauthorized-iam-change:
      condition: IAM policy modified by non-admin user
      notification: Email + SMS to admin

  - api-key-usage-spike:
      condition: API requests > 200% of baseline
      notification: Email to admin

  - database-connection-failure:
      condition: Cloud SQL connection errors > 10 in 5 minutes
      notification: Email + PagerDuty

  - secret-access-anomaly:
      condition: Secret accessed from unexpected service account
      notification: Email + SMS to admin

  - failed-login-attempts:
      condition: >5 failed admin logins in 10 minutes
      notification: Email to admin

High Priority Alerts (1-hour response):
  - cost-threshold-exceeded:
      condition: Daily GCP spend > $100
      notification: Email to admin

  - api-quota-exhausted:
      condition: Gemini API quota usage > 80%
      notification: Email to developer

  - ssl-certificate-expiry:
      condition: Certificate expiring in < 30 days
      notification: Email to admin

  - backup-failure:
      condition: Database backup failed
      notification: Email to admin

Medium Priority Alerts (4-hour response):
  - high-error-rate:
      condition: Application error rate > 5% for 15 minutes
      notification: Email to developer

  - slow-response-time:
      condition: P95 latency > 3 seconds for 15 minutes
      notification: Email to developer
```

**Alerting Channels:**
```yaml
Email:
  - admin@dailyworker.com (all critical alerts)
  - dev@dailyworker.com (high/medium alerts)

SMS:
  - Admin phone (critical alerts only)

PagerDuty:
  - On-call rotation (critical infrastructure alerts)

Slack:
  - #dwn-security channel (all security alerts)
  - #dwn-ops channel (infrastructure alerts)
```

### 5.3 Intrusion Detection

**Cloud IDS (Intrusion Detection System):**

```yaml
Configuration:
  - Enable: Cloud IDS for VPC network
  - Inspection: All traffic to/from database subnet
  - Threat Intelligence: Google Cloud Threat Intelligence
  - Alerts:
      - SQL injection attempts
      - Port scanning
      - Malware downloads
      - Command and control communication
      - Data exfiltration attempts
```

**Security Command Center (SCC):**
```yaml
Enable: Standard tier (free)
Features:
  - Asset discovery and inventory
  - Vulnerability scanning
  - Misonfiguration detection
  - Threat detection
  - Compliance monitoring

Scans:
  - Web Security Scanner: Weekly scans of dailyworker.com
  - Container Analysis: Scan Cloud Run container images
  - Findings: Auto-remediate critical findings
```

---

## 6. Compliance and Audit Requirements

### 6.1 Data Privacy Compliance

**GDPR Compliance (if EU users):**
```yaml
Requirements:
  - Data minimization: Only store necessary user data
  - Right to erasure: Implement user data deletion
  - Data portability: Export user data on request
  - Consent management: Cookie consent banner
  - Privacy policy: Clear and accessible
  - Data breach notification: <72 hour reporting

Implementation:
  - No PII storage for anonymous users
  - IP geolocation: Do not store IP addresses
  - User accounts: Email + password only (minimal data)
  - Cookie consent: Implement banner with opt-in/opt-out
```

**CCPA Compliance (California users):**
```yaml
Requirements:
  - Do Not Sell My Personal Information
  - Right to know what data is collected
  - Right to delete personal data
  - Opt-out of data sale

Implementation:
  - No data selling (not applicable)
  - Privacy policy with CCPA disclosures
  - User data deletion endpoint
```

### 6.2 Audit Logging

**Compliance Audit Requirements:**

```yaml
Logs to Retain:
  - Admin Activity: 3 years
  - Data Access: 1 year
  - Security Events: 3 years
  - Application Logs: 90 days
  - Access Logs: 1 year

Audit Trail:
  - Who: User/service account identifier
  - What: Action performed (create, read, update, delete)
  - When: Timestamp (UTC)
  - Where: Source IP, region, resource
  - Why: Request context, API call details

Immutability:
  - Store audit logs in append-only Cloud Storage bucket
  - Enable Object Versioning
  - Set retention policy (cannot be deleted before expiry)
  - Use Customer-Managed Encryption Keys (CMEK) for sensitive logs
```

**Audit Schedule:**
```yaml
Daily:
  - Review security alert summary
  - Check failed authentication attempts
  - Verify backup completion

Weekly:
  - Review IAM changes
  - Check API usage anomalies
  - Verify cost trends

Monthly:
  - Full security review
  - Review user access lists
  - Check for unused service accounts
  - Update security documentation

Quarterly:
  - Penetration testing (if budget allows)
  - Compliance assessment
  - Rotate non-critical secrets
  - Review and update security policies

Annually:
  - Full security audit
  - Disaster recovery testing
  - Rotate all secrets
  - Review and update compliance requirements
```

### 6.3 Compliance Monitoring

**Automated Compliance Checks:**

```yaml
GCP Organization Policies:
  - Restrict public IP allocation on Cloud SQL
  - Require HTTPS load balancing
  - Restrict VM external IP attachment
  - Require OS Login for Compute Engine
  - Enforce uniform bucket-level access on Cloud Storage
  - Require service account key management

Config Connector Policies:
  - Enforce encryption at rest for all resources
  - Require VPC Service Controls for sensitive APIs
  - Enforce Cloud Armor on all load balancers
  - Require Private Google Access for VPC subnets

Forseti Security:
  - Install Forseti for GCP policy enforcement (if budget allows)
  - Scan for policy violations hourly
  - Auto-remediate or alert on violations
```

---

## 7. Application Security

### 7.1 Authentication and Authorization

**Admin Panel Security:**

```yaml
Authentication:
  - Method: JWT-based authentication
  - Password Policy:
      - Minimum 12 characters
      - Require: uppercase, lowercase, number, special character
      - No common passwords (use zxcvbn library)
      - Bcrypt hashing (cost factor: 12)
  - Session Management:
      - Session timeout: 30 minutes inactivity
      - Absolute timeout: 8 hours
      - Secure cookies (httpOnly, secure, sameSite=strict)
  - Multi-Factor Authentication:
      - TOTP (Google Authenticator, Authy)
      - Backup codes (encrypted, one-time use)
      - Required for admin role

Authorization:
  - Role-Based Access Control (RBAC):
      - Admin: Full access
      - Editor: Article approval, editorial queue
      - Viewer: Read-only access to published content
  - API Authorization:
      - JWT tokens with role claims
      - Token expiry: 1 hour
      - Refresh tokens: 7 days
```

**API Security:**
```yaml
Input Validation:
  - Sanitize all user inputs
  - Validate data types, lengths, formats
  - Use parameterized queries (prevent SQL injection)
  - Escape HTML output (prevent XSS)

Rate Limiting:
  - Public API: 100 requests/minute per IP
  - Admin API: 50 requests/minute per user
  - Image upload: 10 requests/hour per user
  - Implement using Redis-based rate limiter

CORS Policy:
  - Allowed origins: https://dailyworker.com, https://www.dailyworker.com
  - Allowed methods: GET, POST, PUT, DELETE
  - Allowed headers: Content-Type, Authorization
  - Credentials: true
  - Max age: 3600 seconds

Content Security Policy (CSP):
  default-src 'self';
  script-src 'self' 'unsafe-inline' https://cdn.cloudflare.com;
  style-src 'self' 'unsafe-inline';
  img-src 'self' https://storage.googleapis.com https://images.unsplash.com;
  font-src 'self' https://fonts.googleapis.com;
  connect-src 'self' https://api.dailyworker.com;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
```

### 7.2 Dependency Security

**Dependency Scanning:**
```yaml
Tools:
  - npm audit (Node.js)
  - pip-audit (Python)
  - Dependabot (GitHub)
  - Snyk (optional, if budget allows)

Schedule:
  - Run on every PR (CI/CD pipeline)
  - Weekly automated scans
  - Alert on critical/high vulnerabilities

Remediation:
  - Critical vulnerabilities: Patch within 24 hours
  - High vulnerabilities: Patch within 7 days
  - Medium vulnerabilities: Patch within 30 days
  - Low vulnerabilities: Review quarterly
```

**Supply Chain Security:**
```yaml
- Use lock files (package-lock.json, requirements.txt)
- Verify package signatures where available
- Pin dependency versions (no floating versions)
- Review dependencies before adding new ones
- Use npm ci / pip install --require-hashes in production
- Scan container images for vulnerabilities
```

### 7.3 Container Security

**Cloud Run Container Hardening:**

```dockerfile
# Use minimal base images
FROM node:20-alpine AS base  # Alpine for minimal attack surface

# Run as non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs

# Copy only necessary files
COPY --chown=nodejs:nodejs package*.json ./
RUN npm ci --only=production

# Read-only filesystem (where possible)
COPY --chown=nodejs:nodejs --chmod=555 ./src ./src
```

**Container Image Scanning:**
```yaml
- Scan on build: Integrate with Google Container Analysis
- Scan on deploy: Block deployment if critical vulnerabilities found
- Continuous scanning: Daily scans of running images
- Vulnerability database: Use Google's vulnerability feed
```

---

## 8. Incident Response Plan

### 8.1 Security Incident Response

**Incident Severity Levels:**

| Severity | Definition | Response Time | Escalation |
|----------|------------|---------------|------------|
| P0 - Critical | Data breach, production outage, active attack | 15 minutes | Immediate admin notification |
| P1 - High | Security vulnerability exploited, API key compromised | 1 hour | Admin + developer notification |
| P2 - Medium | Suspected intrusion attempt, config error | 4 hours | Developer notification |
| P3 - Low | Failed login attempts, minor config issue | 24 hours | Log review |

**Incident Response Workflow:**

```yaml
Detection:
  - Automated alerts (Cloud Monitoring, SCC)
  - Manual discovery (logs, user reports)
  - Third-party notification (Google, security researcher)

Triage:
  - Assess severity (P0-P3)
  - Identify affected systems
  - Determine scope of impact
  - Assign incident commander

Containment:
  - Isolate affected resources
  - Revoke compromised credentials
  - Enable enhanced monitoring
  - Preserve evidence (logs, snapshots)

Eradication:
  - Remove malicious code/access
  - Patch vulnerabilities
  - Reset credentials
  - Apply security updates

Recovery:
  - Restore from clean backups
  - Verify system integrity
  - Re-enable services
  - Monitor for reinfection

Post-Incident:
  - Document timeline and actions
  - Root cause analysis
  - Update security policies
  - Implement preventive measures
  - Notify affected parties (if required)
```

### 8.2 API Key Compromise Response

**If GCP API Key Compromised:**

```yaml
Immediate Actions (within 15 minutes):
  1. Revoke compromised key in GCP Console
  2. Generate new scoped API key
  3. Update Secret Manager with new key
  4. Deploy new key to Cloud Run (automated rollout)
  5. Monitor for unusual API usage

Investigation (within 1 hour):
  1. Review Cloud Audit Logs for unauthorized API calls
  2. Check billing for unexpected charges
  3. Identify how key was compromised (git history, logs, etc.)
  4. Assess scope of data accessed or modified

Remediation:
  1. Rotate all related secrets (Claude, OpenAI, etc.)
  2. Review and update access controls
  3. Implement additional monitoring
  4. Document incident and lessons learned
```

**If Database Credentials Compromised:**

```yaml
Immediate Actions (within 15 minutes):
  1. Change database password via Secret Manager
  2. Restart Cloud Run services to pick up new password
  3. Review database logs for unauthorized queries
  4. Check for data exfiltration

Investigation:
  1. Identify compromised queries (SELECT on sensitive tables)
  2. Check for data modification (UPDATE, DELETE)
  3. Determine source of compromise
  4. Assess regulatory notification requirements (GDPR, CCPA)

Remediation:
  1. Migrate to Cloud SQL IAM authentication (remove passwords)
  2. Enable Cloud SQL Query Insights for ongoing monitoring
  3. Implement database activity monitoring
  4. Notify affected users if PII accessed
```

---

## 9. Disaster Recovery and Business Continuity

### 9.1 Backup Strategy

**Database Backups:**
```yaml
Cloud SQL Automated Backups:
  - Frequency: Daily at 3 AM UTC
  - Retention: 7 days
  - Backup window: 1-hour window (low traffic period)
  - Binary logging: Enabled (for point-in-time recovery)
  - Encryption: Google-managed keys

On-Demand Backups:
  - Before major deployments
  - Before schema migrations
  - Retention: 30 days

Testing:
  - Monthly backup restoration test
  - Document recovery time objective (RTO): <1 hour
  - Document recovery point objective (RPO): <24 hours
```

**Cloud Storage Backups:**
```yaml
Object Versioning:
  - Enable on all buckets
  - Retain 30 versions per object
  - Lifecycle: Delete versions older than 90 days

Image Backups:
  - Cross-region replication to us-east1
  - Retention: Indefinite (unless deleted by admin)
  - Backup frequency: Real-time (via replication)
```

**Application Code Backups:**
```yaml
- Git repository: GitHub (primary)
- Docker images: Google Container Registry (automated)
- Infrastructure as Code: Terraform state in Cloud Storage
- Retention: Indefinite (version controlled)
```

### 9.2 Disaster Recovery Plan

**Disaster Scenarios:**

| Scenario | Impact | Recovery Strategy | RTO | RPO |
|----------|--------|-------------------|-----|-----|
| Database failure | Cannot publish articles | Restore from automated backup | 1 hour | 24 hours |
| Cloud Run outage | Website down | Redeploy to different region | 2 hours | 0 (stateless app) |
| API key compromised | Image generation fails | Rotate key, use fallback images | 15 minutes | 0 |
| Cloud Storage deletion | Missing images | Restore from versioned objects | 1 hour | 0 |
| Full region outage | Complete service outage | Failover to multi-region setup | 4 hours | 24 hours |

**Recovery Procedures:**

```yaml
Database Recovery:
  1. Identify latest good backup (pre-incident)
  2. Create new Cloud SQL instance
  3. Restore backup to new instance
  4. Update Cloud Run connection string
  5. Verify data integrity
  6. Redirect traffic to new instance
  7. Monitor for issues

Application Recovery:
  1. Identify last known good container image
  2. Deploy to Cloud Run in backup region
  3. Update DNS to point to new region
  4. Verify functionality
  5. Monitor logs and metrics

Complete Region Failover:
  1. Deploy Cloud Run to us-east1 (backup region)
  2. Restore database in us-east1
  3. Update DNS records (30-minute TTL)
  4. Enable Cross-Region Load Balancer
  5. Verify traffic routing
  6. Monitor performance
```

---

## 10. Implementation Checklist

### 10.1 Pre-Production Security Checklist

**CRITICAL - Must Complete Before Batch 8:**

```yaml
API Key Security:
  - [ ] Create new scoped GCP API key
  - [ ] Restrict to required APIs only (Vertex AI, Cloud Storage, Cloud SQL, Cloud Run)
  - [ ] Add HTTP referrer restrictions (dailyworker.com)
  - [ ] Set quota limits (1000 requests/day)
  - [ ] Rotate unrestricted key
  - [ ] Document key restrictions in security log

Service Account Setup:
  - [ ] Create production service account
  - [ ] Grant minimal IAM roles (aiplatform.user, storage.objectCreator, cloudsql.client)
  - [ ] Bind to Cloud Run service
  - [ ] Test authentication from Cloud Run
  - [ ] Delete any exported service account keys

Secret Management:
  - [ ] Enable Secret Manager API
  - [ ] Create secrets for all API keys
  - [ ] Create secrets for database credentials
  - [ ] Grant service account secretAccessor role
  - [ ] Update application to read from Secret Manager
  - [ ] Verify .env.local not committed to git

IAM Configuration:
  - [ ] Create IAM groups (admins, editors, developers)
  - [ ] Assign users to appropriate groups
  - [ ] Grant roles to groups (not individual users)
  - [ ] Enable MFA for all human accounts
  - [ ] Remove unused service accounts
  - [ ] Document IAM structure

Network Security:
  - [ ] Create VPC with private subnets
  - [ ] Enable Cloud SQL Private IP
  - [ ] Configure firewall rules (deny-all default)
  - [ ] Enable Cloud Armor on load balancer
  - [ ] Configure rate limiting policies
  - [ ] Test firewall rules (attempt blocked access)

Database Security:
  - [ ] Disable public IP on Cloud SQL
  - [ ] Enable SSL/TLS enforcement
  - [ ] Create database users with minimal permissions
  - [ ] Enable automated backups (daily)
  - [ ] Enable point-in-time recovery
  - [ ] Test backup restoration

Monitoring and Alerting:
  - [ ] Create log sinks (security logs, audit logs)
  - [ ] Configure alert policies (IAM changes, API spikes, cost thresholds)
  - [ ] Set up notification channels (email, SMS)
  - [ ] Enable Security Command Center
  - [ ] Test alerts (trigger test alerts)
  - [ ] Document incident response procedures

Application Security:
  - [ ] Implement JWT authentication for admin panel
  - [ ] Enable MFA for admin accounts
  - [ ] Configure Content Security Policy headers
  - [ ] Implement rate limiting on APIs
  - [ ] Set secure cookie flags (httpOnly, secure, sameSite)
  - [ ] Run dependency vulnerability scan (npm audit / pip-audit)
  - [ ] Fix critical and high severity vulnerabilities

Container Security:
  - [ ] Use minimal base image (Alpine Linux)
  - [ ] Run as non-root user
  - [ ] Scan container image for vulnerabilities
  - [ ] Enable Container Analysis in GCP
  - [ ] Set read-only filesystem where possible
  - [ ] Remove unnecessary packages and tools

Compliance:
  - [ ] Create privacy policy (GDPR, CCPA)
  - [ ] Implement cookie consent banner
  - [ ] Enable audit logging (3-year retention)
  - [ ] Set up log retention policies
  - [ ] Document data handling procedures
  - [ ] Verify no PII storage for anonymous users

Testing:
  - [ ] Penetration test admin panel
  - [ ] Test authentication bypass attempts
  - [ ] Test SQL injection on all inputs
  - [ ] Test XSS on article body and comments
  - [ ] Test CSRF protection
  - [ ] Verify rate limiting works
  - [ ] Test API key restrictions (attempt blocked API calls)

Documentation:
  - [ ] Document all API keys and their restrictions
  - [ ] Document IAM structure and roles
  - [ ] Document incident response procedures
  - [ ] Document backup and recovery procedures
  - [ ] Create runbook for common security scenarios
  - [ ] Update requirements.md with security specifications
```

### 10.2 Post-Production Security Checklist

**First 30 Days After Launch:**

```yaml
Week 1:
  - [ ] Monitor logs daily for security events
  - [ ] Review API usage for anomalies
  - [ ] Check for failed authentication attempts
  - [ ] Verify backups are running successfully
  - [ ] Test alert notifications

Week 2:
  - [ ] First backup restoration test
  - [ ] Review IAM access logs
  - [ ] Check for unused service accounts
  - [ ] Review cost reports for billing anomalies
  - [ ] Update security documentation

Week 3:
  - [ ] First security audit
  - [ ] Review and tune alert thresholds
  - [ ] Check for new vulnerabilities in dependencies
  - [ ] Verify rate limiting effectiveness
  - [ ] Test incident response procedures

Week 4:
  - [ ] Quarterly secret rotation (if due)
  - [ ] Review and update firewall rules
  - [ ] Penetration test (if budget allows)
  - [ ] Document lessons learned
  - [ ] Plan security improvements
```

---

## 11. Cost Estimates

### 11.1 Security Infrastructure Costs

**Monthly Recurring Costs:**

| Service | Purpose | Estimated Cost |
|---------|---------|----------------|
| Cloud Armor | DDoS protection, rate limiting | $0-50/month |
| Secret Manager | API key storage (6 secrets × 2 versions) | $0.36/month |
| Cloud Logging | Security logs (50GB/month free tier) | $0/month |
| Cloud Monitoring | Metrics and alerting | $0/month (free tier) |
| Cloud SQL Backups | Automated backups (7 days) | $0-5/month |
| VPC Flow Logs | Network monitoring | $0-10/month |
| Security Command Center | Vulnerability scanning (standard tier) | $0/month |
| SSL Certificates | Google-managed certificates | $0/month |
| **Total** | | **$0-65/month** |

**One-Time Setup Costs:**

| Item | Cost |
|------|------|
| Security audit (optional) | $0-1,000 |
| Penetration testing (optional) | $0-2,000 |
| Security training | $0 (free resources) |
| **Total** | **$0-3,000** |

**Cost Optimization Tips:**
- Use free tier services where possible (Cloud Logging, Cloud Monitoring)
- Start with standard tier Security Command Center (free)
- Use Google-managed SSL certificates (free)
- Implement Cloud Armor only on production (not dev/staging)
- Use automated backups instead of continuous replication initially

---

## 12. Security Best Practices Summary

### 12.1 Golden Rules

1. **Principle of Least Privilege:** Grant minimum permissions required for each role
2. **Defense in Depth:** Multiple layers of security (network, application, data)
3. **Assume Breach:** Plan for compromise, not just prevention
4. **Encrypt Everything:** Data at rest, data in transit, backups
5. **Automate Security:** Automated scanning, alerting, remediation
6. **Monitor Continuously:** Real-time security monitoring and alerting
7. **Test Regularly:** Backups, incident response, disaster recovery
8. **Document Everything:** Security configurations, procedures, incidents
9. **Rotate Secrets:** Regular rotation schedule for all credentials
10. **Patch Quickly:** Critical vulnerabilities within 24 hours

### 12.2 Quick Reference

**Emergency Contacts:**
- GCP Support: https://console.cloud.google.com/support
- Security Incidents: security@dailyworker.com
- On-Call Admin: [PHONE_NUMBER]

**Critical Links:**
- GCP Console: https://console.cloud.google.com
- Secret Manager: https://console.cloud.google.com/security/secret-manager
- Cloud Logging: https://console.cloud.google.com/logs
- Security Command Center: https://console.cloud.google.com/security/command-center

**Key Commands:**
```bash
# Revoke API key
gcloud services api-keys delete [KEY_ID] --project=[PROJECT_ID]

# Rotate database password
gcloud secrets versions add database-password --data-file=/path/to/new/password

# Review IAM permissions
gcloud projects get-iam-policy [PROJECT_ID]

# View recent security logs
gcloud logging read "severity>=ERROR" --limit=50 --format=json
```

---

## 13. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-01 | Project Manager | Initial security configuration document. Comprehensive security requirements for pre-production implementation. Covers: API key scoping (GCP, Claude, OpenAI, Twitter, Reddit), secret management strategy (dev + production), IAM configuration, network security, monitoring/alerting, compliance (GDPR/CCPA), incident response, disaster recovery, implementation checklist (pre/post production), cost estimates. Critical focus on scoping unrestricted GCP API key before Batch 8 deployment. |

---

**END OF DOCUMENT**

---

## Next Steps

1. **Immediate (This Week):**
   - Review this document with development team
   - Create new scoped GCP API key
   - Set up Secret Manager
   - Rotate unrestricted API key

2. **Before Batch 8 (GCP Deployment):**
   - Complete pre-production security checklist
   - Set up service accounts with minimal permissions
   - Configure VPC and firewall rules
   - Enable monitoring and alerting
   - Test backup and recovery procedures

3. **After Launch:**
   - Monitor security logs daily (first week)
   - Conduct weekly security reviews (first month)
   - Perform backup restoration test (monthly)
   - Rotate secrets per schedule
   - Update security documentation

**Document Owner:** Project Manager
**Review Schedule:** Monthly (or after security incidents)
**Next Review Date:** 2026-02-01
