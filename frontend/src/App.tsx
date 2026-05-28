import { useState, useCallback } from 'react';
import UploadForm from './components/UploadForm';
import JobList from './components/JobList';
import { createJob } from './api';
import { useJobPolling } from './hooks/useJobPolling';
import type { JobEntry } from './types';

export default function App() {
  const [jobs, setJobs] = useState<JobEntry[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const updateJob = useCallback((jobID: string, updates: Partial<JobEntry>) => {
    setJobs(prev =>
      prev.map(j => (j.jobID === jobID ? { ...j, ...updates } : j))
    );
  }, []);

  useJobPolling({ jobs, onUpdate: updateJob });

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
        jobID: response.jobID,
        fileName: params.file.name,
        fileLanguage: params.fileLanguage,
        translationLanguage: params.translationLanguage,
        voiceID: params.voiceID,
        splittingID: params.splittingID,
        status: response.status,
        progress: 0,
        downloadURL: null,
        error: null,
        createdAt: new Date(),
      };
      setJobs(prev => [newJob, ...prev]);
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Unbekannter Fehler beim Upload.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = useCallback((jobID: string) => {
    setJobs(prev => prev.filter(j => j.jobID !== jobID));
  }, []);

  const handleRetry = useCallback((_jobID: string) => {
    // Retry-Logik: Job aus Liste entfernen, Nutzer kann neu hochladen
    setJobs(prev => prev.filter(j => j.jobID !== _jobID));
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-indigo-50/30 to-slate-100">
      {/* Header */}
      <header className="border-b border-white/60 bg-white/70 backdrop-blur-sm">
        <div className="mx-auto flex max-w-5xl items-center gap-4 px-6 py-4">
          <img src="/logo.png" alt="LibriMe Logo" className="h-9 w-auto" />
          <div>
            <h1 className="text-xl font-bold tracking-tight text-gray-900">LibriMe</h1>
            <p className="text-xs text-gray-500 italic">"Freedom starts in your ear."</p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">

          {/* Linke Spalte: Upload */}
          <div>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Neues Hörbuch erstellen</h2>
              <p className="mt-1 text-sm text-gray-500">
                Lade eine PDF-Datei hoch und wähle deine Einstellungen.
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

            {/* Info-Box */}
            <div className="mt-4 rounded-xl bg-indigo-50/70 px-4 py-3">
              <p className="text-xs font-medium text-indigo-800">Unterstützte Formate</p>
              <p className="mt-0.5 text-xs text-indigo-600">
                PDF-Dokumente werden automatisch in hochwertige Audiobooks konvertiert. Die Verarbeitung erfolgt serverseitig.
              </p>
            </div>
          </div>

          {/* Rechte Spalte: Job-Liste */}
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Meine Jobs</h2>
                <p className="mt-1 text-sm text-gray-500">
                  {jobs.length === 0
                    ? 'Noch keine Aufträge gestartet.'
                    : `${jobs.length} ${jobs.length === 1 ? 'Auftrag' : 'Aufträge'} insgesamt`}
                </p>
              </div>
              {jobs.length > 0 && (
                <button
                  onClick={() => setJobs([])}
                  className="rounded-lg px-3 py-1.5 text-xs font-medium text-gray-500 hover:bg-red-50 hover:text-red-600 transition-colors"
                >
                  Alle löschen
                </button>
              )}
            </div>

            <JobList jobs={jobs} onDelete={handleDelete} onRetry={handleRetry} />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-gray-200 bg-white/50 py-6 text-center text-xs text-gray-400">
        <p>LibriMe &mdash; PDF zu Hörbuch &mdash; Powered by OCR &amp; TTS</p>
      </footer>
    </div>
  );
}
