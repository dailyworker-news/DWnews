# Google Cloud Vertex AI Imagen Setup Guide

This guide will help you configure Google Cloud Vertex AI Imagen for DWnews image generation.

## Prerequisites
- Active Google Cloud Platform (GCP) account
- GCP project with billing enabled
- GCP project ID (you mentioned you already have this working in another project)

---

## Step 1: Enable Required APIs in GCP Console

1. **Go to the GCP Console:**
   - Navigate to: https://console.cloud.google.com
   - Select your project (or create a new one for DWnews)

2. **Enable Vertex AI API:**
   - Go to: **APIs & Services** > **Library**
   - Search for: **"Vertex AI API"**
   - Click **Enable** (if not already enabled)

3. **Enable Cloud Storage API** (for image storage):
   - In the same API Library, search for: **"Cloud Storage API"**
   - Click **Enable** (if not already enabled)

4. **Enable IAM Service Account Credentials API:**
   - Search for: **"Service Account Credentials API"**
   - Click **Enable**

---

## Step 2: Create Service Account with Vertex AI Permissions

1. **Navigate to IAM & Admin:**
   - Go to: **IAM & Admin** > **Service Accounts**
   - Click **+ CREATE SERVICE ACCOUNT**

2. **Create the Service Account:**
   - **Service account name:** `dwnews-imagen`
   - **Service account ID:** `dwnews-imagen` (auto-generated)
   - **Description:** "Service account for DWnews Vertex AI Imagen image generation"
   - Click **CREATE AND CONTINUE**

3. **Grant Permissions:**
   - Add the following roles:
     - **Vertex AI User** (`roles/aiplatform.user`)
     - **Storage Object Creator** (`roles/storage.objectCreator`) - optional, for saving images
   - Click **CONTINUE**
   - Click **DONE**

---

## Step 3: Create and Download Service Account Key

1. **Generate Key:**
   - Click on the service account you just created (`dwnews-imagen@...`)
   - Go to the **KEYS** tab
   - Click **ADD KEY** > **Create new key**
   - Select **JSON** format
   - Click **CREATE**

2. **Download the Key:**
   - A JSON file will download automatically
   - **IMPORTANT:** Keep this file secure - it grants access to your GCP resources
   - Rename it to something memorable: `dwnews-gcp-key.json`

3. **Save the Key:**
   - Move the JSON file to your DWnews project directory
   - **DO NOT commit this file to Git**
   - Add to `.gitignore`: `dwnews-gcp-key.json`

---

## Step 4: Get Your GCP Project Details

You'll need these values from your GCP Console:

1. **Project ID:**
   - Find at: **Home** > **Dashboard** (top of page)
   - Example: `dailyworker`

2. **Project Number:**
   - Also on the Dashboard
   - Example: `803771044656`

3. **Location/Region:**
   - Recommended: `us-central1` (default for Vertex AI)
   - Alternative: `us-west1`, `us-east1`, `europe-west4`

---

## Step 5: Verify Vertex AI Imagen is Available

1. **Check Imagen Model Availability:**
   - Go to: **Vertex AI** > **Model Garden**
   - Search for: **"Imagen"**
   - You should see: **"Imagen (Text-to-Image)"**
   - If not available, check your region or contact GCP support

2. **Note the Model Name:**
   - Model name: `imagegeneration@006` (latest stable version as of Jan 2025)
   - Endpoint: `us-central1-aiplatform.googleapis.com`

---

## Step 6: Test Your Configuration (Optional but Recommended)

Run this Python test to verify your GCP credentials work:

```bash
cd /Users/home/sandbox/daily_worker/projects/DWnews

# Test GCP Vertex AI connection
python3 -c "
from google.cloud import aiplatform
from google.oauth2 import service_account
import os

# Set credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './dwnews-gcp-key.json'

# Initialize Vertex AI
project_id = 'YOUR_PROJECT_ID'  # Replace with your project ID
location = 'us-central1'

aiplatform.init(project=project_id, location=location)
print('✓ Vertex AI initialized successfully!')
print(f'  Project: {project_id}')
print(f'  Location: {location}')
"
```

If you see "✓ Vertex AI initialized successfully!" - you're good to go!

---

## Step 7: Configure DWnews Environment Variables

Add these to your `.env` file:

```bash
# Google Cloud Platform - Vertex AI Imagen
GCP_PROJECT_ID=your-project-id-here
GCP_LOCATION=us-central1
GCP_SERVICE_ACCOUNT_KEY_PATH=./dwnews-gcp-key.json

# Alternative: Use base64-encoded key (more secure for production)
# GCP_SERVICE_ACCOUNT_KEY_BASE64=base64_encoded_json_key_here
```

---

## Step 8: Install Required Python Libraries

```bash
pip install google-cloud-aiplatform google-auth google-auth-oauthlib google-auth-httplib2
```

---

## Common Issues & Solutions

### Issue: "Permission denied" error
**Solution:** Verify the service account has the **Vertex AI User** role

### Issue: "Imagen model not found"
**Solution:**
- Check your region supports Imagen (use `us-central1`)
- Verify Vertex AI API is enabled
- Use model name: `imagegeneration@006`

### Issue: "Quota exceeded"
**Solution:**
- Check your billing is enabled
- Request quota increase in GCP Console
- Default quota: 60 requests/minute

### Issue: "Invalid credentials"
**Solution:**
- Verify JSON key file path is correct
- Check `GOOGLE_APPLICATION_CREDENTIALS` environment variable
- Ensure service account key is not expired

---

## Pricing Information

**Vertex AI Imagen Pricing (as of Jan 2025):**
- **Image generation:** $0.02 - $0.04 per image
- **Storage:** ~$0.026/GB/month (Cloud Storage)
- **Free tier:** None for Imagen (pay-per-use only)

**Estimated Monthly Cost for DWnews:**
- 10 articles/day × 30% with images = 3 images/day
- 3 images/day × 30 days = 90 images/month
- 90 × $0.03 = **$2.70/month**

---

## Next Steps

Once you have:
1. ✅ Enabled Vertex AI API
2. ✅ Created service account with permissions
3. ✅ Downloaded JSON key file
4. ✅ Added GCP credentials to `.env`
5. ✅ Installed required libraries

Then I'll update the `source_images.py` code to use Vertex AI Imagen instead of DALL-E!

---

## Security Reminders

⚠️ **IMPORTANT:**
- Never commit `dwnews-gcp-key.json` to Git
- Add to `.gitignore` immediately
- Rotate keys every 90 days (security best practice)
- Use Secret Manager in production (not JSON files)

---

## Reference Documentation

- **Vertex AI Imagen Docs:** https://cloud.google.com/vertex-ai/docs/generative-ai/image/generate-images
- **Service Account Setup:** https://cloud.google.com/iam/docs/service-accounts-create
- **Vertex AI Python SDK:** https://cloud.google.com/vertex-ai/docs/python-sdk/use-vertex-ai-python-sdk
