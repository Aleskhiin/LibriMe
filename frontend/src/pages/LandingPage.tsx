import { Link, useNavigate } from 'react-router-dom';
import librimeBg from '../assets/librime_bg.png';
import LanguageToggle from '../components/LanguageToggle';
import { useI18n } from '../i18n';

export default function LandingPage() {
  const navigate = useNavigate();
  const { t } = useI18n();

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
          <LanguageToggle />
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col items-center justify-center px-6 py-16 text-center">
        <img src="/logoBig.png" alt="LibriMe" className="mb-8 h-24 w-auto" />

        <h2 className="max-w-2xl text-4xl font-bold tracking-tight text-stone-950 sm:text-5xl">
          {t('landingTitle')}
        </h2>
        <p className="mt-4 max-w-xl text-base text-stone-600 sm:text-lg">
          {t('landingSubtitle')}
        </p>

        <button
          onClick={() => navigate('/app')}
          className="
            mt-10 flex items-center justify-center gap-2 rounded-xl bg-orange-600 px-8 py-4 text-base font-semibold text-white shadow-md shadow-orange-900/10
            transition-all duration-200 hover:bg-orange-700 hover:shadow-lg active:scale-[0.98]
          "
        >
          {t('landingCta')}
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </button>

        <div className="mt-16 grid grid-cols-1 gap-6 sm:grid-cols-3">
          <div className="rounded-2xl border border-orange-100 bg-orange-50/85 p-6 text-left shadow-sm shadow-orange-900/5 backdrop-blur-sm">
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-orange-100">
              <svg className="h-5 w-5 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="font-semibold text-stone-800">{t('landingUploadTitle')}</p>
            <p className="mt-1 text-sm text-stone-600">{t('landingUploadText')}</p>
          </div>

          <div className="rounded-2xl border border-orange-100 bg-orange-50/85 p-6 text-left shadow-sm shadow-orange-900/5 backdrop-blur-sm">
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-orange-100">
              <svg className="h-5 w-5 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
            <p className="font-semibold text-stone-800">{t('landingTtsTitle')}</p>
            <p className="mt-1 text-sm text-stone-600">{t('landingTtsText')}</p>
          </div>

          <div className="rounded-2xl border border-orange-100 bg-orange-50/85 p-6 text-left shadow-sm shadow-orange-900/5 backdrop-blur-sm">
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-orange-100">
              <svg className="h-5 w-5 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="font-semibold text-stone-800">{t('landingReadyTitle')}</p>
            <p className="mt-1 text-sm text-stone-600">{t('landingReadyText')}</p>
          </div>
        </div>
      </main>

      <footer className="border-t border-orange-200/70 bg-orange-50/70 py-6 text-center text-xs text-stone-500">
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
