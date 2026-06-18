# R2 bucket CORS — required for direct-to-R2 browser uploads

The direct-upload flow PUTs file bytes from the browser straight to Cloudflare
R2 using presigned URLs. The browser will not let those requests through (and
cannot read the multipart **ETag** response header) unless the R2 bucket has a
CORS policy that allows the app origins and **exposes `ETag`**.

Config lives in [`r2-cors.json`](./r2-cors.json).

## What it must contain

- **AllowedOrigins** — every origin the app is served from:
  - `https://aiveilix-499209.web.app` (Firebase Hosting)
  - the future custom domain (`https://app.aiveilix.com` placeholder — edit to match)
  - `http://localhost:5173` (local dev; drop in production if you prefer)
- **AllowedMethods** — `PUT` (single + part uploads), `POST` (multipart ops),
  `GET`, `HEAD`.
- **AllowedHeaders** — `*` (covers `Content-Type`, which is part of the signed
  single-PUT request, and any `x-amz-*` headers). Tighten to
  `["Content-Type"]` if you want to be strict.
- **ExposeHeaders** — **`ETag`** is mandatory. Without it, browser multipart
  completion cannot collect part ETags and large uploads will fail.

## Apply it

### Option A — Cloudflare dashboard
R2 → your bucket → **Settings** → **CORS Policy** → **Edit** → paste the contents
of `r2-cors.json` → Save.

### Option B — Wrangler
```bash
npx wrangler r2 bucket cors set aiveilix --file ./docs/r2-cors.json --force
# verify:
npx wrangler r2 bucket cors list aiveilix
```
(Use the real bucket name — `R2_BUCKET_NAME`, default `aiveilix`.)

### Option C — aws CLI against the S3-compatible endpoint
`aws s3api` expects the rules wrapped under `CORSRules`, so use this inline form:
```bash
aws s3api put-bucket-cors \
  --bucket aiveilix \
  --endpoint-url "https://<R2_ACCOUNT_ID>.r2.cloudflarestorage.com" \
  --cors-configuration '{
    "CORSRules": [
      {
        "AllowedOrigins": ["https://aiveilix-499209.web.app","https://app.aiveilix.com","http://localhost:5173"],
        "AllowedMethods": ["GET","PUT","POST","HEAD"],
        "AllowedHeaders": ["*"],
        "ExposeHeaders": ["ETag"],
        "MaxAgeSeconds": 3600
      }
    ]
  }'
```

## Verify
After applying, a browser preflight to an object PUT should return
`Access-Control-Allow-Origin` for your origin and `Access-Control-Expose-Headers: ETag`.
A quick check from the app: upload a >100 MB file — it should complete via the
multipart path and appear in the file list as `processing → ready`.
