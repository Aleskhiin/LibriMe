# LibriMe Frontend

> "Freedom starts in your ear."

LibriMe is a React frontend for converting documents into narrated audiobooks. Users upload a supported file, choose source and target language settings, and receive an audio result after backend processing.

## Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Available Scripts](#available-scripts)
- [Configuration](#configuration)
- [Routing](#routing)
- [Backend API](#backend-api)

## Features

- Landing page at `/` with authentication entry points and a direct path into the app
- Document upload via drag and drop or file picker
- Supported file extensions include images, PDF, text, Markdown, Office documents, HTML, CSV, and JSON
- Anonymous usage with a 10 MB upload limit, authenticated usage with a 50 MB upload limit
- Per-job settings for source language, target language, voice, and output splitting
- Voice selection is derived from the target language:
  - English (US): Female (v1)
  - German: Male (v1)
  - French: Male (v1)
- Grouped job list for active, completed, and failed jobs
- Completed jobs include an audio player and download action
- German and English UI translations through `src/i18n.tsx`
- Firebase authentication support

## Tech Stack

- [React 19](https://react.dev/) with [TypeScript](https://www.typescriptlang.org/)
- [Vite](https://vite.dev/) for development and production builds
- [React Router](https://reactrouter.com/) for client-side routing
- [Tailwind CSS](https://tailwindcss.com/) for styling
- [Firebase](https://firebase.google.com/) for authentication
- [ESLint](https://eslint.org/) with `typescript-eslint`

## Project Structure

```text
frontend/
├── public/
│   ├── logo.png              # Small legacy logo asset
│   ├── logoBig.png           # Main LibriMe logo asset
│   └── runtime-config.js     # Runtime configuration defaults
├── src/
│   ├── auth/
│   │   ├── AuthProvider.tsx  # Authentication context
│   │   └── firebase.ts       # Firebase initialization
│   ├── components/
│   │   ├── AuthMenu.tsx      # Login/account menu
│   │   ├── JobCard.tsx       # Single job entry
│   │   ├── JobList.tsx       # Grouped job overview
│   │   ├── LanguageToggle.tsx
│   │   └── UploadForm.tsx    # Upload form and job settings
│   ├── hooks/
│   │   └── useJobPolling.ts  # Polls active jobs
│   ├── pages/
│   │   ├── ImprintPage.tsx
│   │   └── LandingPage.tsx
│   ├── api.ts                # Backend API client
│   ├── App.tsx               # Main application view
│   ├── i18n.tsx              # UI translations
│   ├── main.tsx              # Router entry point
│   ├── runtimeConfig.ts      # Runtime config reader
│   └── types.ts              # Shared frontend types
├── DEPLOYMENT.md
├── package.json
└── server.mjs                # Production static server
```

## Setup

Prerequisites: [Node.js](https://nodejs.org/) LTS and npm.

```bash
npm install
npm run dev
```

The development server is available at `http://localhost:5173` by default.

## Available Scripts

| Script | Description |
| --- | --- |
| `npm run dev` | Starts the Vite development server with HMR |
| `npm run build` | Runs TypeScript project build and creates a production bundle |
| `npm run preview` | Serves the production build locally |
| `npm run lint` | Runs ESLint |
| `npm run start` | Starts the production static server from `server.mjs` |

## Configuration

The app reads runtime configuration from `runtime-config.js` through `src/runtimeConfig.ts`.

For local Vite development, environment variables can also be provided through `.env.local`:

```env
VITE_API_BASE_URL=/api
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_APP_ID=your-app-id
```

For Cloud Run deployment details, see [DEPLOYMENT.md](./DEPLOYMENT.md).

## Routing

| Path | Page | Description |
| --- | --- | --- |
| `/` | `LandingPage` | Product entry page with authentication options |
| `/app` | `App` | Main upload and job overview application |
| `/impressum` | `ImprintPage` | Legal notice page |

## Backend API

The frontend expects these backend endpoints, implemented by the API client in `src/api.ts`:

- `POST /jobs` creates a new narration job
- `GET /jobs` lists all jobs
- `GET /jobs/:jobID` returns one job status
- `PUT /jobs/:jobID` updates a job
- `GET /jobs/:jobID/result` downloads the generated audiobook
- `GET /health` checks backend availability
