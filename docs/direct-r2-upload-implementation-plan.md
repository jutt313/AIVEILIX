# Direct-to-R2 Large Upload Implementation Plan

## Why this is needed

Current production upload sends the whole file from the browser to Cloud Run first. That fails for large files because Cloud Run has a 32 MiB HTTP/1 request-size limit before FastAPI receives the request.

For an enterprise document product, the backend should control auth, quota, metadata, and processing, but the raw file bytes should go directly from the browser to Cloudflare R2.

Target flow:

1. Frontend asks backend to start an upload.
2. Backend checks auth, bucket permission, file count, storage quota, and per-file size limit.
3. Backend creates a safe R2 object key and returns presigned upload info.
4. Browser uploads directly to R2.
5. Frontend tells backend the upload is complete.
6. Backend verifies the R2 object, creates/updates DB rows, and starts the existing processing pipeline.

Do not expose R2 secrets in frontend code.

## Current Implementation

Backend route:

- `backend/app/api/v1/endpoints/files.py`
- `POST /v1/buckets/{bucket_id}/files`
- Accepts `files: list[UploadFile] = FastAPIFile(...)`.
- Calls `_require_bucket_for_action(..., "can_upload_files")`.
- Calls `enforce_upload_quota(...)`.
- Calls `intake_upload(...)`.
- Adds `process_file(...)` as a background task.

Backend intake:

- `backend/app/services/pipeline/upload.py`
- `intake_upload(...)` reads the whole upload into memory with `file_bytes = await upload.read()`.
- Uploads raw bytes to R2 with `upload_file(file_bytes, r2_key, content_type=content_type)`.
- Creates `files` and `file_versions` rows.
- Logs `upload_completed` and `file_processing_started`.
- Sets file status to `processing`.

R2 helper:

- `backend/app/services/storage/r2.py`
- Existing functions:
  - `upload_file(...)`
  - `download_file(...)`
  - `delete_file(...)`
  - `get_presigned_url(...)` for downloads only
  - `build_raw_key(...)`
  - `build_layout_key(...)`

Frontend upload:

- `frontend/src/api/auth.js`
- `bucketApi.uploadFiles(bucketId, files)` creates `FormData`, appends each file as `files`, and posts to `/buckets/{bucketId}/files`.

Frontend callers:

- `frontend/src/App.jsx`
- Main upload paths call `bucketApi.uploadFiles(...)`.
- UI already has file list refresh, thread scope updates, pending upload state, and processing polling.

Plan limits today:

- `backend/app/services/plans.py`
- Individual: 5 GB total storage, 100 documents.
- Team: 15 GB total storage, 300 documents.
- Enterprise: 1 TB total storage, 100,000 documents.
- Enterprise supports admin `limits_override`.

Quota enforcement today:

- `backend/app/services/quota.py`
- `enforce_upload_quota(...)` checks document count and total storage only.
- There is no per-file size limit yet.

## Product Limit Recommendation

Do not market this as unlimited. Use plan-based limits with Enterprise overrides.

Suggested defaults:

- Individual: 100 MB per file.
- Team: 5 GB per file.
- Enterprise: 100 GB per file.
- Enterprise custom: higher by contract.

R2 multipart can technically support very large objects, but product limits must protect cost, abuse, processing time, and support expectations.

Add `max_file_size_bytes` to plan limits so users get a clear plan-limit message before upload starts.

## Backend Work

### 1. Extend plan limits

Update:

- `backend/app/services/plans.py`
- `backend/app/services/quota.py`
- `backend/app/api/v1/endpoints/billing.py`
- `backend/app/api/v1/endpoints/admin.py`
- frontend plan/admin UI fields in `frontend/src/App.jsx`

Add:

```python
max_file_size_bytes: int
```

Suggested values:

```python
individual = 100 * _MB
team = 5 * _GB
business = 100 * _GB
```

Add this field to `_OVERRIDABLE` so Enterprise accounts can be customized.

Add validation in upload-start endpoint:

- reject if `file.size > max_file_size_bytes`
- reject if current storage + incoming file size exceeds `max_storage_bytes`
- reject if doc count + incoming file count exceeds `max_documents`

### 2. Add R2 presigned upload helpers

Update:

- `backend/app/services/storage/r2.py`

Add single-part presign:

- `create_presigned_put_url(key, content_type, expires_in=900)`
- use `client.generate_presigned_url("put_object", Params={Bucket, Key, ContentType}, ExpiresIn=...)`

Add multipart helpers:

- `create_multipart_upload(key, content_type) -> upload_id`
- `create_presigned_upload_part_url(key, upload_id, part_number, expires_in=900)`
- `complete_multipart_upload(key, upload_id, parts)`
- `abort_multipart_upload(key, upload_id)`
- `head_object(key)` to verify size, content type, and existence

Use multipart for files over 100 MB. Single PUT is acceptable below 100 MB.

### 3. Add upload-session endpoints

Create new endpoints in `backend/app/api/v1/endpoints/files.py`, or a separate `uploads.py` router if preferred.

Recommended API:

```text
POST /v1/buckets/{bucket_id}/uploads/init
POST /v1/buckets/{bucket_id}/uploads/{upload_id}/parts
POST /v1/buckets/{bucket_id}/uploads/{upload_id}/complete
POST /v1/buckets/{bucket_id}/uploads/{upload_id}/abort
```

`init` request:

```json
{
  "filename": "big.pdf",
  "content_type": "application/pdf",
  "size": 1234567890
}
```

`init` response for small file:

```json
{
  "mode": "single",
  "upload_id": "app-upload-session-id",
  "file_id": "uuid",
  "r2_key": "raw/{file_id}/v1/big.pdf",
  "url": "presigned-put-url",
  "expires_in": 900
}
```

`init` response for large file:

```json
{
  "mode": "multipart",
  "upload_id": "app-upload-session-id",
  "file_id": "uuid",
  "r2_key": "raw/{file_id}/v1/big.pdf",
  "r2_upload_id": "r2-multipart-id",
  "part_size": 16777216,
  "expires_in": 900
}
```

`parts` request:

```json
{
  "part_numbers": [1, 2, 3]
}
```

`parts` response:

```json
{
  "parts": [
    { "part_number": 1, "url": "..." },
    { "part_number": 2, "url": "..." }
  ]
}
```

`complete` request:

```json
{
  "parts": [
    { "PartNumber": 1, "ETag": "\"etag-from-r2\"" }
  ]
}
```

`complete` should:

1. Complete multipart upload if needed.
2. `HEAD` the R2 object.
3. Verify size matches the original requested size.
4. Create `files` row and `file_versions` row.
5. Log `upload_completed`.
6. Set status to `processing`.
7. Log `file_processing_started`.
8. Start `process_file(file_id, trace_run_id, "upload")`.
9. Return the same `FileUploadResponse` shape currently returned by `POST /files`.

### 4. Track upload sessions

Add a small DB table via Alembic migration.

Suggested table: `upload_sessions`

Fields:

- `id` UUID primary key
- `file_id` UUID unique not null
- `bucket_id` UUID not null
- `user_id` UUID not null
- `filename` text not null
- `content_type` text not null
- `size` bigint not null
- `r2_key` text not null
- `mode` text not null: `single` or `multipart`
- `r2_upload_id` text nullable
- `status` text not null: `initiated`, `uploaded`, `completed`, `aborted`, `failed`
- `created_at`
- `expires_at`
- `completed_at`

Reason:

- Lets backend validate completion.
- Lets frontend retry/resume within a short window.
- Lets cleanup abort old multipart uploads.

### 5. Keep the existing upload endpoint temporarily

Do not delete `POST /v1/buckets/{bucket_id}/files` immediately.

Keep it for:

- backwards compatibility
- very small uploads if needed
- fast rollback

But frontend should move to the new direct-R2 flow.

## Frontend Work

### 1. Add upload API methods

Update:

- `frontend/src/api/auth.js`

Add:

- `initUpload(bucketId, file)`
- `getUploadPartUrls(bucketId, uploadSessionId, partNumbers)`
- `completeUpload(bucketId, uploadSessionId, parts)`
- `abortUpload(bucketId, uploadSessionId)`

Keep auth headers only for backend calls. The direct R2 `PUT` calls use the presigned URLs and should not include app auth headers.

### 2. Implement direct upload client

Create helper:

- `frontend/src/api/uploads.js` or local helper near `auth.js`

Behavior:

- If `mode === "single"`:
  - `PUT` file to presigned URL.
  - Include matching `Content-Type`.
  - Call complete endpoint.

- If `mode === "multipart"`:
  - Split the file into chunks.
  - Recommended part size: 16 MB or 32 MB.
  - Upload 3-5 parts concurrently.
  - Collect `ETag` response header for each part.
  - Call complete endpoint with ordered parts.

Support:

- progress percentage
- cancel/abort
- retry failed parts
- user-facing plan-limit errors from backend

### 3. Replace current upload calls

Update:

- `frontend/src/App.jsx`

Replace direct calls to:

```js
bucketApi.uploadFiles(bucketId, files)
```

with a new helper that loops files through direct-R2 upload and returns the same uploaded file response array.

This keeps existing downstream UI behavior:

- refresh file list
- update thread scope
- show processing state
- poll until ready/failed

## Processing Pipeline

No major pipeline rewrite should be needed.

Existing processing reads raw objects from R2 through `download_file(row.r2_path)`. The new complete endpoint must create the same `files.r2_path` format and status transitions the current `intake_upload(...)` creates.

To reduce duplicated logic, refactor `backend/app/services/pipeline/upload.py`:

- keep `intake_upload(...)` for legacy multipart form uploads
- add `finalize_r2_upload(...)` for direct-to-R2 uploads
- share DB row creation, version row creation, event logging, and status transition code

## R2 CORS

R2 bucket CORS must allow browser uploads from:

- `https://aiveilix-499209.web.app`
- future custom domain
- local dev origin if needed

Allowed methods:

- `PUT`
- `POST` if using multipart POST operations through presigned URLs
- `GET`
- `HEAD`

Allowed headers:

- `Content-Type`
- any `x-amz-*` headers used by the SDK/signature flow

Expose headers:

- `ETag`

Without exposing `ETag`, browser multipart completion cannot reliably collect part ETags.

## Security Requirements

- Never send R2 secret keys to frontend.
- Presigned URLs expire quickly, around 15 minutes.
- Object keys must be generated by backend, not trusted from frontend.
- Verify the object with `HEAD` before DB finalization.
- Verify exact file size on complete.
- Enforce plan and permission checks before signing.
- Abort incomplete multipart uploads when user cancels or session expires.
- Rate-limit upload init endpoints.
- Sanitize filenames for object keys and UI display.

## Tests

Backend unit tests:

- plan limit blocks oversize file before signing
- storage quota blocks before signing
- document count blocks before signing
- init creates upload session
- complete verifies object size and creates `files` + `file_versions`
- complete starts processing task
- abort marks session aborted and calls R2 abort for multipart

Frontend tests/manual QA:

- small PDF upload still works
- file over old Cloud Run limit uploads successfully
- multipart progress updates
- cancel upload aborts cleanly
- failed part retries
- plan limit message appears before upload begins
- completed upload appears in file list and reaches processing/ready

Production verification:

- Upload 5 MB PDF.
- Upload 100 MB PDF.
- Upload 1 GB test file on Enterprise.
- Confirm backend logs show `init`, `complete`, and processing, not raw file POST body.
- Confirm Cloud Run no longer receives large upload payloads.
- Confirm R2 object size matches uploaded file size.

## Rollout Plan

1. Add backend helpers, DB table, and endpoints behind current auth.
2. Add frontend direct upload helper.
3. Route only large files through direct-to-R2 first, keep small files on old endpoint.
4. Test with 100 MB and 1 GB files.
5. Move all uploads to direct-to-R2.
6. Keep old endpoint for one release.
7. Remove or admin-disable old endpoint after production confidence.

## Acceptance Criteria

- A file larger than 32 MiB uploads successfully from Firebase Hosting.
- Cloud Run logs do not show large `POST /files` request bodies.
- Backend still owns auth, quota, DB records, and processing state.
- Enterprise file-size limit can be changed from admin override.
- User gets a clear message if plan limit is exceeded before the upload starts.
- Existing file processing pipeline continues to work from R2.
