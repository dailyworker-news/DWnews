# API Credentials Setup Guide

This guide walks you through obtaining the API credentials needed to run The Daily Worker's automated journalism pipeline.

---

## 1. Twitter API v2 Setup

### Why We Need It
Monitor Twitter for breaking news, trends, and worker-related discussions.

### Free Tier Limits
- 1,500 tweets per month (~50/day)
- Sufficient for testing and initial production

### Step-by-Step Instructions

#### Option A: Bearer Token (Recommended - Simpler)

1. **Go to Twitter Developer Portal**
   - Visit: https://developer.twitter.com/
   - Sign in with your Twitter account

2. **Apply for Developer Access**
   - Click "Developer Portal" or "Apply"
   - Select "Hobbyist" → "Exploring the API"
   - Fill out the application form:
     - **Purpose:** News aggregation and monitoring
     - **Use case:** Automated discovery of newsworthy events for a worker-focused news platform
   - Accept terms and submit

3. **Create a Project and App**
   - Once approved, go to "Projects & Apps"
   - Click "Create Project"
   - Name: "Daily Worker Pipeline"
   - Select "Read" permissions only
   - Create an app within the project: "DailyWorker Signal Intake"

4. **Generate Bearer Token**
   - In your app settings, go to "Keys and Tokens"
   - Click "Generate" under "Bearer Token"
   - **COPY THIS TOKEN IMMEDIATELY** (shown only once)
   - Store in password manager

#### Option B: OAuth 1.0a (More Complex, More Control)

If you need additional features later, use this method:
- Generate API Key and Secret
- Generate Access Token and Access Token Secret
- All four credentials needed

### What You'll Provide to Me

Just send (via secure method):
```
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 2. Reddit API Setup

### Why We Need It
Monitor Reddit for trending discussions, worker stories, and community-reported news.

### Free Tier Limits
- 100 requests per minute
- More than sufficient for our needs

### Step-by-Step Instructions

1. **Log in to Reddit**
   - Go to: https://www.reddit.com/
   - Log in with your account (create one if needed)

2. **Navigate to App Preferences**
   - Go to: https://www.reddit.com/prefs/apps
   - Scroll to "Developed Applications" section

3. **Create an Application**
   - Click "Create App" or "Create Another App"
   - Fill out the form:
     - **Name:** The Daily Worker
     - **App type:** Select "script"
     - **Description:** News aggregation for worker-focused journalism
     - **About URL:** (leave blank or use: https://localhost)
     - **Redirect URI:** http://localhost:8080
   - Click "Create app"

4. **Copy Credentials**
   - After creation, you'll see:
     - **Client ID:** Short string under "personal use script" (e.g., `a1b2c3d4e5f6g7`)
     - **Secret:** Longer string next to "secret" label
   - Copy both values

5. **Choose User Agent**
   - Can be any descriptive string
   - Format: `PlatformName/Version (by /u/YourRedditUsername)`
   - Example: `DailyWorker/1.0 (by /u/your_username)`

### What You'll Provide to Me

```
REDDIT_CLIENT_ID=a1b2c3d4e5f6g7
REDDIT_CLIENT_SECRET=h8i9j0k1l2m3n4o5p6q7r8s9
REDDIT_USER_AGENT=DailyWorker/1.0 (by /u/your_username)
```

---

## 3. Optional: LLM API Keys (If Not Already Configured)

### Claude (Anthropic)
- Go to: https://console.anthropic.com/
- Navigate to "API Keys"
- Create new key
- Recommended: Claude 3.5 Sonnet (best quality/cost)

```
CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxx
```

### OpenAI (ChatGPT)
- Go to: https://platform.openai.com/api-keys
- Create new secret key
- Recommended: GPT-4 Turbo (good quality, lower cost than GPT-4)

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
```

### Google Gemini
- Go to: https://makersuite.google.com/app/apikey
- Create API key
- Recommended: Gemini 1.5 Pro

```
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxx
```

**Note:** We'll use whichever LLM API you prefer. Only one is needed.

---

## 4. How to Provide Credentials Securely

### Option A: Create .env.local File (Recommended)

1. Create file at: `/Users/home/sandbox/daily_worker/projects/DWnews/.env.local`

2. Paste credentials in this format:
```env
# Twitter API
TWITTER_BEARER_TOKEN=your_actual_bearer_token_here

# Reddit API
REDDIT_CLIENT_ID=your_actual_client_id
REDDIT_CLIENT_SECRET=your_actual_secret
REDDIT_USER_AGENT=DailyWorker/1.0 (by /u/yourusername)

# LLM API (if not already configured)
CLAUDE_API_KEY=sk-ant-your_key_here
# OR
OPENAI_API_KEY=sk-your_key_here
# OR
GOOGLE_API_KEY=AIzaSy_your_key_here
```

3. Save the file

4. Tell me "Credentials configured in .env.local"

### Option B: Provide Directly (Less Secure)

Just paste the credentials in chat. I'll:
1. Create the .env.local file
2. Confirm it's created
3. Recommend you verify no credentials appear in logs

---

## 5. Security Notes

### Important
- ✅ .env.local is already in .gitignore (won't be committed)
- ✅ Credentials stay on your local machine
- ✅ Never shared with cloud services during local testing
- ⚠️ Keep your .env.local file private
- ⚠️ Don't share credentials in public channels

### If Credentials Are Compromised
- **Twitter:** Regenerate bearer token in developer portal
- **Reddit:** Delete app and create new one
- **LLM APIs:** Regenerate API key in respective platform

---

## 6. Verification

Once you provide credentials, I'll run a test script that:

1. Connects to Twitter API
   - Fetches 10 recent tweets about "labor unions"
   - Verifies authentication works
   - Displays sample results

2. Connects to Reddit API
   - Fetches 10 recent posts from r/antiwork
   - Verifies authentication works
   - Displays sample results

3. Tests LLM API
   - Generates a short test article
   - Verifies generation works

You'll see output confirming each API works correctly.

---

## 7. Cost Tracking

### During Testing (Local)
- Twitter: $0 (free tier)
- Reddit: $0 (free tier)
- LLM: ~$0.50-2.00 per test article (depends on API choice)

### During Production (Daily)
- Twitter: $0 (under free tier limit)
- Reddit: $0 (under free tier limit)
- LLM: ~$15-60/month (depends on article volume and API choice)
- Total: Estimated $15-60/month for LLM generation

**Budget Status:** ✅ Within $30-100/month target

---

## 8. Timeline

### Immediate (Today)
1. You: Obtain Twitter + Reddit credentials (15-30 minutes)
2. You: Provide credentials via .env.local or chat
3. Me: Create verification test script
4. Me: Run verification test
5. Both: Confirm all APIs working

### Next (Same Session)
1. Me: Run signal intake test (discover events from live feeds)
2. Both: Review discovered events
3. Both: Select 1 event for full pipeline test
4. Me: Generate test article
5. You: Editorial review

**Total time:** 1-2 hours for complete local test

---

## Ready to Proceed?

Once you have:
- ✅ Twitter Bearer Token
- ✅ Reddit Client ID + Secret + User Agent
- ✅ (Optional) LLM API key if not already configured

Provide them using Option A (create .env.local) or Option B (paste in chat), and we'll begin testing!
