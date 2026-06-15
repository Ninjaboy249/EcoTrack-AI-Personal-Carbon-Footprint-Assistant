How to push the workflows branch and open a PR

1) Push branch to GitHub (run locally in repo):

   git checkout deploy-workflows-pr
   git push -u origin deploy-workflows-pr

2) Open a pull request using GitHub web UI or gh CLI:

   gh pr create --base main --head deploy-workflows-pr --title "Add deployment workflows" --body "Adds GitHub Actions to deploy frontend to Vercel and backend to Render. See DEPLOYMENT.md for details."

If you prefer the web UI: open your repo on GitHub, you should see a banner to create a PR from deploy-workflows-pr.

Add required repository secrets (GitHub -> Settings -> Secrets & variables -> Actions):
- VERCEL_TOKEN (Vercel personal token)
- VERCEL_ORG_ID
- VERCEL_PROJECT_ID
- RENDER_API_KEY (Render service API key)
- RENDER_SERVICE_ID (Render service id, e.g., srv-xxxx)
- MONGODB_URI (optional)
- OPENAI_API_KEY (optional)

Vercel setup notes:
- Create a new project in Vercel from this GitHub repo, or link an existing project.
- If using the Vercel action, put VERCEL_TOKEN, VERCEL_ORG_ID and VERCEL_PROJECT_ID into repo secrets.
- In Vercel project Settings -> Environment Variables, add any runtime envs (MONGODB_URI, OPENAI_API_KEY).

Render setup notes:
- Create a new Web Service on Render, connect to this GitHub repo and point "Root" to the backend folder.
- Build Command: npm ci && npm run build
- Start Command: npm run start
- Add service environment variables (MONGODB_URI, OPENAI_API_KEY) in Render dashboard.
- Copy the Render Service ID (starts with "srv-") and create a Render API Key (in Account -> API Keys). Add both to GitHub Secrets.

Verification:
- After PR is merged to main, workflows will run automatically.
- Frontend will be deployed to Vercel (check Vercel project dashboard).
- Backend will trigger a Render deploy (check Render service deploys).

If you want, provide access tokens here and I can push and open the PR for you, but for security it's safer if you push and create the PR from your machine. If you'd like a play-by-play while you do it, tell me and I'll guide you interactively.
