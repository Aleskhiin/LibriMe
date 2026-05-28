import type { JobState } from './api';

export interface JobEntry {
  jobID: string;
  fileName: string;
  fileLanguage: string;
  translationLanguage: string;
  voiceID: string;
  splittingID: string;
  status: JobState;
  progress: number;
  downloadURL: string | null;
  error: string | null;
  createdAt: Date;
}
