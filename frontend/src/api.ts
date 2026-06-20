const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8080';

export interface JobCreatedResponse {
  jobID: string;
  status: JobState;
  message: string;
  StatusURL: string;
}

export interface JobStatusResponse {
  jobID: string;
  status: JobState;
  progress: number;
  downloadURL: string | null;
  error: string | null;
}

export type JobState = 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED';

export interface CreateJobParams {
  file: File;
  fileLanguage: string;
  translationLanguage: string;
  voiceID: string;
  splittingID: string;
}

export async function createJob(params: CreateJobParams): Promise<JobCreatedResponse> {
  const form = new FormData();
  form.append('file', params.file);
  form.append('fileLanguage', params.fileLanguage);
  form.append('translationLanguage', params.translationLanguage);
  form.append('voiceID', params.voiceID);
  form.append('splittingID', params.splittingID);

  const res = await fetch(`${BASE_URL}/jobs`, {
    method: 'POST',
    body: form,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Upload fehlgeschlagen (${res.status}): ${text}`);
  }

  return res.json();
}

export async function getJobStatus(jobID: string): Promise<JobStatusResponse> {
  const res = await fetch(`${BASE_URL}/jobs/${jobID}`);
  if (!res.ok) {
    throw new Error(`Status-Abfrage fehlgeschlagen (${res.status})`);
  }
  return res.json();
}

export function getResultUrl(jobID: string): string {
  return `${BASE_URL}/jobs/${jobID}/result`;
}
