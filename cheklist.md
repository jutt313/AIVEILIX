l---
  FULL PRODUCTION LAUNCH CHECKLIST

  1. Legal & Compliance

  - Privacy Policy page
  - Terms of Service page
  - Tokusho page
  - [x] Cookie consent banner (exempt - only strictly necessary auth cookies used, no tracking/analytics)
  - [x] GDPR: 72-hour breach notification plan (added to Privacy Policy section 12)
  - [x] Document all subprocessors (internal doc only - available on request)

  2. Security

  - [x] Remove secrets from git history (done - git-filter-repo, force pushed)
  - [ ] Rotate ALL exposed credentials (PENDING - do before launch!)
  - [x] Set strong APP_SECRET_KEY and OAUTH_TOKEN_SECRET via env vars (done - set in Cloud Run)
  - [x] Restrict CORS headers (done - specific headers, removed old URLs, added claude.ai)
  - [x] Remove stack traces from error responses (done - removed type leak, blocked /dev/errors in prod)
  - [x] Run pip audit + npm audit (fixed axios, cryptography, pillow, setuptools, pip - ecdsa unfixable upstream)
  - [x] HTTPS enforced (auto by Firebase + Cloud Run)
  - [x] RLS on all tables (verified in Supabase)
  - [x] API keys hashed with SHA-256 (confirmed in code)

  3. Email

  - Verify SPF record for sending domain
  - Configure DKIM
  - Configure DMARC
  - Test all transactional emails (signup, reset, notifications)

  4. SEO

  - [x] Meta tags, OG tags, Twitter cards (improved - benefit-focused, no internal tech)
  - [x] sitemap.xml (8 pages, submitted to Google)
  - [x] robots.txt (AI crawlers allowed)
  - [x] Structured data (JSON-LD) (featureList instead of fake rating)
  - [x] Submit to Google Search Console (done - 8 pages discovered)

  5. Performance

  - [x] CDN for frontend assets (Firebase auto CDN)
  - [x] Enable gzip/Brotli compression (Firebase auto)
  - [x] Database connection pooling (Supabase Pooler port 6543 + pgbouncer=true)
  - [x] Vite build minified (npm run build in deploy command)

  6. Monitoring

  - [x] Error tracking (using Google Cloud Logging - free, built into Cloud Run, zero setup)
  - [x] Uptime monitoring with alerting (UptimeRobot - free, monitors aiveilix.com + api.aiveilix.com/health)
  - [x] Disable verbose logging in production (OPTIONS + 400 verbose logs silenced in prod)
  - Health endpoint exists (/health)

  7. Database

  - [ ] Automated backups (requires Supabase Pro - upgrade before full launch)
  - [ ] Test backup restoration (do after upgrading to Pro)
  - [x] All 11 migrations applied (verified)
  - [x] Indexes: IVFFlat, GIN, B-tree (in schema)

  8. Stripe & Payments

  - Switch to LIVE Stripe keys (currently test mode)
  - Verify webhook signature in production
  - Test payment flow end-to-end with real card
  - Handle failed payments (dunning emails)
  - Webhook handler implemented
  - Subscription lifecycle (create, cancel, reactivate)

  9. Authentication

  - [x] Rate limit login attempts (5/min on login & signup, 3/min on forgot-password)
  - [x] Prevent user enumeration (generic error messages across all auth endpoints)
  - [x] Email verification on signup (Supabase handles)
  - [x] Password reset with expiring tokens (Supabase handles)
  - [x] JWT token management (implemented)

  10. Deployment

  - [x] Set production env vars: BACKEND_URL, FRONTEND_URL, APP_ENV=production (already set in Cloud Run)
  - CI/CD pipeline
  - Rollback strategy documented
  - [x] Remove all console.log from frontend (silenced in production via main.jsx override)
  - [x] Hot reload disabled in production (auto-disabled when APP_ENV=production)

  11. Pre-Launch Day

  - Full smoke test: signup → login → upload → chat
  - Confirm DNS propagation
  - Confirm SSL valid
  - Confirm error tracking receiving events
  - Confirm backups ran in last 24h

  ---
  Top 3 priorities right now:
  1. [x] Remove secrets from git (DONE)
  2. Restrict CORS + remove stack traces from errors
  3. Set production env vars (BACKEND_URL=https://api.aiveilix.com)

  Want me to start fixing any of these?