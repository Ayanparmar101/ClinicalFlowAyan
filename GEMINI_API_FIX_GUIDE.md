# Gemini API Key Issue - Complete Fix Guide

## Problem Identified
Both API keys in your project are showing:
- `404 models/gemini-pro is not found`
- `API_KEY_INVALID` errors

This means the API keys are either:
1. **Expired or revoked**
2. **From a deleted/disabled Google Cloud project**
3. **Don't have proper permissions for Gemini API**

## ✅ Solution: Get a New Valid API Key

### Step 1: Create New API Key
1. Visit: **https://aistudio.google.com/app/apikey**
2. Sign in with your Google account
3. Click **"Get API Key"** or **"Create API Key"**
4. Select or create a new Google Cloud project
5. Click **"Create API key in new project"** (recommended for testing)
6. Copy the new API key (starts with `AIza...`)

### Step 2: Update .env File
1. Open: `C:\Users\Ayan Parmar\Desktop\NestTry\.env`
2. Replace the GEMINI_API_KEY line with your new key:
   ```
   GEMINI_API_KEY=YOUR_NEW_KEY_HERE
   ```
3. Keep the model as: `GEMINI_MODEL=gemini-pro`
4. Save the file

### Step 3: Test the New Key
Run this command to verify:
```bash
conda activate clinical
cd "C:\Users\Ayan Parmar\Desktop\NestTry"
python test_gemini_api.py
```

You should see:
```
✓ SUCCESS!
Response: API key is working correctly
Your Gemini API is configured correctly!
```

### Step 4: Restart Streamlit Dashboard
Once the key works:
```bash
conda activate clinical
cd "C:\Users\Ayan Parmar\Desktop\NestTry"
streamlit run src/dashboard/app.py
```

## Available Models (as of 2026)
After getting a new key, you can use:
- `gemini-pro` (recommended, stable)
- `gemini-1.5-pro` (larger context)
- `gemini-1.5-flash` (faster, cheaper)
- `gemini-2.0-flash-exp` (experimental, latest)

## Important Notes
⚠️ **Free Tier Limits**: Google AI Studio free tier has rate limits:
- 15 requests per minute
- 1,500 requests per day
- 1 million tokens per day

📝 **API Key Security**:
- Don't share your API key publicly
- Don't commit it to public GitHub repos
- Keep it in your .env file only

## Troubleshooting

### If you still get errors after creating new key:
1. **Wait 1-2 minutes** for key activation
2. **Check internet connection** - API requires network access
3. **Verify key format** - Should start with `AIza` and be ~39 characters
4. **Try different model** - Use `gemini-pro` instead of newer models

### If you see "Quota Exceeded":
- You've hit the free tier limit
- Wait 24 hours for reset
- Or enable billing in Google Cloud Console

## Current Status
❌ **Old Key 1**: `AIzaSyBpIEkrUqRQWl5JL1TCI9uspDU3QNh42Sk` - INVALID
❌ **Old Key 2**: `AIzaSyAQ55XZOdbZ2v1IZCkC09vOaM6Q2KnuJWQ` - INVALID

**Action Required**: Get a new API key from https://aistudio.google.com/app/apikey

## What Will Work After Fix
Once you have a valid API key, these features will work:
✅ Data Completeness Trends (AI summaries)
✅ Study Analysis (AI insights)
✅ CRA Dashboard (AI recommendations)
✅ AI Insights page (natural language queries)
✅ Executive summaries
✅ Risk alerts with explanations

## Quick Commands Reference
```bash
# Activate environment
conda activate clinical

# Test API key
python test_gemini_api.py

# Start dashboard
streamlit run src/dashboard/app.py

# Check environment
conda env list
```

---
**Next Step**: Visit https://aistudio.google.com/app/apikey to get a new API key!
