import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import librimeBg from '../assets/librime_bg.png';
import AuthMenu from '../components/AuthMenu';
import LanguageToggle from '../components/LanguageToggle';
import { useI18n } from '../i18n';
import { useAuth } from '../auth/AuthProvider';

export default function LandingPage() {
  const navigate = useNavigate();
  const { t } = useI18n();
  const { user, isAuthLoading, signInEmail, signInGoogle, signUpEmail } = useAuth();
  const [authError, setAuthError] = useState<string | null>(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleGoogleAuth = async () => {
    setAuthError(null);

    try {
      await signInGoogle();
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
      navigate('/app');
    } catch (err) {
      setAuthError(err instanceof Error ? err.message : t('authLoginFailed'));
    }
  };

  return (
    <div
      className="flex min-h-screen flex-col bg-cover bg-center bg-fixed text-stone-900"
      style={{ backgroundImage: `linear-gradient(rgba(255, 247, 237, 0.82), rgba(255, 237, 213, 0.74)), url(${librimeBg})` }}
    >
      <header className="border-b border-orange-200/70 bg-orange-50/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-5xl items-center gap-4 px-6 py-4">
          <img src="/logo.png" alt="LibriMe Logo" className="h-9 w-auto" />
          <div className="min-w-0 flex-1">
            <h1 className="text-xl font-bold tracking-tight text-stone-950">LibriMe</h1>
            <p className="text-xs italic text-stone-600">"Freedom starts in your ear."</p>
          </div>
          <AuthMenu />
          <LanguageToggle />
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col items-center justify-center px-6 py-8 text-center">
        <img src="/logoBig.png" alt="LibriMe" className="mb-4 h-16 w-auto sm:h-20" />

        <h2 className="max-w-2xl text-3xl font-bold tracking-tight text-stone-950 sm:text-4xl">
          {t('landingTitle')}
        </h2>
        <p className="mt-2 max-w-xl text-sm text-stone-600 sm:text-base">
          {t('landingSubtitle')}
        </p>

        <div className="mt-6 flex w-full max-w-2xl flex-col items-center gap-3">
          {user ? (
            <>
              <p className="text-sm text-stone-600">
                {t('authSignedInAs', { name: user.displayName || user.email || 'User' })}
              </p>
              <button
                onClick={() => navigate('/app')}
                className="flex items-center justify-center gap-2 rounded-xl bg-orange-600 px-8 py-4 text-base font-semibold text-white shadow-md shadow-orange-900/10 transition-all duration-200 hover:bg-orange-700 hover:shadow-lg active:scale-[0.98]"
              >
                {t('authOpenApp')}
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </button>
            </>
          ) : (
            <div className="w-full rounded-2xl border border-orange-100 bg-orange-50/90 p-4 text-left shadow-lg shadow-orange-900/10 backdrop-blur-sm sm:max-w-md">
              <p className="text-base font-semibold text-stone-900">{t('authContinueTitle')}</p>

              <div className="mt-4 grid gap-2">
                <button
                  type="button"
                  onClick={() => navigate('/app')}
                  className="flex w-full items-center justify-center gap-2 rounded-xl bg-orange-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-orange-700"
                >
                  {t('authContinueAnonymous')}
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </button>
                <p className="text-center text-xs text-stone-500">{t('authAnonymousLimit')}</p>
                <div className="my-1 h-px bg-orange-100" />
                <button
                  type="button"
                  onClick={handleGoogleAuth}
                  disabled={isAuthLoading}
                  className="flex w-full items-center justify-center gap-3 rounded-xl border border-orange-200 bg-white px-4 py-2.5 text-sm font-semibold text-stone-800 shadow-sm transition-colors hover:bg-orange-50 disabled:cursor-not-allowed disabled:opacity-60"
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
                  <p className="text-xs font-medium text-stone-500">{t('authEmailPasswordHint')}</p>
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
              </div>
            </div>
          )}

          {authError && (
            <div className="w-full rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">
              {authError}
            </div>
          )}
        </div>

        <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="rounded-2xl border border-orange-100 bg-orange-50/85 p-4 text-left shadow-sm shadow-orange-900/5 backdrop-blur-sm">
            <div className="mb-2 flex h-9 w-9 items-center justify-center rounded-full bg-orange-100">
              <svg className="h-5 w-5 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="font-semibold text-stone-800">{t('landingUploadTitle')}</p>
            <p className="mt-1 text-xs leading-5 text-stone-600 sm:text-sm">{t('landingUploadText')}</p>
          </div>

          <div className="rounded-2xl border border-orange-100 bg-orange-50/85 p-4 text-left shadow-sm shadow-orange-900/5 backdrop-blur-sm">
            <div className="mb-2 flex h-9 w-9 items-center justify-center rounded-full bg-orange-100">
              <svg className="h-5 w-5 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
            <p className="font-semibold text-stone-800">{t('landingTtsTitle')}</p>
            <p className="mt-1 text-xs leading-5 text-stone-600 sm:text-sm">{t('landingTtsText')}</p>
          </div>

          <div className="rounded-2xl border border-orange-100 bg-orange-50/85 p-4 text-left shadow-sm shadow-orange-900/5 backdrop-blur-sm">
            <div className="mb-2 flex h-9 w-9 items-center justify-center rounded-full bg-orange-100">
              <svg className="h-5 w-5 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="font-semibold text-stone-800">{t('landingReadyTitle')}</p>
            <p className="mt-1 text-xs leading-5 text-stone-600 sm:text-sm">{t('landingReadyText')}</p>
          </div>
        </div>
      </main>

      <footer className="border-t border-orange-200/70 bg-orange-50/70 py-4 text-center text-xs text-stone-500">
        <div className="mx-auto flex max-w-5xl flex-col items-center justify-center gap-2 px-6 sm:flex-row sm:gap-4">
          <p>{t('landingFooter')}</p>
          <Link to="/impressum" className="font-medium text-orange-700 underline-offset-4 hover:underline">
            {t('footerImprint')}
          </Link>
        </div>
      </footer>
    </div>
  );
}
