// Direct-to-R2 upload client.
//
// The browser uploads raw file bytes straight to Cloudflare R2 using presigned
// URLs, so large files never pass through Cloud Run (which caps request bodies
// at 32 MiB). The backend still owns auth, plan/quota, the object key,
// verification, and the DB records — those go through bucketApi (api/auth.js).
//
// IMPORTANT: the raw PUTs to R2 must NOT carry app auth headers — the presigned
// URL is itself the credential. Only the init/parts/complete/abort calls are
// authenticated backend calls.

import { bucketApi } from './auth';

const PART_BATCH = 50;        // how many part URLs to request per /parts call
const PART_CONCURRENCY = 5;   // parallel part uploads within a batch
const MAX_PART_RETRIES = 3;

// Raw PUT to a presigned R2 URL. The URL is the credential; no auth headers.
async function putToR2(url, body, { contentType, signal } = {}) {
  const headers = {};
  if (contentType) headers['Content-Type'] = contentType;
  const res = await fetch(url, { method: 'PUT', headers, body, signal });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Upload to storage failed (${res.status}). ${text.slice(0, 200)}`.trim());
  }
  return res;
}

function planParts(fileSize, partSize) {
  const parts = [];
  let offset = 0;
  let number = 1;
  while (offset < fileSize) {
    const end = Math.min(offset + partSize, fileSize);
    parts.push({ partNumber: number, start: offset, end });
    offset = end;
    number += 1;
  }
  return parts;
}

async function fetchPartUrls(bucketId, uploadId, numbers) {
  const resp = await bucketApi.getUploadPartUrls(bucketId, uploadId, numbers);
  const map = new Map();
  (resp.parts || []).forEach((p) => map.set(p.part_number, p.url));
  return map;
}

async function uploadPartWithRetry(bucketId, uploadId, part, blob, urlMap, signal) {
  let lastErr;
  for (let attempt = 0; attempt < MAX_PART_RETRIES; attempt += 1) {
    if (signal?.aborted) throw new DOMException('Upload cancelled', 'AbortError');
    try {
      let url = urlMap.get(part.partNumber);
      if (!url) {
        const refreshed = await fetchPartUrls(bucketId, uploadId, [part.partNumber]);
        url = refreshed.get(part.partNumber);
        urlMap.set(part.partNumber, url);
      }
      const res = await putToR2(url, blob, { signal });
      // Needs R2 CORS to expose the ETag response header.
      const etag = res.headers.get('ETag') || res.headers.get('etag');
      if (!etag) {
        throw new Error('Storage did not return an ETag (R2 bucket CORS must expose ETag).');
      }
      return etag;
    } catch (err) {
      if (err.name === 'AbortError') throw err;
      lastErr = err;
      urlMap.delete(part.partNumber); // force a fresh presigned URL next attempt
      await new Promise((r) => setTimeout(r, 400 * (attempt + 1)));
    }
  }
  throw lastErr || new Error(`Part ${part.partNumber} failed to upload.`);
}

async function uploadMultipart(bucketId, file, init, opts) {
  const uploadId = init.upload_id;
  const partSize = init.part_size;
  const signal = opts.signal;
  const partsMeta = planParts(file.size, partSize);
  const etags = new Array(partsMeta.length);
  let loaded = 0;

  for (let i = 0; i < partsMeta.length; i += PART_BATCH) {
    if (signal?.aborted) throw new DOMException('Upload cancelled', 'AbortError');
    const batch = partsMeta.slice(i, i + PART_BATCH);
    const urlMap = await fetchPartUrls(bucketId, uploadId, batch.map((p) => p.partNumber));

    let cursor = 0;
    const worker = async () => {
      while (cursor < batch.length) {
        const p = batch[cursor];
        cursor += 1;
        const blob = file.slice(p.start, p.end);
        const etag = await uploadPartWithRetry(bucketId, uploadId, p, blob, urlMap, signal);
        etags[p.partNumber - 1] = etag;
        loaded += p.end - p.start;
        opts.onProgress?.({ loaded, total: file.size });
      }
    };
    await Promise.all(
      Array.from({ length: Math.min(PART_CONCURRENCY, batch.length) }, worker),
    );
  }

  const parts = etags.map((etag, idx) => ({ PartNumber: idx + 1, ETag: etag }));
  return bucketApi.completeUpload(bucketId, uploadId, parts);
}

async function uploadSingle(bucketId, file, init, opts) {
  // Content-Type must match what the backend signed (file.type || octet-stream).
  const contentType = file.type || 'application/octet-stream';
  await putToR2(init.url, file, { contentType, signal: opts.signal });
  opts.onProgress?.({ loaded: file.size, total: file.size });
  return bucketApi.completeUpload(bucketId, init.upload_id, []);
}

// Upload a single File directly to R2. Returns the FileUploadResponse the
// backend produces on completion (same shape as the legacy upload endpoint).
export async function uploadFileDirect(bucketId, file, opts = {}) {
  const init = await bucketApi.initUpload(bucketId, file);
  try {
    if (init.mode === 'multipart') return await uploadMultipart(bucketId, file, init, opts);
    return await uploadSingle(bucketId, file, init, opts);
  } catch (err) {
    // Best-effort: free the session and drop any partial multipart data in R2.
    try { await bucketApi.abortUpload(bucketId, init.upload_id); } catch (_) { /* ignore */ }
    throw err;
  }
}

// Drop-in replacement for bucketApi.uploadFiles(bucketId, files): uploads each
// file directly to R2 and resolves to the same array of FileUploadResponse
// objects, so existing callers (file-list refresh, thread scope, polling) work
// unchanged. A 402 plan-limit error from init is thrown before any bytes move.
export async function uploadFilesDirect(bucketId, files, opts = {}) {
  const list = Array.from(files || []);
  const results = [];
  for (let i = 0; i < list.length; i += 1) {
    const file = list[i];
    const res = await uploadFileDirect(bucketId, file, {
      ...opts,
      onProgress: opts.onProgress
        ? (p) => opts.onProgress({ ...p, file, fileIndex: i, fileCount: list.length })
        : undefined,
    });
    results.push(res);
  }
  return results;
}
