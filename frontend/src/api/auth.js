const BASE = import.meta.env.VITE_API_URL;

// When the backend rejects an action for hitting a plan limit (HTTP 402),
// broadcast it so the global <UpgradeModal/> can show the upgrade popup.
function emitLimitHit(data) {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('aiveilix:limit-hit', {
      detail: { message: (data && data.detail) || "You've reached a plan limit." },
    }));
  }
}

// Which workspace the user is currently acting in: 'self' (own account) or a
// workspace owner's id. Sent as the X-Workspace header so the backend resolves
// the right context. Unset = backend default (a user's single membership).
const ACTIVE_WORKSPACE_KEY = 'aiveilix-active-workspace';

export function getActiveWorkspace() {
  try { return localStorage.getItem(ACTIVE_WORKSPACE_KEY) || null; } catch { return null; }
}

export function setActiveWorkspace(id) {
  try {
    if (!id) localStorage.removeItem(ACTIVE_WORKSPACE_KEY);
    else localStorage.setItem(ACTIVE_WORKSPACE_KEY, id);
  } catch { /* storage unavailable — ignore */ }
}

async function request(method, path, body, token, signal) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const ws = getActiveWorkspace();
  if (ws) headers['X-Workspace'] = ws;
  const res = await fetch(`${BASE}/v1${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
    signal,
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    if (res.status === 402) emitLimitHit(data);
    throw new Error(data?.detail || 'Something went wrong. Please try again.');
  }

  return data;
}

async function requestForm(method, path, formData, token) {
  const headers = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  const ws = getActiveWorkspace();
  if (ws) headers['X-Workspace'] = ws;
  const res = await fetch(`${BASE}/v1${path}`, {
    method,
    headers,
    body: formData,
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    if (res.status === 402) emitLimitHit(data);
    throw new Error(data?.detail || 'Something went wrong. Please try again.');
  }

  return data;
}

export const authApi = {
  register: (fullName, email, password) =>
    request('POST', '/auth/register', { full_name: fullName, email, password }),

  login: (email, password) =>
    request('POST', '/auth/login', { email, password }),

  logout: () => {
    const accessToken = sessionStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    return request('POST', '/auth/logout', { refresh_token: refreshToken || '' }, accessToken);
  },

  forgotPassword: (email) =>
    request('POST', '/auth/forgot-password', { email }),

  resendVerification: (email) =>
    request('POST', '/auth/resend-verification', { email }),

  verifyEmail: (token) =>
    request('POST', '/auth/verify-email', { token }),

  resetPassword: (token, newPassword) =>
    request('POST', '/auth/reset-password', { token, new_password: newPassword }),

  getOAuthAuthorizeUrl: (provider, redirectUri, mode = 'login', stateToken = '') => {
    const params = new URLSearchParams({ redirect_uri: redirectUri, mode });
    if (stateToken) params.set('state_token', stateToken);
    return request('GET', `/auth/${provider}/authorize-url?${params.toString()}`);
  },

  exchangeOAuth: (provider, code, redirectUri) =>
    request('POST', `/auth/${provider}`, { code, redirect_uri: redirectUri }),

  saveOnboarding: (useCase, need, referralSource) => {
    const token = sessionStorage.getItem('access_token');
    return request('POST', '/user/onboarding', { use_case: useCase, need, referral_source: referralSource }, token);
  },
};

// Sign the user out everywhere: best-effort backend logout (blacklists the
// access token + drops the refresh token server-side), then clear all local
// auth state. Always resolves — callers navigate to /login afterward.
export async function signOut() {
  try {
    await authApi.logout();
  } catch {
    // Token may already be expired/invalid — clear local state regardless.
  }
  sessionStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

function authToken() {
  return sessionStorage.getItem('access_token');
}

export const bucketApi = {
  get: (bucketId) => request('GET', `/buckets/${bucketId}`, null, authToken()),
  listConversations: (bucketId) =>
    request('GET', `/buckets/${bucketId}/conversations`, null, authToken()),
  createConversation: (bucketId, title) =>
    request('POST', `/buckets/${bucketId}/conversations`, { title }, authToken()),
  deleteConversation: (bucketId, convId) =>
    request('DELETE', `/buckets/${bucketId}/conversations/${convId}`, null, authToken()),
  getMessages: (bucketId, convId) =>
    request('GET', `/buckets/${bucketId}/conversations/${convId}/messages`, null, authToken()),
  sendMessage: (bucketId, convId, content, signal, opts = {}) =>
    request('POST', `/buckets/${bucketId}/conversations/${convId}/messages`, { content, web_search: opts.webSearch ?? null, agentic_mode: opts.agenticMode ?? null }, authToken(), signal),
  sendMessageStream: async (
    bucketId, convId, content, signal, opts = {},
    { onStep, onPlan, onToken } = {},
  ) => {
    const token = authToken();
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const ws = getActiveWorkspace();
    if (ws) headers['X-Workspace'] = ws;
    const res = await fetch(`${BASE}/v1/buckets/${bucketId}/conversations/${convId}/messages/stream`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ content, web_search: opts.webSearch ?? null, agentic_mode: opts.agenticMode ?? null }),
      signal,
    });
    if (!res.ok || !res.body) {
      const data = await res.json().catch(() => ({}));
      if (res.status === 402) emitLimitHit(data);
      throw new Error(data?.detail || 'Something went wrong. Please try again.');
    }
    const reader = res.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buf = '';
    let finalResult = null;
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      // SSE events are separated by a blank line; each "data:" line carries one JSON message
      let sepIdx;
      while ((sepIdx = buf.indexOf('\n\n')) !== -1) {
        const raw = buf.slice(0, sepIdx);
        buf = buf.slice(sepIdx + 2);
        const line = raw.split('\n').find(l => l.startsWith('data:'));
        if (!line) continue;
        let payload;
        try { payload = JSON.parse(line.slice(5).trim()); } catch { continue; }
        if (payload.kind === 'step' && onStep) {
          onStep(payload.event);
        } else if (payload.kind === 'plan_update' && onPlan) {
          onPlan(payload.plan || []);
        } else if (payload.kind === 'token' && onToken) {
          onToken(payload.text || '');
        } else if (payload.kind === 'done') {
          finalResult = payload.result;
        } else if (payload.kind === 'error') {
          throw new Error(payload.message || 'AI reply failed.');
        }
      }
    }
    if (!finalResult) throw new Error('Stream ended without a final result.');
    return finalResult;
  },
  deleteMessagesFrom: (bucketId, convId, messageId) =>
    request('DELETE', `/buckets/${bucketId}/conversations/${convId}/messages/from/${messageId}`, null, authToken()),
  submitFeedback: (bucketId, convId, messageId, rating, reason) =>
    request('POST', `/buckets/${bucketId}/conversations/${convId}/messages/${messageId}/feedback`, { rating, reason: reason || null }, authToken()),
  saveMessageAsFile: (bucketId, convId, messageId, fileName, content) =>
    request('POST', `/buckets/${bucketId}/conversations/${convId}/messages/${messageId}/save-as-file`, { file_name: fileName, content }, authToken()),
  getThreadScope: (bucketId, convId) =>
    request('GET', `/buckets/${bucketId}/conversations/${convId}/scope`, null, authToken()),
  setThreadScope: (bucketId, convId, fileIds, scoped) =>
    request('PUT', `/buckets/${bucketId}/conversations/${convId}/scope`, { file_ids: fileIds, scoped }, authToken()),
  listFiles: (bucketId) =>
    request('GET', `/buckets/${bucketId}/files`, null, authToken()),
  getFile: (bucketId, fileId) =>
    request('GET', `/buckets/${bucketId}/files/${fileId}`, null, authToken()),
  getFileLayout: (bucketId, fileId) =>
    request('GET', `/buckets/${bucketId}/files/${fileId}/layout`, null, authToken()),
  listFileChunks: (bucketId, fileId) =>
    request('GET', `/buckets/${bucketId}/files/${fileId}/chunks`, null, authToken()),
  listFileEvents: (bucketId, fileId) =>
    request('GET', `/buckets/${bucketId}/files/${fileId}/events`, null, authToken()),
  // Legacy multipart-form upload: the whole file is POSTed through the API.
  // Kept for backwards-compat/rollback; the app now uploads via uploadFilesDirect
  // (api/uploads.js), which streams bytes straight to R2 and avoids the Cloud Run
  // 32 MiB request-size limit.
  uploadFiles: (bucketId, files) => {
    const fd = new FormData();
    files.forEach(f => fd.append('files', f));
    return requestForm('POST', `/buckets/${bucketId}/files`, fd, authToken());
  },

  // ── Direct-to-R2 upload session API ──
  // These hit the backend (auth + quota + presigning); the raw bytes go straight
  // browser→R2 via the presigned URLs returned here (see api/uploads.js).
  initUpload: (bucketId, file) =>
    request('POST', `/buckets/${bucketId}/uploads/init`, {
      filename: file.name,
      content_type: file.type || 'application/octet-stream',
      size: file.size,
    }, authToken()),
  getUploadPartUrls: (bucketId, uploadId, partNumbers) =>
    request('POST', `/buckets/${bucketId}/uploads/${uploadId}/parts`, { part_numbers: partNumbers }, authToken()),
  completeUpload: (bucketId, uploadId, parts) =>
    request('POST', `/buckets/${bucketId}/uploads/${uploadId}/complete`, { parts }, authToken()),
  abortUpload: (bucketId, uploadId) =>
    request('POST', `/buckets/${bucketId}/uploads/${uploadId}/abort`, {}, authToken()),
  deleteFile: (bucketId, fileId) =>
    request('DELETE', `/buckets/${bucketId}/files/${fileId}`, null, authToken()),
  downloadFile: async (bucketId, fileId, filename) => {
    const dlHeaders = { Authorization: `Bearer ${authToken()}` };
    const ws = getActiveWorkspace();
    if (ws) dlHeaders['X-Workspace'] = ws;
    const res = await fetch(`${BASE}/v1/buckets/${bucketId}/files/${fileId}/download`, {
      headers: dlHeaders,
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data?.detail || 'Could not download file.');
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename || 'download';
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  },
  renameConversation: (bucketId, convId, title) =>
    request('PATCH', `/buckets/${bucketId}/conversations/${convId}`, { title }, authToken()),
  autoTitleConversation: (bucketId, convId, message) =>
    request('POST', `/buckets/${bucketId}/conversations/${convId}/auto-title`, { message }, authToken()),
  pinConversation: (bucketId, convId, isPinned) =>
    request('PATCH', `/buckets/${bucketId}/conversations/${convId}/pin`, { is_pinned: isPinned }, authToken()),
  replaceFile: (bucketId, fileId, file) => {
    const fd = new FormData();
    fd.append('file', file);
    return requestForm('POST', `/buckets/${bucketId}/files/${fileId}/replace`, fd, authToken());
  },

  // MCP token management
  listMcpTokens: (bucketId) =>
    request('GET', `/buckets/${bucketId}/mcp-tokens`, null, authToken()),
  createMcpToken: (bucketId, name, allowedTools, allowedOrigins) =>
    request('POST', `/buckets/${bucketId}/mcp-tokens`, { name, allowed_tools: allowedTools, allowed_origins: allowedOrigins }, authToken()),
  updateMcpToken: (bucketId, tokenId, payload) =>
    request('PATCH', `/buckets/${bucketId}/mcp-tokens/${tokenId}`, payload, authToken()),
  revokeMcpToken: (bucketId, tokenId) =>
    request('DELETE', `/buckets/${bucketId}/mcp-tokens/${tokenId}`, null, authToken()),
  getMcpTokenLogs: (bucketId, tokenId, limit = 100, offset = 0) =>
    request('GET', `/buckets/${bucketId}/mcp-tokens/${tokenId}/logs?limit=${limit}&offset=${offset}`, null, authToken()),
};

export const dashboardApi = {
  getProfile: () => request('GET', '/user/profile', null, authToken()),
  updateProfile: (payload) => request('PUT', '/user/profile', payload, authToken()),
  uploadAvatar: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return requestForm('PUT', '/user/avatar', formData, authToken());
  },
  getProviderConnectUrl: (provider, redirectUri, stateToken = '') => {
    const params = new URLSearchParams({ redirect_uri: redirectUri });
    if (stateToken) params.set('state_token', stateToken);
    return request('GET', `/user/auth-provider/${provider}/connect-url?${params.toString()}`, null, authToken());
  },
  connectAuthProvider: (provider, code, redirectUri) =>
    request('POST', `/user/auth-provider/${provider}`, { code, redirect_uri: redirectUri }, authToken()),
  disconnectAuthProvider: (provider) =>
    provider
      ? request('DELETE', `/user/auth-provider/${provider}`, null, authToken())
      : request('DELETE', '/user/auth-provider', null, authToken()),
  changePassword: (currentPassword, newPassword) =>
    request('PUT', '/user/password', { current_password: currentPassword, new_password: newPassword }, authToken()),
  deleteAccount: (password) => request('DELETE', '/user/account', { password }, authToken()),
  getStats: () => request('GET', '/user/stats', null, authToken()),
  getMonthlyStats: (startMonth, endMonth) => {
    const params = new URLSearchParams();
    if (startMonth) params.set('start_month', startMonth);
    if (endMonth) params.set('end_month', endMonth);
    const suffix = params.size ? `?${params.toString()}` : '';
    return request('GET', `/user/stats/monthly${suffix}`, null, authToken());
  },
  listBuckets: () => request('GET', '/buckets', null, authToken()),
  createBucket: (name, description, color, icon) =>
    request('POST', '/buckets', { name, description, color, icon }, authToken()),
  deleteBucket: (bucketId) => request('DELETE', `/buckets/${bucketId}`, null, authToken()),
  deleteAllBuckets: () => request('DELETE', '/buckets/all', null, authToken()),
  updateBucket: (bucketId, payload) => request('PUT', `/buckets/${bucketId}`, payload, authToken()),
  listAccountMcpTokens: () => request('GET', '/user/account-mcp-tokens', null, authToken()),
  createAccountMcpToken: (payload) => request('POST', '/user/account-mcp-tokens', payload, authToken()),
  updateAccountMcpToken: (tokenId, payload) => request('PATCH', `/user/account-mcp-tokens/${tokenId}`, payload, authToken()),
  deleteAccountMcpToken: (tokenId) => request('DELETE', `/user/account-mcp-tokens/${tokenId}`, null, authToken()),
  listNotifications: () => request('GET', '/notifications', null, authToken()),
  markAllRead: () => request('PUT', '/notifications/read-all', null, authToken()),
  markNotificationRead: (notificationId) => request('PATCH', `/notifications/${notificationId}/read`, null, authToken()),
  deleteNotification: (notificationId) => request('DELETE', `/notifications/${notificationId}`, null, authToken()),
  deleteAllNotifications: () => request('DELETE', '/notifications/all', null, authToken()),
};

export const billingApi = {
  getPlan: () => request('GET', '/billing/plan', null, authToken()),
  getHistory: () => request('GET', '/billing/history', null, authToken()),
  // Start a Stripe Checkout session for a paid plan; returns { url } to redirect to.
  createCheckout: (plan) => request('POST', '/billing/checkout', { plan }, authToken()),
  // Stripe Customer Portal (manage card / downgrade / cancel); returns { url }.
  openPortal: () => request('POST', '/billing/portal', {}, authToken()),
  cancelSubscription: () => request('POST', '/billing/cancel', {}, authToken()),
  // Manual "ask admin for more limits" flow (separate from paid-plan upgrades).
  requestUpgrade: (plan) => request('POST', '/billing/upgrade', plan ? { plan } : {}, authToken()),
  requestLimitIncrease: (requestedLimits, note, triggerMessage) =>
    request('POST', '/billing/limit-increase-requests', {
      requested_limits: requestedLimits,
      note: note || null,
      trigger_message: triggerMessage || null,
    }, authToken()),
};

// Verified admin actions carry the logged-in JWT + the short-lived X-Admin-Session token.
async function adminSessionRequest(method, path, body, session) {
  const headers = { 'Content-Type': 'application/json', 'X-Admin-Session': session || '' };
  const token = authToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${BASE}/v1${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data?.detail;
    throw new Error(typeof detail === 'string' ? detail : 'Request failed.');
  }
  return data;
}

// Verified admin multipart upload (prebuild demo files).
async function adminSessionForm(method, path, formData, session) {
  const headers = { 'X-Admin-Session': session || '' };
  const token = authToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${BASE}/v1${path}`, { method, headers, body: formData });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data?.detail;
    throw new Error(typeof detail === 'string' ? detail : 'Upload failed.');
  }
  return data;
}

export const adminApi = {
  // Step 1 — email + admin key → emails a 60-second 6-digit code.
  requestCode: (email, adminKey) => request('POST', '/admin/request-code', { email, admin_key: adminKey }, authToken()),
  // Step 2 — verify the code → returns { admin_session }.
  verifyCode: (code) => request('POST', '/admin/verify-code', { code }, authToken()),
  // Verified actions — carry the admin session token.
  lookup: (email, session) => adminSessionRequest('POST', '/admin/lookup', { email }, session),
  setPlan: (email, plan, status, limitsOverride, session) =>
    adminSessionRequest('POST', '/admin/set-plan', { email, plan, status, limits_override: limitsOverride }, session),
  listLimitRequests: (session, status = 'pending') =>
    adminSessionRequest('GET', `/admin/limit-requests?status=${encodeURIComponent(status)}`, null, session),
  listEnterpriseInquiries: (session, status = 'new') =>
    adminSessionRequest('GET', `/admin/enterprise-inquiries?status=${encodeURIComponent(status)}`, null, session),
  applyLimitRequest: (requestId, plan, limitsOverride, adminNote, session) =>
    adminSessionRequest('POST', `/admin/limit-requests/${requestId}/apply`, {
      plan,
      limits_override: limitsOverride,
      admin_note: adminNote || null,
    }, session),
  rejectLimitRequest: (requestId, adminNote, session) =>
    adminSessionRequest('POST', `/admin/limit-requests/${requestId}/reject`, {
      admin_note: adminNote || null,
    }, session),

  // ── Demo buckets ──
  listDemoBuckets: (session) => adminSessionRequest('GET', '/admin/demo-buckets', null, session),
  createDemoBucket: (payload, session) => adminSessionRequest('POST', '/admin/demo-buckets', payload, session),
  getDemoBucket: (id, session) => adminSessionRequest('GET', `/admin/demo-buckets/${id}`, null, session),
  updateDemoBucket: (id, payload, session) => adminSessionRequest('PATCH', `/admin/demo-buckets/${id}`, payload, session),
  deleteDemoBucket: (id, session) => adminSessionRequest('DELETE', `/admin/demo-buckets/${id}`, null, session),
  uploadDemoFiles: (id, files, session) => {
    const fd = new FormData();
    files.forEach((f) => fd.append('files', f));
    return adminSessionForm('POST', `/admin/demo-buckets/${id}/files`, fd, session);
  },
  getDemoActivity: (id, session) => adminSessionRequest('GET', `/admin/demo-buckets/${id}/activity`, null, session),
  listDemoMeetings: (session, status = 'pending') =>
    adminSessionRequest('GET', `/admin/demo-meetings?status=${encodeURIComponent(status)}`, null, session),
  updateDemoMeeting: (id, payload, session) => adminSessionRequest('PATCH', `/admin/demo-meetings/${id}`, payload, session),
};

export const enterpriseApi = {
  contact: (payload) => request('POST', '/enterprise/contact', payload, authToken()),
};
