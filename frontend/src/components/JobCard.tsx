import { useState } from 'react';
import type { JobEntry } from '../types';
import { downloadJobResult, getResultUrl } from '../api';

interface JobCardProps {
  job: JobEntry;
  onRetry: (jobID: string) => void;
}

const STATUS_LABELS: Record<JobEntry['status'], string> = {
  QUEUED: 'Warteschlange',
  RUNNING: 'Wird verarbeitet',
  COMPLETED: 'Abgeschlossen',
  FAILED: 'Fehlgeschlagen',
};

const STATUS_COLORS: Record<JobEntry['status'], string> = {
  QUEUED: 'bg-amber-100 text-amber-800',
  RUNNING: 'bg-orange-100 text-orange-800',
  COMPLETED: 'bg-green-100 text-green-800',
  FAILED: 'bg-red-100 text-red-800',
};

const LANGUAGE_LABELS: Record<string, string> = {
  en_US: 'English (US)',
  de_DE: 'Deutsch',
  fr_FR: 'Französisch',
  es_ES: 'Spanisch',
};

const VOICE_LABELS: Record<string, string> = {
  male_v1: 'Männlich (v1)',
  female_v1: 'Weiblich (v1)',
};

function formatTime(date: Date | undefined): string {
  if (!date || Number.isNaN(date.getTime())) {
    return 'Gerade eben';
  }

  return date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
}

export default function JobCard({ job, onRetry }: JobCardProps) {
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const isActive = job.status === 'QUEUED' || job.status === 'RUNNING';
  const isCompleted = job.status === 'COMPLETED';
  const isFailed = job.status === 'FAILED';
  const resultUrl = job.downloadURL ?? getResultUrl(job.jobID);
  const downloadFilename = `${job.fileName.replace(/\.[^/.]+$/, '')}.wav`;

  const handleDownload = async () => {
    setIsDownloading(true);
    setDownloadError(null);

    try {
      await downloadJobResult(resultUrl, downloadFilename);
    } catch (err) {
      setDownloadError(err instanceof Error ? err.message : 'Download fehlgeschlagen.');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className={`
      rounded-2xl border bg-orange-50/90 shadow-sm shadow-orange-900/5 transition-all duration-300 backdrop-blur-sm
      ${isCompleted ? 'border-green-200 shadow-green-50' : ''}
      ${isFailed ? 'border-red-200' : ''}
      ${isActive ? 'border-orange-200' : ''}
      ${!isActive && !isCompleted && !isFailed ? 'border-orange-100' : ''}
    `}>
      <div className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="flex min-w-0 items-center gap-3">
            <div className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg ${isCompleted ? 'bg-green-100' : isActive ? 'bg-orange-100' : 'bg-orange-100'}`}>
              <svg className={`h-5 w-5 ${isCompleted ? 'text-green-600' : isActive ? 'text-orange-600' : 'text-orange-500'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div className="min-w-0">
              <p className="truncate font-semibold text-stone-800">{job.fileName}</p>
              <p className="text-xs text-stone-500">{formatTime(job.createdAt)}</p>
            </div>
          </div>

          <span className={`flex-shrink-0 rounded-full px-2.5 py-1 text-xs font-medium ${STATUS_COLORS[job.status]}`}>
            {STATUS_LABELS[job.status]}
          </span>
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          <span className="inline-flex items-center gap-1 rounded-md bg-orange-100 px-2 py-1 text-xs text-orange-900">
            <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
            </svg>
            {LANGUAGE_LABELS[job.fileLanguage] ?? job.fileLanguage}
            &nbsp;-&gt;&nbsp;
            {LANGUAGE_LABELS[job.translationLanguage] ?? job.translationLanguage}
          </span>
          <span className="inline-flex items-center gap-1 rounded-md bg-orange-100 px-2 py-1 text-xs text-orange-900">
            <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
            {VOICE_LABELS[job.voiceID] ?? job.voiceID}
          </span>
          <span className="inline-flex items-center rounded-md bg-orange-100 px-2 py-1 text-xs text-orange-900">
            {job.splittingID}
          </span>
        </div>

        {isActive && (
          <div className="mt-4">
            <div className="mb-1 flex items-center justify-between text-xs text-stone-500">
              <span>{job.status === 'QUEUED' ? 'Warte auf Verarbeitung...' : 'Wird verarbeitet...'}</span>
              <span>{job.progress}%</span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-orange-100">
              <div
                className="h-full rounded-full bg-orange-500 transition-all duration-500"
                style={{ width: `${Math.max(0, Math.min(100, job.progress))}%` }}
              />
            </div>
          </div>
        )}

        {isFailed && job.error && (
          <div className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700">
            {job.error}
          </div>
        )}

        {isCompleted && (
          <div className="mt-4 flex flex-wrap gap-2">
            <div className="w-full">
              <audio controls className="w-full rounded-lg" src={resultUrl}>
                Dein Browser unterstützt kein Audio-Element.
              </audio>
            </div>
            {downloadError && (
              <div className="w-full rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700">
                {downloadError}
              </div>
            )}
            <button
              type="button"
              onClick={handleDownload}
              disabled={isDownloading}
              className="inline-flex items-center gap-1.5 rounded-lg bg-orange-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              {isDownloading ? 'Wird geladen...' : 'Herunterladen'}
            </button>
          </div>
        )}

        {isFailed && (
          <div className="mt-3 flex items-center justify-end gap-2 border-t border-orange-100 pt-3">
            <button
              onClick={() => onRetry(job.jobID)}
              className="inline-flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-medium text-orange-700 transition-colors hover:bg-orange-100"
            >
              <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Erneut versuchen
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
