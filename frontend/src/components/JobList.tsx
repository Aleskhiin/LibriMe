import type { JobEntry } from '../types';
import JobCard from './JobCard';

interface JobListProps {
  jobs: JobEntry[];
  onDelete: (jobID: string) => void;
  onRetry: (jobID: string) => void;
}

export default function JobList({ jobs, onDelete, onRetry }: JobListProps) {
  if (jobs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-orange-200 bg-orange-50/80 py-14 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-orange-100">
          <svg className="h-7 w-7 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
          </svg>
        </div>
        <p className="mt-3 font-medium text-stone-600">Noch keine Jobs</p>
        <p className="mt-1 text-sm text-stone-500">Lade eine Datei hoch, um dein erstes Hörbuch zu erstellen.</p>
      </div>
    );
  }

  const activeJobs = jobs.filter(job => job.status === 'QUEUED' || job.status === 'RUNNING');
  const completedJobs = jobs.filter(job => job.status === 'COMPLETED');
  const failedJobs = jobs.filter(job => job.status === 'FAILED');

  return (
    <div className="space-y-6">
      {activeJobs.length > 0 && (
        <section>
          <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-stone-600">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-orange-400 opacity-75" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-orange-500" />
            </span>
            In Bearbeitung ({activeJobs.length})
          </h3>
          <div className="space-y-3">
            {activeJobs.map(job => (
              <JobCard key={job.jobID} job={job} onDelete={onDelete} onRetry={onRetry} />
            ))}
          </div>
        </section>
      )}

      {completedJobs.length > 0 && (
        <section>
          <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-stone-600">
            <svg className="h-4 w-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            Abgeschlossen ({completedJobs.length})
          </h3>
          <div className="space-y-3">
            {completedJobs.map(job => (
              <JobCard key={job.jobID} job={job} onDelete={onDelete} onRetry={onRetry} />
            ))}
          </div>
        </section>
      )}

      {failedJobs.length > 0 && (
        <section>
          <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-stone-600">
            <svg className="h-4 w-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            Fehlgeschlagen ({failedJobs.length})
          </h3>
          <div className="space-y-3">
            {failedJobs.map(job => (
              <JobCard key={job.jobID} job={job} onDelete={onDelete} onRetry={onRetry} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
