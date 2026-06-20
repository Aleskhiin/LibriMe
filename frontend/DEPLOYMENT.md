# Frontend Cloud Run Deploy

This frontend is built as a Cloud Run container and reads runtime values from `runtime-config.js`.

## Prerequisites

- `gcloud` CLI installed and authenticated
- Google Cloud project selected
- Cloud Run API enabled

## Service Account

```bash
gcloud iam service-accounts create librime-frontend-sa \
  --display-name="LibriMe Frontend Service Account"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:librime-frontend-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:librime-frontend-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountTokenCreator"
```

## Build

```bash
gcloud builds submit --tag eu.gcr.io/PROJECT_ID/librifrontend .
```

## Deploy

```bash
gcloud run deploy librifrontend \
  --image eu.gcr.io/PROJECT_ID/librifrontend \
  --platform managed \
  --region europe-west3 \
  --service-account=librime-frontend-sa@PROJECT_ID.iam.gserviceaccount.com \
  --allow-unauthenticated \
  --set-env-vars="BACKEND_URL=https://YOUR-BACKEND-URL,\
GCS_BUCKET_NAME=YOUR_BUCKET_NAME,\
VITE_FIREBASE_API_KEY=YOUR_FIREBASE_API_KEY,\
VITE_FIREBASE_AUTH_DOMAIN=YOUR_PROJECT.firebaseapp.com,\
VITE_FIREBASE_PROJECT_ID=YOUR_PROJECT_ID,\
VITE_FIREBASE_APP_ID=YOUR_FIREBASE_APP_ID"
```

The frontend does not need a build-time backend URL. Cloud Run injects the runtime config through `runtime-config.js`, so the same image works across environments.
