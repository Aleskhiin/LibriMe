export interface RuntimeConfig {
  apiBaseUrl?: string;
  firebaseApiKey?: string;
  firebaseAuthDomain?: string;
  firebaseProjectId?: string;
  firebaseAppId?: string;
}

declare global {
  interface Window {
    __LIBRIME_CONFIG__?: RuntimeConfig;
  }
}

function normalizeValue(value: string | undefined): string | undefined {
  const trimmed = value?.trim();
  return trimmed ? trimmed : undefined;
}

export function getRuntimeConfig(): RuntimeConfig {
  if (typeof window !== 'undefined' && window.__LIBRIME_CONFIG__) {
    return window.__LIBRIME_CONFIG__;
  }

  return {
    apiBaseUrl: normalizeValue(import.meta.env.VITE_API_BASE_URL),
    firebaseApiKey: normalizeValue(import.meta.env.VITE_FIREBASE_API_KEY),
    firebaseAuthDomain: normalizeValue(import.meta.env.VITE_FIREBASE_AUTH_DOMAIN),
    firebaseProjectId: normalizeValue(import.meta.env.VITE_FIREBASE_PROJECT_ID),
    firebaseAppId: normalizeValue(import.meta.env.VITE_FIREBASE_APP_ID),
  };
}
