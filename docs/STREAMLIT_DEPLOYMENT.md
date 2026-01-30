# Streamlit Cloud Deployment Guide

## 🚀 Quick Setup for Hosted Streamlit App

### Step 1: Add Secrets to Streamlit Cloud

1. Go to your Streamlit Cloud dashboard: https://share.streamlit.io/
2. Click on your deployed app
3. Click the **"⚙️ Settings"** button
4. Go to the **"Secrets"** section
5. Add the following secrets:

```toml
GEMINI_API_KEY = "AIzaSyBIM4Cm0fJZefnAduktRPg7KDAsfQSbyjQ"
GEMINI_MODEL = "gemma-3-27b-it"
```

6. Click **"Save"**
7. Your app will automatically restart with the new secrets

### Step 2: Verify AI Features Work

After adding the secrets and restarting:

1. Navigate to **"🤖 AI Insights"** page
2. Try asking a question like: "Which sites are underperforming?"
3. You should see AI-generated insights

### ⚠️ Important Notes

- **Never commit `.streamlit/secrets.toml` to GitHub** - it's already in `.gitignore`
- Secrets are only accessible to your deployed app on Streamlit Cloud
- Local development uses `.env` file, hosted deployment uses Streamlit secrets
- The code automatically detects which source to use

### 🔄 How It Works

The application checks for API keys in this order:

1. **Parameter passed to `GenerativeAI(api_key="...")`** (highest priority)
2. **Streamlit Cloud secrets** (`st.secrets["GEMINI_API_KEY"]`)
3. **Environment variables from `.env`** (lowest priority, local dev only)

This ensures seamless operation in both local and hosted environments.

### 🐛 Troubleshooting

**Problem:** AI Insights not working on hosted app

**Solution:**
1. Check that you added the secrets correctly in Streamlit Cloud
2. Verify the secret key is exactly `GEMINI_API_KEY` (case-sensitive)
3. Check app logs for errors: Settings → Logs
4. Restart the app: Settings → Reboot app

**Problem:** "Gemini client not initialized" error

**Solution:**
- The API key may be missing or invalid
- Check Streamlit Cloud logs for specific error messages
- Verify the API key is still active in Google Cloud Console

**Problem:** "Response Blocked" messages

**Solution:**
- Try rephrasing your questions
- The AI model may have content filters triggered
- Check if you're using `gemma-3-27b-it` model (set in secrets)

### 📝 Local Development

For local development, use the `.env` file:

```bash
# .env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemma-3-27b-it
```

Or create `.streamlit/secrets.toml` (not committed):

```toml
GEMINI_API_KEY = "your_api_key_here"
GEMINI_MODEL = "gemma-3-27b-it"
```

### ✅ Verification Checklist

- [ ] Added `GEMINI_API_KEY` to Streamlit Cloud secrets
- [ ] Added `GEMINI_MODEL` to Streamlit Cloud secrets
- [ ] Saved secrets and restarted app
- [ ] Tested AI Insights page
- [ ] Verified AI responses are generated
- [ ] Checked no errors in logs

---

**Last Updated:** January 30, 2026
