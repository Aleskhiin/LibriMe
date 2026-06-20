import { Link } from 'react-router-dom';
import LanguageToggle from '../components/LanguageToggle';
import librimeBg from '../assets/librime_bg.png';
import { useI18n } from '../i18n';

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="border-t border-orange-100 py-3 first:border-t-0">
      <dt className="text-xs font-semibold uppercase tracking-wide text-orange-700">{label}</dt>
      <dd className="mt-1 text-sm text-stone-800">{value}</dd>
    </div>
  );
}

const DEVELOPERS = [
  { name: 'Florian Fuchs', role: 'Projektmanager & Co. AI Module Developer' },
  { name: 'Dominik Bliem-Zupansky', role: 'Frontend Developer & Head of Marketing' },
  { name: 'Georg Maier', role: 'AI Module Developer & Assistant Documentation Manager' },
  { name: 'Stefan Aldrian', role: 'Head of Documentation & Assistant Marketing Manager' },
  { name: 'Philip Macheiner', role: 'Backend development & Assistant Projectmanager' },
];

const REPOSITORY_URL = 'https://github.com/Aleskhiin/LibriMe';

export default function ImprintPage() {
  const { t } = useI18n();

  return (
    <div
      className="min-h-screen bg-cover bg-center bg-fixed text-stone-900"
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

      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="mb-6 flex flex-wrap gap-3">
          <Link
            to="/"
            className="rounded-lg bg-orange-100 px-3 py-1.5 text-sm font-medium text-orange-800 transition-colors hover:bg-orange-200"
          >
            {t('imprintBackHome')}
          </Link>
          <Link
            to="/app"
            className="rounded-lg bg-orange-100 px-3 py-1.5 text-sm font-medium text-orange-800 transition-colors hover:bg-orange-200"
          >
            {t('imprintBackApp')}
          </Link>
        </div>

        <section className="rounded-2xl border border-orange-100 bg-orange-50/90 p-6 shadow-sm shadow-orange-900/5 backdrop-blur-sm">
          <div className="max-w-3xl">
            <h2 className="text-3xl font-bold tracking-tight text-stone-950">{t('imprintTitle')}</h2>
            <p className="mt-2 text-sm text-stone-600">{t('imprintSubtitle')}</p>
          </div>

          <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
            <article className="rounded-xl border border-orange-100 bg-white/70 p-5">
              <h3 className="text-base font-semibold text-stone-900">{t('imprintProviderTitle')}</h3>
              <dl className="mt-4">
                <InfoRow label={t('imprintProjectName')} value="LibriMe" />
                <InfoRow label={t('imprintResponsibleTitle')} value={t('imprintResponsibleValue')} />
              </dl>
            </article>

            <article className="rounded-xl border border-orange-100 bg-white/70 p-5">
              <h3 className="text-base font-semibold text-stone-900">{t('imprintContactTitle')}</h3>
              <dl className="mt-4">
                <InfoRow label={t('imprintEmail')} value={t('imprintEmailValue')} />
                <InfoRow label={t('imprintRepository')} value={REPOSITORY_URL} />
              </dl>
            </article>
          </div>

          <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
            <article className="rounded-xl border border-orange-100 bg-white/70 p-5">
              <h3 className="text-base font-semibold text-stone-900">{t('imprintOpenSourceTitle')}</h3>
              <p className="mt-3 text-sm leading-6 text-stone-700">{t('imprintOpenSourceText')}</p>
              <dl className="mt-4">
                <InfoRow label={t('imprintLicense')} value="MIT" />
                <div className="border-t border-orange-100 py-3">
                  <dt className="text-xs font-semibold uppercase tracking-wide text-orange-700">{t('imprintRepository')}</dt>
                  <dd className="mt-1 text-sm">
                    <a
                      href={REPOSITORY_URL}
                      target="_blank"
                      rel="noreferrer"
                      className="font-medium text-orange-700 underline-offset-4 hover:underline"
                    >
                      {REPOSITORY_URL}
                    </a>
                  </dd>
                </div>
              </dl>
            </article>

            <article className="rounded-xl border border-orange-100 bg-white/70 p-5">
              <h3 className="text-base font-semibold text-stone-900">{t('imprintDevelopersTitle')}</h3>
              <div className="mt-4 divide-y divide-orange-100">
                {DEVELOPERS.map(developer => (
                  <div key={developer.name} className="grid gap-1 py-3 sm:grid-cols-[minmax(0,1fr)_minmax(0,1.6fr)]">
                    <p className="text-sm font-semibold text-stone-800">{developer.name}</p>
                    <p className="text-sm text-stone-600">
                      <span className="sr-only">{t('imprintRole')}: </span>
                      {developer.role}
                    </p>
                  </div>
                ))}
              </div>
            </article>
          </div>
        </section>
      </main>

      <footer className="mt-16 border-t border-orange-200/70 bg-orange-50/70 py-6 text-center text-xs text-stone-500">
        <div className="mx-auto flex max-w-5xl flex-col items-center justify-center gap-2 px-6 sm:flex-row sm:gap-4">
          <p>LibriMe</p>
          <Link to="/impressum" className="font-medium text-orange-700 underline-offset-4 hover:underline">
            {t('footerImprint')}
          </Link>
        </div>
      </footer>
    </div>
  );
}
