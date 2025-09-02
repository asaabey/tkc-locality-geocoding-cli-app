# Netlify Deployment Notes

## Build
- Base directory: `frontend`
- Build command: `npm ci && npm run build`
- Publish directory: `dist`

## Environment Variables
- Set `VITE_API_BASE_URL` to your backend URL, e.g. `https://aus-geocoding-api.docpockets.com`
- You can also set this in `netlify.toml` under `[context.production.environment]`

## Local Development
- Copy `.env.example` to `.env.local` and customize as needed.
- Run `npm run dev` from the `frontend/` folder.

## CORS
- Backend currently allows CORS from all origins. For production harden this to your Netlify domain.
