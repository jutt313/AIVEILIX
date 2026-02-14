// Frontend config - auto-detect API URL based on hostname
function getApiUrl() {
  if (import.meta.env.VITE_API_URL) return import.meta.env.VITE_API_URL;
  const host = window.location.hostname;
  // Production: Firebase or custom domain → use production API
  if (host === 'aiveilix.com' || host === 'www.aiveilix.com' ||
      host === 'aiveilix-427f3.web.app' || host === 'aiveilix-427f3.firebaseapp.com') {
    return 'https://api.aiveilix.com';
  }
  // Default: local development
  return 'http://localhost:7223';
}

function getAppUrl() {
  if (import.meta.env.VITE_APP_URL) return import.meta.env.VITE_APP_URL;
  return window.location.origin;
}

export const config = {
  apiUrl: getApiUrl(),
  appUrl: getAppUrl(),
  supabaseUrl: import.meta.env.VITE_SUPABASE_URL || '',
  supabaseAnonKey: import.meta.env.VITE_SUPABASE_ANON_KEY || '',
}
