Deployment steps (automated workflows created)

Workflows added:
- .github/workflows/deploy-frontend.yml  (deploys frontend to Vercel on push to main)
- .github/workflows/deploy-backend-render.yml  (builds backend and triggers Render deploy on push to main)

Required repository secrets (add in GitHub > Settings > Secrets & Variables > Actions):
- VERCEL_TOKEN  (Vercel personal token)
- VERCEL_ORG_ID
- VERCEL_PROJECT_ID
- RENDER_API_KEY  (Render API key)
- RENDER_SERVICE_ID  (Render service id, e.g., srv-xxxxx)
- MONGODB_URI  (if you want persistence on MongoDB Atlas)
- OPENAI_API_KEY  (optional, for AI suggestions)

How it works:
1. Push code to main branch.
2. Frontend workflow builds the frontend in ./frontend and deploys using Vercel action.
3. Backend workflow builds backend and calls Render's API to trigger a deploy of your Render service (must be connected to this GitHub repo).

If you'd like, I can open a PR with these changes or attempt to push to origin/main. If you prefer manual setup, I can give exact steps to link the repo in Vercel and Render.
