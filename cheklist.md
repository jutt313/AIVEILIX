l---
  FULL PRODUCTION LAUNCH CHECKLIST

  1. Legal & Compliance

  - Privacy Policy page
  - Terms of Service page
  - Tokusho page
  - Cookie consent banner
  - GDPR: 72-hour breach notification plan
  - Document all subprocessors (Supabase, OpenAI, DeepSeek)

  2. Security

  - [x] Remove secrets from git history (done - git-filter-repo, force pushed)
  - [ ] Rotate ALL exposed credentials (PENDING - do before launch!)
  - [x] Set strong APP_SECRET_KEY and OAUTH_TOKEN_SECRET via env vars (done - set in Cloud Run)
  - [x] Restrict CORS headers (done - specific headers, removed old URLs, added claude.ai)
  - [x] Remove stack traces from error responses (done - removed type leak, blocked /dev/errors in prod)
  - [x] Run pip audit + npm audit (fixed axios, cryptography, pillow, setuptools, pip - ecdsa unfixable upstream)
  - HTTPS enforced
  - RLS on all tables
  - API keys hashed with SHA-256

  3. Email

  - Verify SPF record for sending domain
  - Configure DKIM
  - Configure DMARC
  - Test all transactional emails (signup, reset, notifications)

  4. SEO

  - Meta tags, OG tags, Twitter cards
  - sitemap.xml
  - robots.txt
  - Structured data (JSON-LD)
  - Submit to Google Search Console

  5. Performance

  - CDN for frontend assets
  - Enable gzip/Brotli compression
  - Database connection pooling (Supabase Pooler)
  - Vite build minified

  6. Monitoring

  - Error tracking (Sentry or similar)
  - Uptime monitoring with alerting
  - Disable verbose logging in production
  - Health endpoint exists (/health)

  7. Database

  - Verify automated backups enabled
  - Test backup restoration once
  - Verify all 6 migrations applied
  - Indexes: IVFFlat, GIN, B-tree

  8. Stripe & Payments

  - Switch to LIVE Stripe keys (currently test mode)
  - Verify webhook signature in production
  - Test payment flow end-to-end with real card
  - Handle failed payments (dunning emails)
  - Webhook handler implemented
  - Subscription lifecycle (create, cancel, reactivate)

  9. Authentication

  - [x] Rate limit login attempts (5/min on login & signup, 3/min on forgot-password)
  - Prevent user enumeration
  - Email verification on signup
  - Password reset with expiring tokens
  - JWT token management

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