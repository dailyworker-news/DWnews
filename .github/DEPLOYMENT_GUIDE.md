# Deployment Guide - The Daily Worker

## Overview

This guide covers the deployment process for The Daily Worker to Google Cloud Platform (GCP) using GitHub Actions.

**Deployment Architecture:**
- **Staging Environment:** Auto-deploys from `develop` branch
- **Production Environment:** Manual deployment with approval and gradual rollout
- **Infrastructure:** GCP Cloud Run (serverless containers)
- **Database:** GCP Cloud SQL (PostgreSQL)
- **Secrets:** GCP Secret Manager
- **Monitoring:** GCP Cloud Monitoring + Logging

---

## Prerequisites

### 1. GCP Project Setup

Create separate GCP projects for staging and production:

```bash
# Create projects
gcloud projects create dailyworker-staging --name="Daily Worker Staging"
gcloud projects create dailyworker-prod --name="Daily Worker Production"

# Enable required APIs
for PROJECT in dailyworker-staging dailyworker-prod; do
  gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    sqladmin.googleapis.com \
    secretmanager.googleapis.com \
    logging.googleapis.com \
    monitoring.googleapis.com \
    --project=$PROJECT
done
```

### 2. Service Accounts

Create service accounts with minimal permissions:

**Staging:**
```bash
PROJECT_ID="dailyworker-staging"

# CI/CD service account
gcloud iam service-accounts create github-actions-staging \
  --display-name="GitHub Actions Staging" \
  --project=$PROJECT_ID

# Grant roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-staging@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.developer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-staging@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-staging@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Create key
gcloud iam service-accounts keys create staging-sa-key.json \
  --iam-account=github-actions-staging@${PROJECT_ID}.iam.gserviceaccount.com
```

**Production:**
```bash
PROJECT_ID="dailyworker-prod"

# CI/CD service account
gcloud iam service-accounts create github-actions-prod \
  --display-name="GitHub Actions Production" \
  --project=$PROJECT_ID

# Grant roles (same as staging)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-prod@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.developer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-prod@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-prod@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Create key
gcloud iam service-accounts keys create production-sa-key.json \
  --iam-account=github-actions-prod@${PROJECT_ID}.iam.gserviceaccount.com
```

**Application service accounts:**
```bash
# Staging app service account
gcloud iam service-accounts create dailyworker-staging \
  --display-name="DWnews Staging App" \
  --project=dailyworker-staging

# Production app service account
gcloud iam service-accounts create dailyworker-production \
  --display-name="DWnews Production App" \
  --project=dailyworker-prod

# Grant application permissions
for PROJECT in dailyworker-staging dailyworker-prod; do
  SA="dailyworker-${PROJECT##*-}@${PROJECT}.iam.gserviceaccount.com"

  gcloud projects add-iam-policy-binding $PROJECT \
    --member="serviceAccount:$SA" \
    --role="roles/aiplatform.user"

  gcloud projects add-iam-policy-binding $PROJECT \
    --member="serviceAccount:$SA" \
    --role="roles/storage.objectCreator"

  gcloud projects add-iam-policy-binding $PROJECT \
    --member="serviceAccount:$SA" \
    --role="roles/cloudsql.client"

  gcloud projects add-iam-policy-binding $PROJECT \
    --member="serviceAccount:$SA" \
    --role="roles/secretmanager.secretAccessor"
done
```

### 3. Cloud SQL Setup

**Staging:**
```bash
PROJECT_ID="dailyworker-staging"

# Create Cloud SQL instance
gcloud sql instances create dailyworker-staging \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --no-assign-ip \
  --network=default \
  --enable-bin-log \
  --backup-start-time=03:00 \
  --project=$PROJECT_ID

# Create database
gcloud sql databases create dailyworker_staging \
  --instance=dailyworker-staging \
  --project=$PROJECT_ID

# Set root password
gcloud sql users set-password postgres \
  --instance=dailyworker-staging \
  --password=$(openssl rand -base64 32) \
  --project=$PROJECT_ID
```

**Production:**
```bash
PROJECT_ID="dailyworker-prod"

# Create Cloud SQL instance (higher tier)
gcloud sql instances create dailyworker-production \
  --database-version=POSTGRES_15 \
  --tier=db-g1-small \
  --region=us-central1 \
  --availability-type=REGIONAL \
  --no-assign-ip \
  --network=default \
  --enable-bin-log \
  --backup-start-time=03:00 \
  --retained-backups-count=7 \
  --project=$PROJECT_ID

# Create database
gcloud sql databases create dailyworker_prod \
  --instance=dailyworker-production \
  --project=$PROJECT_ID

# Set root password
gcloud sql users set-password postgres \
  --instance=dailyworker-production \
  --password=$(openssl rand -base64 32) \
  --project=$PROJECT_ID
```

### 4. Secret Manager Setup

Store all API keys and credentials in Secret Manager:

**Staging:**
```bash
PROJECT_ID="dailyworker-staging"

# Claude API key
echo -n "your-claude-api-key" | gcloud secrets create claude-api-key \
  --data-file=- \
  --replication-policy=automatic \
  --project=$PROJECT_ID

# OpenAI API key
echo -n "your-openai-api-key" | gcloud secrets create openai-api-key \
  --data-file=- \
  --replication-policy=automatic \
  --project=$PROJECT_ID

# Database URL
echo -n "postgresql://user:password@/cloudsql/connection-name/database" | \
  gcloud secrets create database-url-staging \
  --data-file=- \
  --replication-policy=automatic \
  --project=$PROJECT_ID

# Twitter Bearer Token (optional)
echo -n "your-twitter-token" | gcloud secrets create twitter-bearer-token \
  --data-file=- \
  --replication-policy=automatic \
  --project=$PROJECT_ID

# Grant access to app service account
for SECRET in claude-api-key openai-api-key database-url-staging twitter-bearer-token; do
  gcloud secrets add-iam-policy-binding $SECRET \
    --member="serviceAccount:dailyworker-staging@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project=$PROJECT_ID
done
```

**Production:** (Same process with production values)

### 5. GitHub Secrets

Add the following secrets to your GitHub repository (Settings → Secrets → Actions):

**Staging Secrets:**
- `GCP_STAGING_PROJECT_ID`: `dailyworker-staging`
- `GCP_STAGING_SA_KEY`: Contents of `staging-sa-key.json`
- `GCP_STAGING_SERVICE_ACCOUNT`: `dailyworker-staging@dailyworker-staging.iam.gserviceaccount.com`
- `GCP_STAGING_DB_CONNECTION`: Cloud SQL connection name (e.g., `dailyworker-staging:us-central1:dailyworker-staging`)
- `GCP_STAGING_DB_INSTANCE`: `dailyworker-staging`
- `GCP_STAGING_DATABASE_URL`: PostgreSQL connection string

**Production Secrets:**
- `GCP_PRODUCTION_PROJECT_ID`: `dailyworker-prod`
- `GCP_PRODUCTION_SA_KEY`: Contents of `production-sa-key.json`
- `GCP_PRODUCTION_SERVICE_ACCOUNT`: `dailyworker-production@dailyworker-prod.iam.gserviceaccount.com`
- `GCP_PRODUCTION_DB_CONNECTION`: Cloud SQL connection name
- `GCP_PRODUCTION_DB_INSTANCE`: `dailyworker-production`
- `GCP_PRODUCTION_DATABASE_URL`: PostgreSQL connection string

---

## Deployment Workflows

### Staging Deployment

**Trigger:** Automatic on push to `develop` branch

**Process:**
1. Security checks (scan for hardcoded secrets)
2. Run full test suite (backend + frontend)
3. Build Docker image
4. Scan image for vulnerabilities
5. Run database migrations
6. Deploy to Cloud Run
7. Health checks and smoke tests

**Manual deployment:**
```bash
# Via GitHub Actions UI
# Go to Actions → Deploy to Staging → Run workflow
```

### Production Deployment

**Trigger:** Manual only (requires approval)

**Process:**
1. Pre-deployment validation
   - Security prerequisites check
   - Scan for hardcoded secrets
2. Run full test suite
3. Build production image
4. Create database backup
5. Run database migrations
6. Deploy new revision (no traffic)
7. Test new revision
8. Gradual traffic migration:
   - 10% traffic → wait 1 min → monitor
   - 50% traffic → wait 2 min → monitor
   - 100% traffic → monitor for 5 min
9. Post-deployment verification
10. Automated rollback on failure

**To deploy to production:**
1. Go to GitHub Actions
2. Select "Deploy to Production"
3. Click "Run workflow"
4. Select "production" environment
5. Type "DEPLOY" to confirm
6. Click "Run workflow"
7. Monitor deployment progress

---

## Rollback Procedures

### Automatic Rollback

The production deployment workflow automatically rolls back if:
- New revision health checks fail
- Smoke tests fail on new revision
- Error rate exceeds threshold during monitoring period

### Manual Rollback

If you need to manually rollback:

**Via GitHub Actions:**
1. Go to Actions → Deploy to Production
2. View the failed deployment run
3. The rollback job will have already executed

**Via gcloud CLI:**
```bash
# List recent revisions
gcloud run revisions list \
  --service=dailyworker-production \
  --platform=managed \
  --region=us-central1 \
  --project=dailyworker-prod

# Rollback to specific revision
gcloud run services update-traffic dailyworker-production \
  --to-revisions=REVISION_NAME=100 \
  --platform=managed \
  --region=us-central1 \
  --project=dailyworker-prod
```

### Database Rollback

If migrations fail or cause issues:

```bash
# List backups
gcloud sql backups list \
  --instance=dailyworker-production \
  --project=dailyworker-prod

# Restore from backup
gcloud sql backups restore BACKUP_ID \
  --backup-instance=dailyworker-production \
  --backup-instance-project=dailyworker-prod \
  --instance=dailyworker-production \
  --project=dailyworker-prod
```

---

## Monitoring and Alerting

### Cloud Monitoring

**Key Metrics to Monitor:**
- Request count
- Error rate
- Response latency (P50, P95, P99)
- CPU utilization
- Memory utilization
- Database connections

**Access metrics:**
```bash
# View Cloud Run metrics
gcloud monitoring dashboards list --project=dailyworker-prod

# Or via Cloud Console
https://console.cloud.google.com/monitoring
```

### Cloud Logging

**View logs:**
```bash
# Recent errors
gcloud logging read \
  "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit=50 \
  --format=json \
  --project=dailyworker-prod

# Specific time range
gcloud logging read \
  "resource.type=cloud_run_revision" \
  --format=json \
  --freshness=1h \
  --project=dailyworker-prod
```

### Alerting Policies

Create alerts for:
- Error rate > 5%
- Response latency P95 > 2s
- Memory usage > 80%
- Database connection failures
- Deployment failures

**Example alert:**
```bash
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s \
  --project=dailyworker-prod
```

---

## Cost Monitoring

### Budget Alerts

Set up budget alerts to prevent runaway costs:

```bash
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Daily Worker Production Budget" \
  --budget-amount=100 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=100
```

### Cost Breakdown

**Expected monthly costs:**

| Service | Staging | Production |
|---------|---------|------------|
| Cloud Run | $5-10 | $20-50 |
| Cloud SQL | $10-15 | $30-60 |
| Cloud Storage | $1-5 | $5-15 |
| Networking | $1-5 | $5-10 |
| Secret Manager | $0-1 | $0-1 |
| Logging | $0-5 | $5-10 |
| **Total** | **$17-41** | **$65-146** |

*Costs vary based on traffic and usage*

---

## Security Checklist

Before first production deployment, ensure:

- [ ] **API Keys:** All API keys scoped and restricted (see `CLOUD_SECURITY_CONFIG.md`)
- [ ] **Service Accounts:** Created with minimal permissions
- [ ] **Secrets:** All secrets in GCP Secret Manager (not in code)
- [ ] **Database:** Private IP only, SSL enforced
- [ ] **Networking:** VPC configured, firewall rules set
- [ ] **Cloud Armor:** Enabled for DDoS protection
- [ ] **IAM:** MFA enabled for all human users
- [ ] **Monitoring:** Alerts configured
- [ ] **Backups:** Automated backups tested
- [ ] **Container:** Running as non-root user
- [ ] **Dependencies:** Vulnerability scans passing

See complete checklist in `projects/DWnews/plans/CLOUD_SECURITY_CONFIG.md`

---

## Troubleshooting

### Deployment Fails at Build Step

**Check:**
- Docker build logs in GitHub Actions
- Dependency conflicts in requirements.txt or package.json
- Build context size (should be < 500MB)

**Fix:**
```bash
# Test build locally
cd projects/DWnews
docker build -t test .
```

### Deployment Fails at Migration Step

**Check:**
- Migration script errors
- Database connectivity
- Cloud SQL Proxy connection

**Fix:**
```bash
# Test migrations locally
./cloud_sql_proxy -instances=CONNECTION_NAME=tcp:5432 &
cd projects/DWnews
python database/migrations/migrate.py
```

### Health Checks Failing

**Check:**
- Application startup logs
- Database connection
- Secret Manager access
- Port configuration (must be 8080)

**Fix:**
```bash
# View Cloud Run logs
gcloud run services logs read dailyworker-production \
  --limit=50 \
  --project=dailyworker-prod
```

### High Latency or Errors

**Check:**
- Cloud Run metrics (CPU, memory)
- Database query performance
- API rate limits (Claude, OpenAI)

**Fix:**
- Scale up Cloud Run instances
- Optimize database queries
- Implement caching
- Add read replicas

---

## Best Practices

1. **Always deploy to staging first**
   - Test thoroughly in staging before production
   - Validate database migrations in staging

2. **Use gradual rollouts**
   - Production deployment uses 10% → 50% → 100% traffic
   - Monitor error rates at each stage

3. **Monitor actively**
   - Watch logs during and after deployment
   - Set up alerts for abnormal patterns

4. **Keep backups fresh**
   - Database backups before each deployment
   - Test backup restoration quarterly

5. **Document incidents**
   - Track deployment issues
   - Update runbooks based on learnings

6. **Regular security reviews**
   - Weekly security log review
   - Monthly IAM audit
   - Quarterly penetration testing

---

## Emergency Contacts

- **GCP Support:** https://console.cloud.google.com/support
- **GitHub Status:** https://www.githubstatus.com/
- **On-Call:** [CONFIGURE_ONCALL_CONTACT]

---

## Additional Resources

- [GCP Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Best Practices](https://cloud.google.com/sql/docs/postgres/best-practices)
- [Secret Manager Guide](https://cloud.google.com/secret-manager/docs)
- [Cloud Armor Documentation](https://cloud.google.com/armor/docs)
- [Security Configuration](../projects/DWnews/plans/CLOUD_SECURITY_CONFIG.md)

---

**Document Version:** 1.0
**Last Updated:** 2026-01-01
**Maintained By:** DevOps Team
