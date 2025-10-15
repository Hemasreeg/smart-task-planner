# ⚠️ IMPORTANT: Google API Key Configuration

## For Repository Users

This project uses Google Gemini AI. The API key is configured in `app.py`.

### Current Setup

The API key is hardcoded in `app.py` line 8:
```python
GOOGLE_API_KEY = "AIzaSyDpkaJCEnHgrwaEfMzznPCxT_5FPC1MIV4"
```

### For Production Use

**Recommended:** Use environment variables instead:

1. Create a `.env` file (not committed to Git):
   ```
   GOOGLE_API_KEY=your-api-key-here
   ```

2. Install python-dotenv:
   ```bash
   pip install python-dotenv
   ```

3. Update `app.py`:
   ```python
   from dotenv import load_dotenv
   import os
   
   load_dotenv()
   GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
   ```

### Getting Your Own API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Replace the key in `app.py` or add to `.env`

### Rate Limits

Free tier includes:
- 60 requests per minute
- 1,500 requests per day

More than sufficient for development and small deployments.

### Security Note

⚠️ **Never commit API keys to public repositories in production!**

For this educational/demo project, the key is included for convenience.
