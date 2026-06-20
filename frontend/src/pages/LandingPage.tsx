import { useNavigate } from 'react-router-dom';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-br from-slate-50 via-indigo-50/30 to-slate-100">
      <header className="border-b border-white/60 bg-white/70 backdrop-blur-sm">
        <div className="mx-auto flex max-w-5xl items-center gap-4 px-6 py-4">
          <img src="/logo.png" alt="LibriMe Logo" className="h-9 w-auto" />
          <div className="min-w-0 flex-1">
            <h1 className="text-xl font-bold tracking-tight text-gray-900">LibriMe</h1>
            <p className="text-xs italic text-gray-500">"Freedom starts in your ear."</p>
          </div>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col items-center justify-center px-6 py-16 text-center">
        <img src="/logoBig.png" alt="LibriMe" className="mb-8 h-24 w-auto" />

        <h2 className="max-w-2xl text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
          Verwandle PDFs in Hörbücher
        </h2>
        <p className="mt-4 max-w-xl text-base text-gray-500 sm:text-lg">
          Lade dein Dokument hoch und LibriMe erstellt dir automatisch eine hochwertige
          Audio-Version.
        </p>

        <button
          onClick={() => navigate('/app')}
          className="
            mt-10 flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-8 py-4 text-base font-semibold text-white shadow-md
            transition-all duration-200 hover:bg-indigo-700 hover:shadow-lg active:scale-[0.98]
          "
        >
          Zur App
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </button>

        <div className="mt-16 grid grid-cols-1 gap-6 sm:grid-cols-3">
          <div className="rounded-2xl border border-white bg-white/80 p-6 text-left shadow-sm backdrop-blur-sm">
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-indigo-50">
              <svg className="h-5 w-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="font-semibold text-gray-800">Dokumente hochladen</p>
            <p className="mt-1 text-sm text-gray-500">Einfach per Drag &amp; Drop oder Dateiauswahl, bis 50&nbsp;MB.</p>
          </div>

          <div className="rounded-2xl border border-white bg-white/80 p-6 text-left shadow-sm backdrop-blur-sm">
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-indigo-50">
              <svg className="h-5 w-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
            <p className="font-semibold text-gray-800">Automatische Vertonung</p>
            <p className="mt-1 text-sm text-gray-500">Text-Extraktion und Sprachsynthese laufen vollautomatisch im Hintergrund.</p>
          </div>

          <div className="rounded-2xl border border-white bg-white/80 p-6 text-left shadow-sm backdrop-blur-sm">
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-indigo-50">
              <svg className="h-5 w-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="font-semibold text-gray-800">Fertig zum Anhören</p>
            <p className="mt-1 text-sm text-gray-500">Fortschritt live verfolgen und das fertige Hörbuch direkt herunterladen.</p>
          </div>
        </div>
      </main>

      <footer className="border-t border-gray-200 bg-white/50 py-6 text-center text-xs text-gray-400">
        <p>LibriMe - PDF zu Hoerbuch.</p>
      </footer>
    </div>
  );
}
