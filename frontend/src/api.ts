const DEFAULT_BASE_URL = 'https://libribackend-4130931555.europe-west3.run.app';
const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? DEFAULT_BASE_URL).replace(/\/$/, '');

export type JobState = 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED';

export interface JobRecord {
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
  outputFilePath: string | null;
  createdAt: string | null;
}

export type JobCreatedResponse = JobRecord;
export type JobStatusResponse = JobRecord;

export interface CreateJobParams {
  file: File;
  fileLanguage: string;
  translationLanguage: string;
  voiceID: string;
  splittingID: string;
}

export interface UpdateJobParams {
  jobID: string;
  status: JobState;
  progress: number;
  outputFilePath: string;
}

type RawJobRecord = Record<string, unknown>;

function asString(value: unknown, fallback = ''): string {
  return typeof value === 'string' ? value : fallback;
}

function asNumber(value: unknown, fallback = 0): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
}

function asJobState(value: unknown): JobState {
  return value === 'QUEUED' || value === 'RUNNING' || value === 'COMPLETED' || value === 'FAILED'
    ? value
    : 'QUEUED';
}

function normalizeJobRecord(raw: RawJobRecord): JobRecord {
  const jobID = asString(raw.jobID ?? raw.jobId ?? raw.id);
  const status = asJobState(raw.status);
  const outputFilePath = asString(raw.outputFilePath ?? raw.output_file_path, '');
  const downloadURL = asString(raw.downloadURL ?? raw.downloadUrl ?? raw.resultURL ?? raw.resultUrl, '');

  return {
    jobID,
    fileName: asString(raw.fileName ?? raw.filename ?? raw.originalFileName, jobID || 'Unbekannte Datei'),
    fileLanguage: asString(raw.fileLanguage, 'en_US'),
    translationLanguage: asString(raw.translationLanguage, 'en_US'),
    voiceID: asString(raw.voiceID ?? raw.voiceId, 'male_v1'),
    splittingID: asString(raw.splittingID ?? raw.splittingId, 'DOCUMENT'),
    status,
    progress: asNumber(raw.progress, status === 'COMPLETED' ? 100 : 0),
    downloadURL: downloadURL || null,
    error: asString(raw.error, '') || null,
    outputFilePath: outputFilePath || null,
    createdAt: asString(raw.createdAt ?? raw.created_at ?? raw.timestamp, '') || null,
  };
}

async function parseJsonResponse<T>(res: Response, context: string): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${context} fehlgeschlagen (${res.status}): ${text || res.statusText}`);
  }

  return res.json() as Promise<T>;
}

export async function createJob(params: CreateJobParams): Promise<JobCreatedResponse> {
  const query = new URLSearchParams({
    fileLanguage: params.fileLanguage,
    translationLanguage: params.translationLanguage,
    voiceID: params.voiceID,
    splittingID: params.splittingID,
  });

  const form = new FormData();
  form.append('file', params.file);

  const res = await fetch(`${BASE_URL}/jobs?${query.toString()}`, {
    method: 'POST',
    body: form,
  });

  const raw = await parseJsonResponse<RawJobRecord>(res, 'Upload');
  return normalizeJobRecord(raw);
}

export async function getJobStatus(jobID: string): Promise<JobStatusResponse> {
  const res = await fetch(`${BASE_URL}/jobs/${encodeURIComponent(jobID)}`);
  const raw = await parseJsonResponse<RawJobRecord>(res, 'Status-Abfrage');
  return normalizeJobRecord(raw);
}

export async function listJobs(): Promise<JobRecord[]> {
  const res = await fetch(`${BASE_URL}/jobs`);
  const raw = await parseJsonResponse<RawJobRecord[] | { value?: RawJobRecord[] }>(res, 'Jobliste');
  const jobs = Array.isArray(raw) ? raw : raw.value ?? [];
  return jobs.map(normalizeJobRecord).filter(job => job.jobID);
}

export async function updateJob(params: UpdateJobParams): Promise<JobRecord> {
  const query = new URLSearchParams({
    status: params.status,
    progress: String(params.progress),
    outputFilePath: params.outputFilePath,
  });

  const res = await fetch(`${BASE_URL}/jobs/${encodeURIComponent(params.jobID)}?${query.toString()}`, {
    method: 'PUT',
  });
  const raw = await parseJsonResponse<RawJobRecord>(res, 'Job-Update');
  return normalizeJobRecord(raw);
}

export async function getHealth(): Promise<string> {
  const res = await fetch(`${BASE_URL}/health`);
  if (!res.ok) {
    throw new Error(`Health-Check fehlgeschlagen (${res.status})`);
  }
  return res.text();
}

export function getResultUrl(jobID: string): string {
  return `${BASE_URL}/jobs/${encodeURIComponent(jobID)}/result`;
}
