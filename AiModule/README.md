# Getting Started — AI Module

## Overview

The AI Module is a Python-based microservice that converts documents and images into audio files (audiobooks). It receives jobs from Google Cloud Pub/Sub, processes the input file, and reports the result back to the Backend.

The processing pipeline consists of three steps:

1. **Text extraction** — read text from the uploaded file
2. **Translation** (optional) — translate the text if source and target language differ
3. **Text-to-Speech** — generate a WAV audio file from the text

---

## Packages

You will need to install the following:

- Python ≥ 3.11
- Docker ≤ 4.49.0
- Google Cloud Pub/Sub subscription
- Google Cloud Storage bucket

All Python dependencies are listed in `AIModule/requirements.txt`.

---

## Running with Docker

The recommended way to run the AI Module is via Docker:

```bash
docker build -t librime-ai ./AIModule
docker run \
  -e PUBSUB_PROJECT_ID=<your-project-id> \
  -e PUBSUB_SUBSCRIPTION=<your-subscription-id> \
  -e GCS_BUCKET_NAME=<your-bucket-name> \
  -e BACKEND_URL=http://<backend-host>:<port> \
  -p 8080:8080 \
  librime-ai
```

The Dockerfile pre-downloads all TTS models and Argos Translate language packages at build time, so no internet access is required at runtime.

---

## Environment Variables

| Variable              | Required | Description                                              |
|-----------------------|----------|----------------------------------------------------------|
| `PUBSUB_PROJECT_ID`   | Yes      | Google Cloud project ID for Pub/Sub                     |
| `PUBSUB_SUBSCRIPTION` | Yes      | Pub/Sub subscription name to pull jobs from             |
| `GCS_BUCKET_NAME`     | Yes      | GCS bucket for input file downloads and audio uploads   |
| `BACKEND_URL`         | Yes      | Base URL of the Backend service for job status updates  |
| `USE_PULL_WORKER`     | No       | Set to `false` to disable the pull worker (default: `true`) |

---

## Architecture

The service exposes a FastAPI HTTP server on port `8080` and simultaneously runs a background thread that pulls messages from Pub/Sub.

```
Pub/Sub Subscription
        │
        ▼
 PubSubJobHandler
        │
        ├─ Download input file from GCS
        │
        ├─ FeatureWorker.run()
        │       │
        │       ├─ [Image]    OCRImageReader  → text
        │       └─ [Document] DocumentReader  → text / chunks
        │               │
        │               ├─ TranslatorFeature (optional)
        │               └─ TextToSpeechFeature → WAV file(s)
        │
        ├─ Upload audio to GCS
        └─ BackendClient.update_status()
```

### Pull vs. Push Worker

- **Pull worker** (default): the service actively polls the Pub/Sub subscription in a background thread.
- **Push mode**: set `USE_PULL_WORKER=false` and configure Pub/Sub to deliver messages to the `/pubsub/push` HTTP endpoint.

---

## Supported File Formats

### Documents

| Format              | Extensions                     | Splitting modes        |
|---------------------|-------------------------------|------------------------|
| PDF                 | `.pdf`                        | document, pages, paragraphs |
| Word                | `.doc`, `.docx`               | document               |
| OpenDocument Text   | `.odt`                        | document               |
| Presentation        | `.ppt`, `.pptx`               | document, pages (slides) |
| Plain Text          | `.txt`                        | document, paragraphs   |
| Markdown            | `.md`, `.markdown`            | document               |
| HTML                | `.html`, `.htm`               | document               |
| CSV                 | `.csv`                        | document               |
| JSON                | `.json`                       | document               |

### Images (OCR via Tesseract)

`.png`, `.jpg`, `.jpeg`, `.bmp`, `.tif`, `.tiff`, `.webp`

---

## Splitting Modes

A job can request one of three splitting modes, which controls how many audio files are generated:

| Mode        | Pub/Sub value  | Behaviour                                  |
|-------------|----------------|--------------------------------------------|
| `DOCUMENT`  | `document`     | One audio file for the entire document     |
| `PAGE`      | `pages`        | One audio file per page or slide           |
| `PARAGRAPH` | `paragraphs`   | One audio file per paragraph               |

---

## Translation

Translation is performed by [Argos Translate](https://github.com/argosopentech/argos-translate) and runs fully offline. The following language pairs are pre-installed in the Docker image:

- `de` ↔ `en`
- `de` ↔ `fr`
- `en` ↔ `fr`

Translation is skipped when source language and target language are identical.

---

## Text-to-Speech

Speech synthesis uses [Coqui TTS](https://github.com/coqui-ai/TTS) with Tacotron2-DDC models. The following language models are pre-downloaded:

| Language | Model                                |
|----------|--------------------------------------|
| German   | `tts_models/de/thorsten/tacotron2-DDC` |
| English  | `tts_models/en/ljspeech/tacotron2-DDC` |
| French   | `tts_models/fr/mai/tacotron2-DDC`    |

GPU acceleration is used automatically when a CUDA-capable device is available.

---

## HTTP Endpoints

| Method | Path            | Description                                      |
|--------|-----------------|--------------------------------------------------|
| `GET`  | `/`             | Health check — returns `{"status": "ok"}`       |
| `GET`  | `/health`       | Health check — returns `{"status": "ok"}`       |
| `POST` | `/pubsub/push`  | Receives a Pub/Sub push message (push mode only) |

---

## Pub/Sub Message Format

The service expects JSON messages with the following fields:

```json
{
  "jobID": "abc123",
  "dataPath": "uploads/abc123/document.pdf",
  "fileLanguage": "DE_DE",
  "translationLanguage": "EN_US",
  "splittingType": "DOCUMENT"
}
```

| Field                 | Description                                              |
|-----------------------|----------------------------------------------------------|
| `jobID`               | Unique job identifier, used as output prefix in GCS     |
| `dataPath`            | Path to the input file inside the GCS bucket            |
| `fileLanguage`        | Source language (format: `LANG_REGION`, e.g. `DE_DE`)  |
| `translationLanguage` | Target language for translation and TTS                 |
| `splittingType`       | One of `DOCUMENT`, `PAGE`, `PARAGRAPH`                  |

---

## Job Status Updates

The AI Module reports job progress to the Backend via `PUT /jobs/{jobID}`:

| Status      | When                                         |
|-------------|----------------------------------------------|
| `RUNNING`   | Job has started processing                   |
| `COMPLETED` | Audio uploaded successfully to GCS           |
| `FAILED`    | An unrecoverable error occurred              |
