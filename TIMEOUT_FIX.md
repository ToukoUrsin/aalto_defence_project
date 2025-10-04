# AI Chat Timeout Fix

## Problem
- **502 Bad Gateway** errors when calling `/ai/chat` on Render
- Gemini API (gemini-2.5-pro) takes longer than Render's timeout to respond
- Render Free tier has a **30-second request timeout**

## Root Cause
1. Gemini-2.5-pro is a powerful but slower model
2. Processing 50+ reports in a single prompt takes time
3. No timeout handling in the backend code
4. Gunicorn default timeout is 30 seconds (matches Render's limit)

## Solutions Implemented

### 1. **Added Timeout to Gemini API Call**
```python
gemini_response = model_with_timeout.generate_content(
    prompt,
    request_options={'timeout': 25}  # 25 seconds (under Render's 30s limit)
)
```

### 2. **Reduced Report Processing**
- Changed from 50 reports → **20 reports** for faster response
- Less data for Gemini to process = faster response time

### 3. **Added Timeout Error Handling**
```python
except TimeoutError as e:
    logger.error(f"Gemini API timeout: {e}")
    response = "AI analysis in progress... Taking longer than expected."
```

### 4. **Increased Gunicorn Timeout**
```yaml
startCommand: gunicorn backend:app --timeout 90 --graceful-timeout 90
```
- Backend worker timeout: 30s → **90s**
- Graceful shutdown: 30s → **90s**

### 5. **Optimized Gemini Configuration**
```python
generation_config={
    'response_mime_type': 'text/plain',
    'max_output_tokens': 1024  # Limit response length for speed
}
```

## Testing

### Test Locally
```powershell
# Start backend
python backend/backend.py

# Test in another terminal
.\test_ai_local.ps1
```

### Test on Render
```powershell
.\test_ai_chat_curl.ps1
```

## Expected Behavior

### Before Fix
- ❌ 502 Bad Gateway after ~30 seconds
- ❌ No error handling
- ❌ Slow processing of 50 reports

### After Fix
- ✅ Response within 25 seconds or timeout gracefully
- ✅ Clear error messages if timeout occurs
- ✅ Faster processing (20 reports max)
- ✅ Backend stays running (no crash)

## Alternative Solutions (if still timing out)

### Option A: Use Faster Model
Change to `gemini-1.5-flash` (much faster):
```python
gemini_model = genai.GenerativeModel('gemini-1.5-flash')
```

### Option B: Async Processing
- Accept request immediately (return 202 Accepted)
- Process in background
- Client polls for result

### Option C: Further Reduce Reports
```python
for i, report in enumerate(reports[:10], 1):  # Only 10 reports
```

### Option D: Upgrade Render Plan
- Render Free: 30s timeout
- Render Starter: 300s timeout (5 minutes)

## Deployment

```bash
# Commit changes
git add backend/backend.py render.yaml
git commit -m "Fix: Add timeout handling for Gemini API calls"
git push origin render-deployment
```

Render will automatically redeploy with the new configuration.

## Monitoring

Check Render logs for:
- `"Gemini API success"` - Working correctly
- `"Gemini API timeout"` - Still timing out (needs faster model)
- `"Gemini API error"` - Other API issues

## Current Configuration
- **Model**: gemini-2.5-pro (most capable, but slower)
- **Reports Analyzed**: Up to 20 reports
- **API Timeout**: 25 seconds
- **Gunicorn Timeout**: 90 seconds
- **Max Response Tokens**: 1024 tokens

**Note**: Render's infrastructure timeout (30s) is a hard limit that can't be increased on the free tier. The backend timeout is now 90s, but Render's proxy will still kill requests after 30s on the free plan.
