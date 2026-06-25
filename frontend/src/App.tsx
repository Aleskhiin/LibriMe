import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import UploadForm from './components/UploadForm';
import JobList from './components/JobList';
import AuthMenu from './components/AuthMenu';
import LanguageToggle from './components/LanguageToggle';
import { createJob, listJobs, type JobRecord } from './api';
import { useJobPolling } from './hooks/useJobPolling';
import type { JobEntry } from './types';
import librimeBg from './assets/librime_bg.png';
import { useI18n } from './i18n';
import { useAuth } from './auth/AuthProvider';

const SUPPORTED_FORMATS = [
  '.png',
  '.jpg',
  '.jpeg',
  '.bmp',
  '.tif',
  '.tiff',
  '.webp',
  '.pdf',
  '.txt',
  '.md',
  '.markdown',
  '.doc',
  '.docx',
  '.odt',
  '.ppt',
  '.pptx',
  '.html',
  '.htm',
  '.csv',
  '.json',
].join(', ');

function toJobEntry(job: JobRecord): JobEntry {
  return {
    ...job,
    createdAt: job.createdAt ? new Date(job.createdAt) : new Date(),
  };
}

export default function App() {
  const { t } = useI18n();
  const { user, isAuthLoading } = useAuth();
  const [jobs, setJobs] = useState<JobEntry[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoadingJobs, setIsLoadingJobs] = useState(true);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [listError, setListError] = useState<string | null>(null);
  const maxFileSizeMB = user ? 50 : 10;
  const hasActiveJob = jobs.some(job => job.status === 'QUEUED' || job.status === 'RUNNING');
  const uploadDisabledReason = isLoadingJobs
    ? t('appJobsLoadingBlock')
    : hasActiveJob
      ? t('appActiveJobBlock')
      : undefined;

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
      const records = await listJobs();
      setJobs(records.map(toJobEntry));
    } catch (err) {
      setListError(err instanceof Error ? err.message : t('appListError'));
    } finally {
      setIsLoadingJobs(false);
    }
  }, [t]);

  useEffect(() => {
    if (!isAuthLoading) {
      loadJobs();
    }
  }, [isAuthLoading, user, loadJobs]);

  const handleSubmit = async (params: {
    file: File;
    fileLanguage: string;
    translationLanguage: string;
    voiceID: string;
    splittingID: string;
  }) => {
    if (uploadDisabledReason) {
      setUploadError(uploadDisabledReason);
      return;
    }

    setIsUploading(true);
    setUploadError(null);

    try {
      const response = await createJob(params);
      const newJob: JobEntry = {
        ...toJobEntry(response),
        fileName: response.fileName || params.file.name,
        fileLanguage: response.fileLanguage || params.fileLanguage,
        translationLanguage: response.translationLanguage || params.translationLanguage,
        voiceID: response.voiceID || params.voiceID,
        splittingID: response.splittingID || params.splittingID,
      };
      setJobs(prev => [newJob, ...prev]);
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : t('appUploadUnknownError'));
    } finally {
      setIsUploading(false);
    }
  };

  const handleRetry = useCallback((jobID: string) => {
    setJobs(prev => prev.filter(job => job.jobID !== jobID));
  }, []);

  return (
    <div
      className="min-h-screen bg-cover bg-center bg-fixed text-stone-900"
      style={{ backgroundImage: `linear-gradient(rgba(255, 247, 237, 0.82), rgba(255, 237, 213, 0.74)), url(${librimeBg})` }}
    >
      <header className="relative z-10 border-b border-orange-200/70 bg-orange-50/80 backdrop-blur-sm">
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

      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          <div>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-stone-950">{t('appNewAudiobookTitle')}</h2>
              <p className="mt-1 text-sm text-stone-600">
                {t('appNewAudiobookSubtitle')}
              </p>
            </div>

            <div className="rounded-2xl border border-orange-100 bg-orange-50/85 p-6 shadow-sm shadow-orange-900/5 backdrop-blur-sm">
              <UploadForm
                onSubmit={handleSubmit}
                isLoading={isUploading}
                maxFileSizeMB={maxFileSizeMB}
                submitDisabledReason={uploadDisabledReason}
              />

              {uploadError && (
                <div className="mt-4 flex items-start gap-2 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">
                  <svg className="mt-0.5 h-4 w-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <span>{uploadError}</span>
                </div>
              )}
            </div>

            <div className="mt-4 rounded-xl border border-orange-200/80 bg-orange-100/80 px-4 py-3 text-orange-950">
              <p className="text-xs font-medium">{t('appSupportedFormats')}</p>
              <p className="mt-0.5 text-xs text-orange-800">
                {SUPPORTED_FORMATS}
              </p>
              <p className="mt-1 text-xs font-medium text-orange-900">
                {t('appUploadLimit', { limit: maxFileSizeMB })}
              </p>
            </div>
          </div>

          <div>
            <div className="mb-6 flex flex-wrap items-center justify-between gap-2">
              <div>
                <h2 className="text-2xl font-bold text-stone-950">{t('appMyJobs')}</h2>
                <p className="mt-1 text-sm text-stone-600">
                  {jobs.length === 0
                    ? isLoadingJobs ? t('appJobsLoading') : t('appNoJobsStarted')
                    : jobs.length === 1 ? t('appOneJobTotal') : t('appManyJobsTotal', { count: jobs.length })}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={loadJobs}
                  disabled={isLoadingJobs}
                  className="rounded-lg px-3 py-1.5 text-xs font-medium text-orange-700 transition-colors hover:bg-orange-100 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {t('appRefresh')}
                </button>
              </div>
            </div>

            {listError && (
              <div className="mb-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">
                {listError}
              </div>
            )}

            <JobList jobs={jobs} onRetry={handleRetry} />
          </div>
        </div>
      </main>

      <footer className="mt-16 border-t border-orange-200/70 bg-orange-50/70 py-6 text-center text-xs text-stone-500">
        <div className="mx-auto flex max-w-5xl flex-col items-center justify-center gap-2 px-6 sm:flex-row sm:gap-4">
          <p>{t('appFooter')}</p>
          <Link to="/impressum" className="font-medium text-orange-700 underline-offset-4 hover:underline">
            {t('footerImprint')}
          </Link>
        </div>
      </footer>
    </div>
  );
}
