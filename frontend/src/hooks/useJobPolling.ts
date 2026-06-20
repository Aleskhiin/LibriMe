import { useEffect, useRef } from 'react';
import { getJobStatus } from '../api';
import type { JobEntry } from '../types';

const POLL_INTERVAL_MS = 3000;

interface UseJobPollingProps {
  jobs: JobEntry[];
  onUpdate: (jobID: string, updates: Partial<JobEntry>) => void;
}

export function useJobPolling({ jobs, onUpdate }: UseJobPollingProps) {
  const activeJobIDs = jobs
    .filter(j => j.status === 'QUEUED' || j.status === 'RUNNING')
    .map(j => j.jobID);

  const intervalsRef = useRef<Map<string, ReturnType<typeof setInterval>>>(new Map());

  useEffect(() => {
    // Neue aktive Jobs starten
    for (const jobID of activeJobIDs) {
      if (!intervalsRef.current.has(jobID)) {
        const poll = async () => {
          try {
            const status = await getJobStatus(jobID);
            onUpdate(jobID, {
              status: status.status,
              progress: status.progress ?? 0,
              downloadURL: status.downloadURL ?? null,
              error: status.error ?? null,
            });

            if (status.status === 'COMPLETED' || status.status === 'FAILED') {
              const interval = intervalsRef.current.get(jobID);
              if (interval) {
                clearInterval(interval);
                intervalsRef.current.delete(jobID);
              }
            }
          } catch (err) {
            console.error(`Polling-Fehler für Job ${jobID}:`, err);
          }
        };

        // Sofort einmal abfragen
        poll();
        const interval = setInterval(poll, POLL_INTERVAL_MS);
        intervalsRef.current.set(jobID, interval);
      }
    }

    // Nicht mehr aktive Jobs stoppen
    for (const [jobID, interval] of intervalsRef.current.entries()) {
      if (!activeJobIDs.includes(jobID)) {
        clearInterval(interval);
        intervalsRef.current.delete(jobID);
      }
    }
  }, [activeJobIDs.join(',')]);

  // Cleanup beim Unmount
  useEffect(() => {
    return () => {
      for (const interval of intervalsRef.current.values()) {
        clearInterval(interval);
      }
      intervalsRef.current.clear();
    };
  }, []);
}
