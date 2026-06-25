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

gcloud projects add-iam-policy-binding librime \
  --member="serviceAccount:librime-frontend-sa@librime.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

gcloud projects add-iam-policy-binding librime \
  --member="serviceAccount:librime-frontend-sa@librime.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountTokenCreator"
```

## Build

```bash
gcloud builds submit --tag eu.gcr.io/librime/librifrontend ./frontend
```

## Deploy

```bash
gcloud run deploy librifrontend \
  --image eu.gcr.io/librime/librifrontend \
  --platform managed \
  --region europe-west4 \
  --service-account=librime-frontend-sa@librime.iam.gserviceaccount.com \
  --allow-unauthenticated \
  --set-env-vars="BACKEND_URL=https://libribackend-4130931555.europe-west3.run.app,\
GCS_BUCKET_NAME=librime-assets-1,\
VITE_FIREBASE_API_KEY=AIzaSyCLS4upLJ1miLntEeh-4Ba9ZhV8_v4KFaw,\
VITE_FIREBASE_AUTH_DOMAIN=librime.firebaseapp.com,\
VITE_FIREBASE_PROJECT_ID=librime,\
VITE_FIREBASE_APP_ID=1:4130931555:web:a1b2c3d4e5f6g7"
```

The frontend does not need a build-time backend URL. Cloud Run injects the runtime config through `runtime-config.js`, so the same image works across environments.
