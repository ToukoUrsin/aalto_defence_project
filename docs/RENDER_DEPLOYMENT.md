# 🚀 Render.com Deployment Guide

Complete guide to deploying the Military Hierarchy System on Render.com for **FREE** (90-day database).

Perfect for **hackathons** and **demos**!

---

## ⏱️ Time Required: ~25-30 minutes

---

## 📋 Prerequisites

1. **GitHub Account** with this repository pushed
2. **Render.com Account** (free) - Sign up at [render.com](https://render.com)
3. **Google Gemini API Key** - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

---

## 🎯 Deployment Steps

### Step 1: Create Render Account (2 minutes)

1. Go to [render.com](https://render.com)
2. Click **"Get Started"**
3. Sign up with GitHub (recommended for easy repo access)
4. Verify your email

### Step 2: Deploy Using Blueprint (5 minutes)

1. In Render Dashboard, click **"New +"** → **"Blueprint"**
2. Connect your GitHub account if not already connected
3. Search for `aalto_defence_project` repository
4. Click **"Connect"**
5. Render will automatically detect `render.yaml`
6. Click **"Apply"** to start deployment

**What happens:**

- ✅ Creates PostgreSQL database (free tier, 90 days)
- ✅ Deploys backend API
- ✅ Deploys frontend dashboard
- ✅ Links everything together

### Step 3: Configure Environment Variables (3 minutes)

The blueprint will pause and ask for environment variables:

1. **For Backend Service:**

   - Click on `military-hierarchy-backend` service
   - Go to **"Environment"** tab
   - Add:
     ```
     Key: GEMINI_API_KEY
     Value: your_actual_gemini_api_key_here
     ```
   - Click **"Save Changes"**

2. **Frontend will auto-configure** with backend URL

### Step 4: Wait for Initial Build (10-15 minutes)

Render will now:

- 📦 Install dependencies
- 🗄️ Initialize PostgreSQL database
- 🏗️ Build backend and frontend
- 🚀 Deploy everything

**Watch the build logs:**

- Click on each service to see progress
- Look for **"Build succeeded"** message
- Then **"Deploy succeeded"**

### Step 5: Get Your URLs (1 minute)

Once deployed, Render provides URLs:

1. **Backend API:**

   - Find in `military-hierarchy-backend` service
   - Format: `https://military-hierarchy-backend-xxxx.onrender.com`
   - Test: Visit `/hierarchy` endpoint

2. **Frontend Dashboard:**
   - Find in `military-hierarchy-frontend` service
   - Format: `https://military-hierarchy-frontend-xxxx.onrender.com`
   - Open in browser!

---

## ✅ Verification Checklist

### Backend Health Check:

```bash
curl https://your-backend-url.onrender.com/hierarchy
```

Should return JSON with units.

### Frontend Access:

- Open frontend URL in browser
- Should see the Military Hierarchy Dashboard
- Check if it connects to backend (network tab)

### Database Check:

```bash
curl https://your-backend-url.onrender.com/soldiers
```

Should return sample soldiers data.

---

## 🎪 For Hackathon Demos

### Quick Demo Setup (5 minutes before presenting):

1. **Open Frontend URL** in browser
2. **Test Features:**

   - View hierarchy tree
   - Check soldier reports
   - Test AI chat feature
   - Show FRAGO generation
   - Demo CASEVAC/EOINCREP suggestions

3. **Explain Stack:**
   - "Backend: Python FastAPI + PostgreSQL on Render"
   - "Frontend: Next.js 15 + React 19"
   - "AI: Google Gemini 2.5 Pro"
   - "Real-time: MQTT messaging"

---

## 🐛 Troubleshooting

### Issue: Build Fails

**Solution:**

- Check build logs in Render dashboard
- Verify `GEMINI_API_KEY` is set correctly
- Ensure GitHub repo is up to date

### Issue: Database Connection Error

**Solution:**

- Wait 2-3 minutes for database to fully initialize
- Check `DATABASE_URL` environment variable is auto-set
- Restart backend service

### Issue: Frontend Can't Connect to Backend

**Solution:**

- Check CORS settings (should allow all origins in code)
- Verify `NEXT_PUBLIC_API_URL` environment variable
- Check backend logs for errors

### Issue: "Service Unavailable" After Some Time

**Solution:**

- Free tier services sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- Keep demo page open during presentation

---

## 💰 Cost Breakdown

| Resource     | Free Tier               | Paid Tier  |
| ------------ | ----------------------- | ---------- |
| **Backend**  | Free (750 hrs/month)    | $7/month   |
| **Frontend** | Free (100 GB bandwidth) | $7/month   |
| **Database** | **Free for 90 days**    | $7/month   |
| **Total**    | **$0 for 90 days**      | ~$21/month |

**For hackathons:** 90 days is MORE than enough! 🎉

---

## 🔄 Updating Your Deployment

After making code changes:

```bash
# 1. Commit and push to GitHub
git add .
git commit -m "Update feature"
git push origin main

# 2. Render auto-deploys! (if auto-deploy enabled)
# Or click "Manual Deploy" in Render dashboard
```

---

## 📊 Monitoring

### View Logs:

1. Go to Render Dashboard
2. Click on service name
3. Click **"Logs"** tab
4. See real-time application logs

### Performance Metrics:

- Click **"Metrics"** tab to see:
  - CPU usage
  - Memory usage
  - Request count
  - Response times

---

## 🎓 Advanced Configuration

### Custom Domain (Optional):

1. In service settings, go to **"Settings"** → **"Custom Domains"**
2. Add your domain
3. Update DNS records as instructed

### Environment-Specific Settings:

```python
# backend/backend.py automatically detects environment
if os.getenv("DATABASE_URL"):
    # Production: PostgreSQL
    use_postgres()
else:
    # Local: SQLite
    use_sqlite()
```

### Scale Up for Production:

- Upgrade to paid tiers for:
  - ✅ No sleep on inactivity
  - ✅ Faster response times
  - ✅ More resources
  - ✅ Permanent database

---

## 🆘 Support

### Render Documentation:

- [Render Docs](https://render.com/docs)
- [PostgreSQL Guide](https://render.com/docs/databases)

### Project Issues:

- Check GitHub repository issues
- Review application logs in Render

---

## 🎉 Success!

Your application is now live and accessible from anywhere!

**Share these URLs:**

- 🌐 Frontend: `https://military-hierarchy-frontend-xxxx.onrender.com`
- 🔧 API Docs: `https://military-hierarchy-backend-xxxx.onrender.com/docs`

**Perfect for:**

- ✅ Hackathon demos
- ✅ Portfolio showcases
- ✅ Client presentations
- ✅ Team testing

---

## 📝 Notes

- **First request after sleep:** Takes ~30-60 seconds
- **Database:** Persists for 90 days on free tier
- **Bandwidth:** 100 GB/month on free tier
- **Build time:** ~10-15 minutes initial, ~5 minutes for updates

---

**Good luck with your hackathon! 🚀**
