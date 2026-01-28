// Frontend config - reads from Vite env or defaults
export const config = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:7223',
  appUrl: import.meta.env.VITE_APP_URL || 'http://localhost:6677', // Frontend origin for OAuth redirect URIs
  supabaseUrl: import.meta.env.VITE_SUPABASE_URL || '',
  supabaseAnonKey: import.meta.env.VITE_SUPABASE_ANON_KEY || '',
}
