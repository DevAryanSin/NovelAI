# NovelAI Deployment Guide

This guide provides step-by-step instructions for deploying the NovelAI application with the frontend on Vercel and the backend on Render.

## Prerequisites

- GitHub account (for connecting to Vercel and Render)
- Google Gemini API keys
- Your code pushed to a GitHub repository

## Backend Deployment (Render)

### Step 1: Prepare Your Repository

Ensure your backend code is pushed to GitHub with the following files:
- `Dockerfile` ✓
- `requirements.txt` ✓
- `.env.example` (template only, not actual keys) ✓
- All Python application files ✓

### Step 2: Create a New Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `novelai-backend` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `backend`
   - **Runtime**: `Docker`
   - **Instance Type**: Free or paid tier (Free tier has limitations)

### Step 3: Configure Environment Variables

In the Render dashboard, add the following environment variables:

```
GEMINI_API_KEY_TEXT_IMAGE=your_actual_gemini_api_key_for_text_and_images
GEMINI_API_KEY_VIDEO=your_actual_gemini_api_key_for_video
GEMINI_API_KEY=your_actual_gemini_api_key
PORT=8000
```

> **Note**: Render automatically sets the `PORT` environment variable, but we include it for clarity.

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Render will automatically build and deploy your Docker container
3. Wait for the deployment to complete (usually 5-10 minutes)
4. Note your backend URL: `https://your-app-name.onrender.com`

### Step 5: Verify Backend Deployment

Test your backend by visiting:
```
https://your-app-name.onrender.com/docs
```

You should see the FastAPI automatic documentation page.

---

## Frontend Deployment (Vercel)

### Step 1: Prepare Your Repository

Ensure your frontend code is pushed to GitHub with the following files:
- `vercel.json` ✓
- `.env.example` (template only) ✓
- `next.config.ts` ✓
- All Next.js application files ✓

### Step 2: Create a New Project on Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)

### Step 3: Configure Environment Variables

In the Vercel project settings, add the following environment variables:

#### Required Variables:
```
NEXT_PUBLIC_BACKEND_URL=https://your-backend-app.onrender.com
```

> **Important**: Replace `your-backend-app` with your actual Render backend URL from the previous step.

#### Optional Variables (if using Gemini on frontend):
```
GEMINI_API_KEY_TEXT_IMAGE=your_actual_gemini_api_key_for_text_and_images
GEMINI_API_KEY_VIDEO=your_actual_gemini_api_key_for_video
```

> **Note**: Currently, all Gemini API calls are made from the backend, so these frontend variables are optional.

### Step 4: Deploy

1. Click **"Deploy"**
2. Vercel will automatically build and deploy your application
3. Wait for the deployment to complete (usually 2-5 minutes)
4. Your app will be available at: `https://your-app-name.vercel.app`

### Step 5: Verify Frontend Deployment

1. Visit your Vercel URL: `https://your-app-name.vercel.app`
2. Upload a test PDF file
3. Verify that the processing works end-to-end

---

## Local Development Setup

### Backend (Local)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and add your actual API keys:
   ```
   GEMINI_API_KEY_TEXT_IMAGE=your_actual_key
   GEMINI_API_KEY_VIDEO=your_actual_key
   GEMINI_API_KEY=your_actual_key
   PORT=8000
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the backend:
   ```bash
   uvicorn main:app --reload
   ```

6. Backend will be available at: `http://localhost:8000`

### Frontend (Local)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Create a `.env.local` file from the template:
   ```bash
   cp .env.example .env.local
   ```

3. Edit `.env.local`:
   ```
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   GEMINI_API_KEY_TEXT_IMAGE=your_actual_key
   GEMINI_API_KEY_VIDEO=your_actual_key
   ```

4. Install dependencies:
   ```bash
   npm install
   ```

5. Run the frontend:
   ```bash
   npm run dev
   ```

6. Frontend will be available at: `http://localhost:3000`

---

## Environment Variables Reference

### Backend Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `GEMINI_API_KEY_TEXT_IMAGE` | Google Gemini API key for text and image generation | Yes | `AIzaSy...` |
| `GEMINI_API_KEY_VIDEO` | Google Gemini API key for video generation | Yes | `AIzaSy...` |
| `GEMINI_API_KEY` | Primary Google Gemini API key | Yes | `AIzaSy...` |
| `PORT` | Port for the backend server | No (defaults to 8000) | `8000` |

### Frontend Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_BACKEND_URL` | URL of the backend API | Yes | `https://your-app.onrender.com` or `http://localhost:8000` |
| `GEMINI_API_KEY_TEXT_IMAGE` | Google Gemini API key (optional, if used on frontend) | No | `AIzaSy...` |
| `GEMINI_API_KEY_VIDEO` | Google Gemini API key (optional, if used on frontend) | No | `AIzaSy...` |

---

## Troubleshooting

### Backend Issues

**Problem**: Render deployment fails with "out of memory" error
- **Solution**: Upgrade to a paid Render plan with more memory, or optimize your dependencies in `requirements.txt`

**Problem**: Backend returns 500 errors
- **Solution**: Check Render logs for detailed error messages. Verify all environment variables are set correctly.

**Problem**: CORS errors when frontend tries to access backend
- **Solution**: The backend is configured with `allow_origins=["*"]` in `main.py`. If you want to restrict this, update the CORS middleware configuration.

### Frontend Issues

**Problem**: "NEXT_PUBLIC_BACKEND_URL is not defined" error
- **Solution**: Ensure you've set the `NEXT_PUBLIC_BACKEND_URL` environment variable in Vercel dashboard

**Problem**: API calls fail with network errors
- **Solution**: Verify your backend URL is correct and the backend is running. Check browser console for detailed error messages.

**Problem**: Build fails on Vercel
- **Solution**: Check Vercel build logs. Ensure all dependencies are in `package.json` and there are no TypeScript errors.

### General Issues

**Problem**: PDF processing times out
- **Solution**: This is likely due to Gemini API rate limits or slow responses. The backend includes delays between API calls to prevent rate limiting. For large PDFs, consider upgrading your Render instance.

**Problem**: Images not generating
- **Solution**: Verify your Gemini API keys have access to image generation. Check backend logs for specific error messages.

---

## Post-Deployment Checklist

- [ ] Backend is accessible at your Render URL
- [ ] Frontend is accessible at your Vercel URL
- [ ] Environment variables are set correctly in both platforms
- [ ] Test PDF upload and processing works end-to-end
- [ ] Test image generation for chapters
- [ ] Test PDF download functionality
- [ ] Check that no API keys are committed to your repository
- [ ] Set up custom domain (optional)
- [ ] Configure monitoring and alerts (optional)

---

## Security Best Practices

1. **Never commit `.env` files** - They are already in `.gitignore`
2. **Rotate API keys regularly** - Update them in Vercel and Render dashboards
3. **Use environment-specific keys** - Consider separate API keys for development and production
4. **Monitor API usage** - Check your Google Cloud Console for Gemini API usage
5. **Set up rate limiting** - Consider adding rate limiting to your backend API

---

## Updating Your Deployment

### Backend Updates

1. Push changes to your GitHub repository
2. Render will automatically detect changes and redeploy
3. Monitor the deployment in Render dashboard

### Frontend Updates

1. Push changes to your GitHub repository
2. Vercel will automatically detect changes and redeploy
3. Monitor the deployment in Vercel dashboard

---

## Cost Considerations

### Render (Backend)
- **Free Tier**: Limited to 750 hours/month, spins down after inactivity
- **Paid Tier**: Starts at $7/month for always-on service with more resources

### Vercel (Frontend)
- **Hobby Plan**: Free for personal projects
- **Pro Plan**: $20/month for commercial projects with more bandwidth

### Google Gemini API
- Check [Google AI Pricing](https://ai.google.dev/pricing) for current rates
- Monitor your usage in Google Cloud Console

---

## Support

For issues specific to:
- **Render**: [Render Documentation](https://render.com/docs)
- **Vercel**: [Vercel Documentation](https://vercel.com/docs)
- **Google Gemini**: [Google AI Documentation](https://ai.google.dev/docs)

---

## Next Steps

After successful deployment:
1. Set up a custom domain for your Vercel app
2. Configure monitoring and logging
3. Set up CI/CD pipelines for automated testing
4. Consider adding authentication if needed
5. Optimize performance based on usage patterns
