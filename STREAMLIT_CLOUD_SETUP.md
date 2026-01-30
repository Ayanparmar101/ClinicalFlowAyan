# Streamlit Cloud Deployment - AI Configuration Guide

## 🚨 IMPORTANT: Required Secrets Configuration

Your Streamlit Cloud app **requires** API secrets to enable AI features. Without these, the AI Insights page will not work.

## ✅ Step-by-Step Setup

### 1. Access Your Streamlit Cloud Dashboard

1. Go to: https://share.streamlit.io/
2. Find your deployed app: **ClinicalFlowAyan**
3. Click on the app name
4. Click the **"⚙️ Settings"** menu (three dots in top right)
5. Select **"Secrets"**

### 2. Add Your Secrets

Copy and paste this **EXACT format** into the secrets editor:

```toml
GEMINI_API_KEY = "AIzaSyBIM4Cm0fJZefnAduktRPg7KDAsfQSbyjQ"
GEMINI_MODEL = "gemma-3-27b-it"
```

**Critical Notes:**
- ✅ Use **double quotes** around values
- ✅ Use **equals sign with spaces**: ` = `
- ✅ Key names must be **EXACT**: `GEMINI_API_KEY` and `GEMINI_MODEL`
- ❌ Do NOT use `.get()` or dictionary access in secrets
- ❌ Do NOT add extra spaces or formatting

### 3. Save and Restart

1. Click **"Save"** at the bottom of the secrets editor
2. Your app will automatically restart
3. Wait 30-60 seconds for the restart to complete

### 4. Verify AI is Working

After restart:

1. Navigate to **"🤖 AI Insights"** page
2. Click **"Generate Portfolio Summary"**
3. You should see AI-generated text appear
4. If you see errors, check the logs (Settings → Logs)

## 🔍 Troubleshooting

### Problem: "Gemini client not initialized" error

**Solutions:**
1. Check that secrets are saved correctly (no typos)
2. Verify the key format matches exactly (double quotes, spaces around `=`)
3. Make sure key names are: `GEMINI_API_KEY` and `GEMINI_MODEL`
4. Try restarting the app: Settings → Reboot app

### Problem: "API key not found" error

**Solutions:**
1. The secrets might not be loaded - check Settings → Secrets
2. Verify you clicked "Save" after adding secrets
3. Try adding secrets again using the exact format above
4. Check app logs for specific error messages

### Problem: "Response Blocked" messages

**Solutions:**
- This means the AI model's content filters were triggered
- Try rephrasing your question to be more neutral
- Check that you're using `gemma-3-27b-it` model (not `gemini-2.0-flash-exp`)

### Problem: Still not working after adding secrets

**Complete Reset:**
1. Go to Settings → Secrets
2. Delete all existing secrets
3. Re-add using the EXACT format shown in Step 2
4. Click Save
5. Go to Settings → Reboot app
6. Wait 60 seconds
7. Clear your browser cache and reload the page

## 📊 How It Works

The application uses a priority system for API keys:

```python
Priority 1: st.secrets["GEMINI_API_KEY"]  # Streamlit Cloud secrets
Priority 2: os.getenv("GEMINI_API_KEY")    # Environment variables
Priority 3: .env file                      # Local development only
```

On Streamlit Cloud:
- The app checks `st.secrets` first
- If not found, it falls back to environment variables (which are empty on Cloud)
- `.env` files are NOT deployed to Streamlit Cloud

## 🧪 Local Development

For local testing, you can use either:

**Option 1: `.env` file** (already set up)
```bash
GEMINI_API_KEY=AIzaSyBIM4Cm0fJZefnAduktRPg7KDAsfQSbyjQ
GEMINI_MODEL=gemma-3-27b-it
```

**Option 2: `.streamlit/secrets.toml`** (recommended for local)
```toml
GEMINI_API_KEY = "AIzaSyBIM4Cm0fJZefnAduktRPg7KDAsfQSbyjQ"
GEMINI_MODEL = "gemma-3-27b-it"
```

## 📝 Verification Checklist

Before asking for help, verify:

- [ ] Secrets added to Streamlit Cloud (not .env file)
- [ ] Secret format matches exactly: `KEY = "value"`
- [ ] Both secrets added: `GEMINI_API_KEY` and `GEMINI_MODEL`
- [ ] Clicked "Save" in secrets editor
- [ ] App restarted (automatic or manual)
- [ ] Waited 60 seconds after restart
- [ ] Tested on "🤖 AI Insights" page
- [ ] Checked logs for specific errors

## 🆘 Still Having Issues?

Check the app logs:
1. Settings → Logs
2. Look for lines containing "Gemini" or "API"
3. Common log messages:
   - `✓ Gemini AI initialized successfully` = Working!
   - `Gemini API key not found` = Secrets not configured
   - `Failed to initialize Gemini client` = Invalid API key

## 🔐 Security Notes

- Secrets are encrypted on Streamlit Cloud
- Never commit secrets to GitHub
- `.streamlit/secrets.toml` is in `.gitignore`
- Only you can access your app's secrets

---

**Last Updated:** January 30, 2026

**Need Help?** Check app logs first, then verify secret format matches exactly.
