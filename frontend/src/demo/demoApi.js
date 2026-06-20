// Public Demo Bucket API client.
//
// A standalone, isolated client for the /v1/demo/* endpoints. It holds the demo
// session token (per-tab, in sessionStorage) and is completely separate from the
// main app's auth — a demo visitor is never a logged-in user.

const BASE = import.meta.env.VITE_API_URL;
const TOKEN_KEY = 'aiveilix-demo-token';

export function getDemoToken() {
  try { return sessionStorage.getItem(TOKEN_KEY) || null; } catch { return null; }
}
export function setDemoToken(token) {
  try {
    if (!token) sessionStorage.removeItem(TOKEN_KEY);
    else sessionStorage.setItem(TOKEN_KEY, token);
  } catch { /* storage unavailable */ }
}
export function clearDemoToken() { setDemoToken(null); }

// A demo limit was hit (HTTP 409 { detail: { limit } }) — callers catch this and
// open the "let's talk" pop-up. Other errors carry a human message.
export class DemoLimitError extends Error {
  constructor(limit) {
    super('demo-limit');
    this.name = 'DemoLimitError';
    this.limit = limit;
  }
}

function buildError(status, data) {
  const detail = data?.detail;
  if (status === 409 && detail && typeof detail === 'object' && detail.limit) {
    return new DemoLimitError(detail.limit);
  }
  const msg = typeof detail === 'string' ? detail : 'Something went wrong. Please try again.';
  const err = new Error(msg);
  err.status = status;
  return err;
}

async function req(method, path, body, { auth = false } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (auth) {
    const t = getDemoToken();
    if (t) headers['Authorization'] = `Bearer ${t}`;
  }
  const res = await fetch(`${BASE}/v1/demo${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw buildError(res.status, data);
  return data;
}

export const demoApi = {
  // ── entry ──
  verifyCode: (slug, code) => req('POST', `/${encodeURIComponent(slug)}/verify-code`, { code }),
  enter: async (slug, { code, name, email, role }) => {
    const data = await req('POST', `/${encodeURIComponent(slug)}/enter`, { code, name, email, role });
    if (data.token) setDemoToken(data.token);
    return data;
  },
  inviteInfo: (token) => req('GET', `/invite/${encodeURIComponent(token)}`),
  inviteAccept: async (token) => {
    const data = await req('POST', `/invite/${encodeURIComponent(token)}/accept`);
    if (data.token) setDemoToken(data.token);
    return data;
  },

  // ── session ──
  me: () => req('GET', '/me', null, { auth: true }),
  files: () => req('GET', '/files', null, { auth: true }),

  // ── threads ──
  listConversations: () => req('GET', '/conversations', null, { auth: true }),
  createConversation: (title) => req('POST', '/conversations', { title }, { auth: true }),
  getMessages: (convId) => req('GET', `/conversations/${convId}/messages`, null, { auth: true }),
  sendMessage: (convId, content, webSearch) =>
    req('POST', `/conversations/${convId}/messages`, { content, web_search: webSearch ?? null }, { auth: true }),

  // ── per-thread file filter (scope) ──
  getScope: (convId) => req('GET', `/conversations/${convId}/scope`, null, { auth: true }),
  setScope: (convId, fileIds, scoped) =>
    req('PUT', `/conversations/${convId}/scope`, { file_ids: fileIds, scoped }, { auth: true }),

  // ── streaming chat (SSE) ──
  sendMessageStream: async (convId, content, { onStep, onToken, onPlan, webSearch } = {}) => {
    const headers = { 'Content-Type': 'application/json' };
    const t = getDemoToken();
    if (t) headers['Authorization'] = `Bearer ${t}`;
    const res = await fetch(`${BASE}/v1/demo/conversations/${convId}/messages/stream`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ content, web_search: webSearch ?? null }),
    });
    if (!res.ok || !res.body) {
      const data = await res.json().catch(() => ({}));
      throw buildError(res.status, data);
    }
    const reader = res.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buf = '';
    let finalResult = null;
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      let sep;
      while ((sep = buf.indexOf('\n\n')) !== -1) {
        const raw = buf.slice(0, sep);
        buf = buf.slice(sep + 2);
        const line = raw.split('\n').find((l) => l.startsWith('data:'));
        if (!line) continue;
        let payload;
        try { payload = JSON.parse(line.slice(5).trim()); } catch { continue; }
        if (payload.kind === 'token' && onToken) onToken(payload.text || '');
        else if (payload.kind === 'plan_update' && onPlan) onPlan(payload.plan || []);
        else if (payload.kind === 'step' && onStep) onStep(payload.event);
        else if (payload.kind === 'done') finalResult = payload.result;
        else if (payload.kind === 'error') {
          if (payload.status === 409 && payload.detail && payload.detail.limit) {
            throw new DemoLimitError(payload.detail.limit);
          }
          const m = typeof payload.detail === 'string' ? payload.detail : 'The assistant could not reply.';
          throw new Error(m);
        }
      }
    }
    if (!finalResult) throw new Error('The reply ended unexpectedly. Please try again.');
    return finalResult;
  },

  // ── upload (multipart) ──
  upload: async (file) => {
    const headers = {};
    const t = getDemoToken();
    if (t) headers['Authorization'] = `Bearer ${t}`;
    const fd = new FormData();
    fd.append('file', file);
    const res = await fetch(`${BASE}/v1/demo/upload`, { method: 'POST', headers, body: fd });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw buildError(res.status, data);
    return data;
  },

  // ── team / survey / meeting / events / mcp ──
  teamInvite: (payload) => req('POST', '/team-invite', payload, { auth: true }),
  team: () => req('GET', '/team', null, { auth: true }),
  survey: (payload) => req('POST', '/survey', payload, { auth: true }),
  meeting: (payload) => req('POST', '/meeting', payload, { auth: true }),
  event: (eventType, payload) => req('POST', '/event', { event_type: eventType, payload }, { auth: true }),
  mcp: () => req('GET', '/mcp', null, { auth: true }),

  // fire-and-forget event (never throws — used in idle/popup tracking)
  logEvent: (eventType, payload) => {
    try { return demoApi.event(eventType, payload).catch(() => {}); } catch { return Promise.resolve(); }
  },
};
