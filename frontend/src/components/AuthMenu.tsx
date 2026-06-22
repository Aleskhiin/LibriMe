import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider';
import { useI18n } from '../i18n';

export default function AuthMenu() {
  const navigate = useNavigate();
  const { t } = useI18n();
  const { user, isAuthLoading, signInEmail, signInGoogle, signUpEmail, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const displayName = user?.displayName || user?.email || 'User';

  const handleGoogleAuth = async () => {
    setAuthError(null);

    try {
      await signInGoogle();
      setIsOpen(false);
      navigate('/app');
    } catch (err) {
      setAuthError(err instanceof Error ? err.message : t('authLoginFailed'));
    }
  };

  const handleEmailAuth = async (mode: 'signIn' | 'signUp') => {
    setAuthError(null);

    try {
      if (mode === 'signIn') {
        await signInEmail(email, password);
      } else {
        await signUpEmail(email, password);
      }
      setIsOpen(false);
      navigate('/app');
    } catch (err) {
      setAuthError(err instanceof Error ? err.message : t('authLoginFailed'));
    }
  };

  const handleLogout = async () => {
    await logout();
    setIsOpen(false);
    navigate('/');
  };

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(open => !open)}
        className="flex max-w-44 items-center gap-2 rounded-lg bg-orange-100 px-3 py-1.5 text-xs font-medium text-orange-900 transition-colors hover:bg-orange-200"
        aria-expanded={isOpen}
        aria-label={t('authMenuLabel')}
      >
        <span className="truncate">{user ? displayName : t('authLogin')}</span>
        <svg className={`h-3.5 w-3.5 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute left-0 z-50 mt-2 w-72 max-h-[calc(100vh-5rem)] overflow-y-auto rounded-xl border border-orange-100 bg-white/95 p-3 text-left shadow-lg shadow-orange-900/10 backdrop-blur-sm">
          {user ? (
            <div className="space-y-2">
              <p className="truncate px-2 text-xs text-stone-500">
                {t('authSignedInAs', { name: displayName })}
              </p>
              <Link
                to="/app"
                onClick={() => setIsOpen(false)}
                className="block rounded-lg px-3 py-2 text-sm font-medium text-stone-800 transition-colors hover:bg-orange-50"
              >
                {t('authOpenApp')}
              </Link>
              <button
                type="button"
                onClick={handleLogout}
                className="w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-red-700 transition-colors hover:bg-red-50"
              >
                {t('authLogout')}
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              <p className="px-2 text-sm font-semibold text-stone-900">{t('authContinueTitle')}</p>
              <button
                type="button"
                onClick={handleGoogleAuth}
                disabled={isAuthLoading}
                className="flex w-full items-center justify-center gap-3 rounded-lg border border-orange-200 bg-white px-3 py-2.5 text-sm font-semibold text-stone-800 transition-colors hover:bg-orange-50 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <svg className="h-5 w-5" viewBox="0 0 24 24" aria-hidden="true">
                  <path fill="#4285F4" d="M21.6 12.23c0-.78-.07-1.53-.2-2.23H12v4.22h5.38a4.6 4.6 0 01-2 3.02v2.51h3.24c1.9-1.75 2.98-4.33 2.98-7.52z" />
                  <path fill="#34A853" d="M12 22c2.7 0 4.96-.9 6.62-2.43l-3.24-2.51c-.9.6-2.04.96-3.38.96-2.6 0-4.8-1.76-5.58-4.12H3.08v2.59A10 10 0 0012 22z" />
                  <path fill="#FBBC05" d="M6.42 13.9a6.01 6.01 0 010-3.8V7.51H3.08a10 10 0 000 8.98l3.34-2.59z" />
                  <path fill="#EA4335" d="M12 5.98c1.47 0 2.8.5 3.84 1.5l2.87-2.87A9.64 9.64 0 0012 2 10 10 0 003.08 7.51l3.34 2.59C7.2 7.74 9.4 5.98 12 5.98z" />
                </svg>
                {t('authContinueGoogle')}
              </button>
              <div className="pt-2">
                <p className="px-2 text-xs font-medium text-stone-500">{t('authEmailPasswordHint')}</p>
                <div className="mt-2 grid gap-2">
                  <input
                    type="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    placeholder={t('authEmail')}
                    className="rounded-lg border border-orange-200 px-3 py-2 text-sm focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-200"
                  />
                  <input
                    type="password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder={t('authPassword')}
                    className="rounded-lg border border-orange-200 px-3 py-2 text-sm focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-200"
                  />
                  <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                    <button
                      type="button"
                      onClick={() => handleEmailAuth('signIn')}
                      disabled={isAuthLoading || !email || !password}
                      className="rounded-lg bg-orange-600 px-3 py-2 text-sm font-semibold text-white transition-colors hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {t('authSignInEmail')}
                    </button>
                    <button
                      type="button"
                      onClick={() => handleEmailAuth('signUp')}
                      disabled={isAuthLoading || !email || !password}
                      className="rounded-lg bg-orange-100 px-3 py-2 text-sm font-semibold text-orange-900 transition-colors hover:bg-orange-200 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {t('authSignUpEmail')}
                    </button>
                  </div>
                </div>
              </div>
              {authError && (
                <div className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700">
                  {authError}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
