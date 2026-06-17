import { useEffect, useMemo, useRef } from 'react';
import { getJobStatus } from '../api';
import type { JobEntry } from '../types';

const POLL_INTERVAL_MS = 3000;

interface UseJobPollingProps {
  jobs: JobEntry[];
  onUpdate: (jobID: string, updates: Partial<JobEntry>) => void;
}

export function useJobPolling({ jobs, onUpdate }: UseJobPollingProps) {
  const activeJobIDs = useMemo(
    () => jobs
      .filter(job => job.status === 'QUEUED' || job.status === 'RUNNING')
      .map(job => job.jobID),
    [jobs]
  );

  const intervalsRef = useRef<Map<string, ReturnType<typeof setInterval>>>(new Map());

  useEffect(() => {
    for (const jobID of activeJobIDs) {
      if (!intervalsRef.current.has(jobID)) {
        const poll = async () => {
          try {
            const status = await getJobStatus(jobID);
            const { createdAt, ...updates } = status;
            onUpdate(jobID, {
              ...updates,
              ...(createdAt ? { createdAt: new Date(createdAt) } : {}),
            });

            if (status.status === 'COMPLETED' || status.status === 'FAILED') {
              const interval = intervalsRef.current.get(jobID);
              if (interval) {
                clearInterval(interval);
                intervalsRef.current.delete(jobID);
              }
            }
          } catch (err) {
            console.error(`Polling-Fehler fuer Job ${jobID}:`, err);
          }
        };

        poll();
        const interval = setInterval(poll, POLL_INTERVAL_MS);
        intervalsRef.current.set(jobID, interval);
      }
    }

    for (const [jobID, interval] of intervalsRef.current.entries()) {
      if (!activeJobIDs.includes(jobID)) {
        clearInterval(interval);
        intervalsRef.current.delete(jobID);
      }
    }
  }, [activeJobIDs, onUpdate]);

  useEffect(() => {
    const intervals = intervalsRef.current;

    return () => {
      for (const interval of intervals.values()) {
        clearInterval(interval);
      }
      intervals.clear();
    };
  }, []);
}
