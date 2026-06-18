import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { teamApi } from '../../api/team';
import { useAppTheme } from './theme';

export default function InviteAcceptPage() {
  const { token } = useParams();
  const navigate = useNavigate();
  const { theme, palette } = useAppTheme();
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    setLoading(true);
    teamApi
      .validateInvite(token)
      .then((data) => setInfo(data))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [token]);

  async function handleAccept(e) {
    e.preventDefault();
    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    if (password !== confirm) {
      setError('Passwords do not match.');
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      const result = await teamApi.acceptInvite(token, password);
      if (result.refresh_token) localStorage.setItem('refresh_token', result.refresh_token);
      sessionStorage.setItem('access_token', result.access_token);
      navigate('/dashboard', { replace: true });
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  const shellLight = 'border-slate-200 bg-white shadow-[0_24px_80px_rgba(148,163,184,0.22)]';
  const shellDark = `${palette.card} shadow-[0_24px_80px_rgba(2,6,23,0.6)]`;
  const inputCls = `w-full rounded-2xl border px-4 py-2.5 text-sm outline-none transition focus:ring-2 ${palette.input}`;
  const btnPrimary = `w-full rounded-2xl px-5 py-3 text-sm font-semibold transition ${palette.primary} disabled:opacity-50`;

  return (
    <main className={`relative min-h-[100dvh] overflow-hidden transition-colors duration-300 ${palette.app}`}>
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-1/2 top-[-12rem] h-80 w-80 -translate-x-1/2 rounded-full bg-blue-500/10 blur-3xl" />
        <div className="absolute bottom-[-8rem] right-[-4rem] h-72 w-72 rounded-full bg-cyan-400/10 blur-3xl" />
      </div>

      <div className="relative mx-auto flex min-h-[100dvh] w-full max-w-7xl items-center justify-center px-4 py-12">
        <div className="w-full max-w-[28rem]">
          <section
            className={`rounded-[2rem] border px-7 py-7 transition-all duration-300 ${
              theme === 'light' ? shellLight : shellDark
            }`}
          >
            <p className={`text-xs font-semibold uppercase tracking-[0.35em] text-center ${palette.accent}`}>
              Aiveilix
            </p>

            {loading && (
              <div className={`mt-8 text-center text-sm ${palette.muted}`}>Loading invitation...</div>
            )}

            {!loading && !info?.valid && (
              <div className="mt-6 text-center">
                <h1 className={`text-xl font-semibold ${palette.title}`}>Invitation unavailable</h1>
                <p className={`mt-3 text-sm ${palette.text}`}>
                  {info?.already_accepted
                    ? 'This invitation has already been accepted.'
                    : info?.expired
                      ? 'This invitation has expired.'
                      : 'This invitation link is invalid.'}
                </p>
                <button
                  onClick={() => navigate('/login')}
                  className={`mt-6 rounded-2xl px-6 py-2.5 text-sm font-semibold ${palette.primary}`}
                >
                  Go to login
                </button>
              </div>
            )}

            {!loading && info?.valid && (
              <>
                <div className="mt-5 flex items-center gap-3">
                  <div
                    className="h-12 w-12 shrink-0 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-sm"
                    style={{ backgroundColor: info.display_color || '#3B82F6' }}
                  >
                    {(info.display_name || info.invite_email || '?').charAt(0).toUpperCase()}
                  </div>
                  <div className="min-w-0">
                    <p className={`text-xs ${palette.muted}`}>You're invited to join</p>
                    <h1 className={`text-base font-semibold truncate ${palette.title}`}>
                      {info.workspace_owner_name || info.workspace_owner_email}
                    </h1>
                  </div>
                </div>

                <div className={`mt-5 rounded-2xl border p-4 ${palette.card}`}>
                  <div className={`text-[10px] font-semibold uppercase tracking-[0.18em] ${palette.muted}`}>
                    Joining as
                  </div>
                  <div className={`mt-1 text-sm font-medium ${palette.title}`}>
                    {info.display_name}
                  </div>
                  <div className={`text-xs ${palette.muted}`}>{info.invite_email}</div>
                </div>

                <form onSubmit={handleAccept} className="mt-6 space-y-4">
                  <div>
                    <label className={`mb-1.5 block text-xs font-semibold uppercase tracking-[0.18em] ${palette.muted}`}>
                      Set a password
                    </label>
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      minLength={8}
                      required
                      placeholder="At least 8 characters"
                      className={inputCls}
                    />
                  </div>
                  <div>
                    <label className={`mb-1.5 block text-xs font-semibold uppercase tracking-[0.18em] ${palette.muted}`}>
                      Confirm password
                    </label>
                    <input
                      type="password"
                      value={confirm}
                      onChange={(e) => setConfirm(e.target.value)}
                      required
                      placeholder="Re-enter your password"
                      className={inputCls}
                    />
                  </div>

                  {error && (
                    <div className={`text-sm rounded-2xl px-4 py-3 ${palette.error}`}>{error}</div>
                  )}

                  <button type="submit" disabled={submitting} className={btnPrimary}>
                    {submitting ? 'Accepting...' : 'Accept invitation'}
                  </button>
                </form>
              </>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}
