const BASE = import.meta.env.VITE_API_URL;

async function request(method, path, body, token) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${BASE}/v1${path}`, {
    method,
    headers,
    body: body !== undefined && body !== null ? JSON.stringify(body) : undefined,
  });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data?.detail || 'Something went wrong.');
  return data;
}

function authToken() {
  return sessionStorage.getItem('access_token');
}

export const teamApi = {
  getMe: () => request('GET', '/user/me', null, authToken()),

  // Activity feed (owner-only)
  getActivity: () => request('GET', '/team/activity', null, authToken()),

  // Team management (owner-only)
  inviteMember: (payload) => request('POST', '/team/invite', payload, authToken()),
  listMembers: () => request('GET', '/team/members', null, authToken()),
  getMember: (memberId) => request('GET', `/team/members/${memberId}`, null, authToken()),
  updateMember: (memberId, payload) =>
    request('PATCH', `/team/members/${memberId}`, payload, authToken()),
  deleteMember: (memberId) =>
    request('DELETE', `/team/members/${memberId}`, null, authToken()),
  resendInvite: (memberId) =>
    request('POST', `/team/members/${memberId}/resend-invite`, null, authToken()),

  // Bucket access (owner-only)
  listBucketAccess: (bucketId) =>
    request('GET', `/team/buckets/${bucketId}/access`, null, authToken()),
  grantBucketAccess: (bucketId, payload) =>
    request('POST', `/team/buckets/${bucketId}/access`, payload, authToken()),
  updateBucketAccess: (bucketId, teamMemberId, permissions) =>
    request(
      'PATCH',
      `/team/buckets/${bucketId}/access/${teamMemberId}`,
      { permissions },
      authToken(),
    ),
  revokeBucketAccess: (bucketId, teamMemberId) =>
    request(
      'DELETE',
      `/team/buckets/${bucketId}/access/${teamMemberId}`,
      null,
      authToken(),
    ),

  // Public — invite accept
  validateInvite: (token) => request('GET', `/team/invite/${token}`),
  acceptInvite: (token, password) =>
    request('POST', `/team/invite/${token}/accept`, { password }),
};

export const DEFAULT_BUCKET_PERMISSIONS = Object.freeze({
  history_scope: 'from_now',
  can_see_other_members: false,
  can_upload_files: false,
  can_download_files: false,
  can_delete_files: false,
  can_use_mcp: false,
});

export const PERMISSION_LABELS = Object.freeze({
  can_see_other_members: 'See other team members (names + colors on bubbles)',
  can_use_mcp: 'Use MCP tools',
  can_upload_files: 'Upload files',
  can_download_files: 'Download files',
  can_delete_files: 'Delete files',
});

export const HISTORY_SCOPE_OPTIONS = Object.freeze([
  {
    value: 'from_now',
    label: 'From now on only',
    description: "Member sees only threads they create after joining.",
  },
  {
    value: 'all',
    label: 'Include all existing threads too',
    description: "Member can read your past threads and other members' threads in this bucket.",
  },
]);
