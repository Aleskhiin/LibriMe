import { auth } from './auth/firebase';
import { getRuntimeConfig } from './runtimeConfig';

const DEFAULT_BASE_URL = 'https://libribackend-4130931555.europe-west3.run.app';
const BASE_URL = (getRuntimeConfig().apiBaseUrl ?? DEFAULT_BASE_URL).replace(/\/$/, '');
const USES_LOCAL_API_PROXY = /^\/api(?:\/|$)/i.test(BASE_URL);
const RESULT_BASE_URL = USES_LOCAL_API_PROXY ? BASE_URL : BASE_URL.replace(/\/api$/i, '');

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

async function withAuthHeaders(headers: HeadersInit = {}): Promise<HeadersInit> {
  const envToken = asString(import.meta.env.VITE_AUTH_TOKEN, '');
  const token = envToken || await auth.currentUser?.getIdToken();
  if (!token) {
    return headers;
  }

  return {
    ...headers,
    Authorization: token.startsWith('Bearer ') ? token : `Bearer ${token}`,
  };
}

async function authenticatedFetch(input: RequestInfo | URL, init: RequestInit = {}): Promise<Response> {
  return fetch(input, {
    ...init,
    credentials: 'include',
    headers: await withAuthHeaders(init.headers),
  });
}

function resolveResultUrl(url: string): string {
  if (/^https?:\/\//i.test(url)) {
    return USES_LOCAL_API_PROXY ? url : url.replace(/\/api(?=\/jobs\/)/i, '');
  }

  const path = url.replace(/^\/+/, '');
  const resultPath = path.replace(/^api\/(?=jobs\/)/i, '');
  return `${RESULT_BASE_URL}/${resultPath}`;
}

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
    fileLanguage: asString(raw.fileLanguage),
    translationLanguage: asString(raw.translationLanguage),
    voiceID: asString(raw.voiceID ?? raw.voiceId),
    splittingID: asString(raw.splittingID ?? raw.splittingId),
    status,
    progress: asNumber(raw.progress, status === 'COMPLETED' ? 100 : 0),
    downloadURL: downloadURL ? resolveResultUrl(downloadURL) : null,
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

  const res = await authenticatedFetch(`${BASE_URL}/jobs?${query.toString()}`, {
    method: 'POST',
    body: form,
  });

  const raw = await parseJsonResponse<RawJobRecord>(res, 'Upload');
  return normalizeJobRecord(raw);
}

export async function getJobStatus(jobID: string): Promise<JobStatusResponse> {
  const res = await authenticatedFetch(`${BASE_URL}/jobs/${encodeURIComponent(jobID)}`);
  const raw = await parseJsonResponse<RawJobRecord>(res, 'Status-Abfrage');
  return normalizeJobRecord(raw);
}

export async function listJobs(): Promise<JobRecord[]> {
  const res = await authenticatedFetch(`${BASE_URL}/jobs`);
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

  const res = await authenticatedFetch(`${BASE_URL}/jobs/${encodeURIComponent(params.jobID)}?${query.toString()}`, {
    method: 'PUT',
  });
  const raw = await parseJsonResponse<RawJobRecord>(res, 'Job-Update');
  return normalizeJobRecord(raw);
}

export async function getHealth(): Promise<string> {
  const res = await authenticatedFetch(`${BASE_URL}/health`);
  if (!res.ok) {
    throw new Error(`Health-Check fehlgeschlagen (${res.status})`);
  }
  return res.text();
}

export function getResultUrl(jobID: string): string {
  return resolveResultUrl(`/jobs/${encodeURIComponent(jobID)}/result`);
}

function getFilenameFromContentDisposition(header: string | null): string | null {
  if (!header) {
    return null;
  }

  const utf8Match = header.match(/filename\*=UTF-8''([^;]+)/i);
  if (utf8Match?.[1]) {
    return decodeURIComponent(utf8Match[1].replace(/"/g, ''));
  }

  const filenameMatch = header.match(/filename="?([^";]+)"?/i);
  return filenameMatch?.[1] ?? null;
}

function isExternalUrl(url: string): boolean {
  if (!/^https?:\/\//i.test(url)) {
    return false;
  }

  return !url.startsWith(window.location.origin) && !url.startsWith(RESULT_BASE_URL);
}

function startBrowserDownload(url: string, filename: string): void {
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
}

export async function downloadJobResult(resultUrl: string, fallbackFilename: string): Promise<void> {
  const resolvedUrl = resolveResultUrl(resultUrl);
  const fallbackDownloadName = fallbackFilename || 'download.wav';
  const fetchResult = isExternalUrl(resolvedUrl) ? fetch(resolvedUrl) : authenticatedFetch(resolvedUrl);
  const res = await fetchResult;

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Download fehlgeschlagen (${res.status}): ${text || res.statusText}`);
  }

  const contentType = res.headers.get('Content-Type') ?? '';
  if (contentType.includes('text/html') || contentType.includes('application/json')) {
    const text = await res.text();
    throw new Error(`Download hat keine Audiodatei geliefert: ${text.slice(0, 200) || contentType}`);
  }

  const blob = await res.blob();
  const objectUrl = window.URL.createObjectURL(blob);
  const filename =
    getFilenameFromContentDisposition(res.headers.get('Content-Disposition')) ||
    fallbackDownloadName;

  startBrowserDownload(objectUrl, filename);
  window.setTimeout(() => window.URL.revokeObjectURL(objectUrl), 1000);
}

export async function logoutApi(): Promise<void> {
  const res = await authenticatedFetch(`${BASE_URL}/auth/logout`, {
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error(`Logout failed: ${res.statusText}`);
  }
}

