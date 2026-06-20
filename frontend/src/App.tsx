import { useCallback, useEffect, useState } from 'react';
import UploadForm from './components/UploadForm';
import JobList from './components/JobList';
import { createJob, getHealth, listJobs, type JobRecord } from './api';
import { useJobPolling } from './hooks/useJobPolling';
import type { JobEntry } from './types';

function toJobEntry(job: JobRecord): JobEntry {
  return {
    ...job,
    createdAt: job.createdAt ? new Date(job.createdAt) : new Date(),
  };
}

export default function App() {
  const [jobs, setJobs] = useState<JobEntry[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoadingJobs, setIsLoadingJobs] = useState(true);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [listError, setListError] = useState<string | null>(null);
  const [apiHealth, setApiHealth] = useState<string>('unbekannt');

  const updateJob = useCallback((jobID: string, updates: Partial<JobEntry>) => {
    setJobs(prev =>
      prev.map(job => (job.jobID === jobID ? { ...job, ...updates } : job))
    );
  }, []);

  useJobPolling({ jobs, onUpdate: updateJob });

  const loadJobs = useCallback(async () => {
    setIsLoadingJobs(true);
    setListError(null);

    try {
      const [records, health] = await Promise.all([listJobs(), getHealth()]);
      setJobs(records.map(toJobEntry));
      setApiHealth(health);
    } catch (err) {
      setListError(err instanceof Error ? err.message : 'Jobliste konnte nicht geladen werden.');
      setApiHealth('nicht erreichbar');
    } finally {
      setIsLoadingJobs(false);
    }
  }, []);

  useEffect(() => {
    loadJobs();
  }, [loadJobs]);

  const handleSubmit = async (params: {
    file: File;
    fileLanguage: string;
    translationLanguage: string;
    voiceID: string;
    splittingID: string;
  }) => {
    setIsUploading(true);
    setUploadError(null);

    try {
      const response = await createJob(params);
      const newJob: JobEntry = {
        ...toJobEntry(response),
        fileName: response.fileName || params.file.name,
      };
      setJobs(prev => [newJob, ...prev]);
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Unbekannter Fehler beim Upload.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = useCallback((jobID: string) => {
    setJobs(prev => prev.filter(job => job.jobID !== jobID));
  }, []);

  const handleRetry = useCallback((jobID: string) => {
    setJobs(prev => prev.filter(job => job.jobID !== jobID));
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-indigo-50/30 to-slate-100">
      <header className="border-b border-white/60 bg-white/70 backdrop-blur-sm">
        <div className="mx-auto flex max-w-5xl items-center gap-4 px-6 py-4">
          <img src="/logo.png" alt="LibriMe Logo" className="h-9 w-auto" />
          <div className="min-w-0 flex-1">
            <h1 className="text-xl font-bold tracking-tight text-gray-900">LibriMe</h1>
            <p className="text-xs italic text-gray-500">"Freedom starts in your ear."</p>
          </div>
          <span className="rounded-full bg-green-50 px-3 py-1 text-xs font-medium text-green-700">
            API: {apiHealth}
          </span>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          <div>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Neues Hoerbuch erstellen</h2>
              <p className="mt-1 text-sm text-gray-500">
                Lade eine PDF-Datei hoch und waehle deine Einstellungen.
              </p>
            </div>

            <div className="rounded-2xl border border-white bg-white/80 p-6 shadow-sm backdrop-blur-sm">
              <UploadForm onSubmit={handleSubmit} isLoading={isUploading} />

              {uploadError && (
                <div className="mt-4 flex items-start gap-2 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">
                  <svg className="mt-0.5 h-4 w-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <span>{uploadError}</span>
                </div>
              )}
            </div>

            <div className="mt-4 rounded-xl bg-indigo-50/70 px-4 py-3">
              <p className="text-xs font-medium text-indigo-800">Unterstuetzte Formate</p>
              <p className="mt-0.5 text-xs text-indigo-600">
                PDF-Dokumente werden automatisch in hochwertige Audiobooks konvertiert. Die Verarbeitung erfolgt serverseitig.
              </p>
            </div>
          </div>

          <div>
            <div className="mb-6 flex flex-wrap items-center justify-between gap-2">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Meine Jobs</h2>
                <p className="mt-1 text-sm text-gray-500">
                  {jobs.length === 0
                    ? isLoadingJobs ? 'Auftraege werden geladen.' : 'Noch keine Auftraege gestartet.'
                    : `${jobs.length} ${jobs.length === 1 ? 'Auftrag' : 'Auftraege'} insgesamt`}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={loadJobs}
                  disabled={isLoadingJobs}
                  className="rounded-lg px-3 py-1.5 text-xs font-medium text-indigo-600 transition-colors hover:bg-indigo-50 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Aktualisieren
                </button>
                {jobs.length > 0 && (
                  <button
                    onClick={() => setJobs([])}
                    className="rounded-lg px-3 py-1.5 text-xs font-medium text-gray-500 transition-colors hover:bg-red-50 hover:text-red-600"
                  >
                    Alle lokal entfernen
                  </button>
                )}
              </div>
            </div>

            {listError && (
              <div className="mb-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">
                {listError}
              </div>
            )}

            <JobList jobs={jobs} onDelete={handleDelete} onRetry={handleRetry} />
          </div>
        </div>
      </main>

      <footer className="mt-16 border-t border-gray-200 bg-white/50 py-6 text-center text-xs text-gray-400">
        <p>LibriMe - PDF zu Hoerbuch - Powered by OCR &amp; TTS</p>
      </footer>
    </div>
  );
}
