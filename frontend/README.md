# LibriMe

> "Freedom starts in your ear."

LibriMe ist ein Web-Frontend, mit dem PDF-Dokumente in vertonte Hoerbuecher umgewandelt werden. Die Datei wird hochgeladen, serverseitig per OCR/TTS verarbeitet, und der Fortschritt der einzelnen Jobs wird live im Frontend verfolgt.

## Inhaltsverzeichnis

- [Funktionen](#funktionen)
- [Tech-Stack](#tech-stack)
- [Projektstruktur](#projektstruktur)
- [Setup](#setup)
- [Verfuegbare Skripte](#verfuegbare-skripte)
- [Konfiguration](#konfiguration)
- [Routing](#routing)
- [Backend-API](#backend-api)

## Funktionen

- **Landing Page** unter `/` mit kurzer Produkt-Vorstellung und Einstieg in die App
- **PDF-Upload** per Drag & Drop oder Dateiauswahl (max. 50 MB, nur `.pdf`)
- **Einstellungen pro Job**: Ausgangssprache, Zielsprache, Stimme und Aufteilung der Ausgabe (ganzes Dokument / seitenweise / absatzweise)
- **Live-Jobuebersicht**: laufende, abgeschlossene und fehlgeschlagene Auftraege werden automatisch per Polling aktualisiert
- **API-Health-Anzeige** im Header, zeigt ob das Backend erreichbar ist

## Tech-Stack

- [React 19](https://react.dev/) mit [TypeScript](https://www.typescriptlang.org/)
- [Vite](https://vite.dev/) als Build-Tool und Dev-Server
- [React Router](https://reactrouter.com/) fuer das Routing
- [Tailwind CSS](https://tailwindcss.com/) fuer das Styling
- [ESLint](https://eslint.org/) mit `typescript-eslint` fuer Linting

## Projektstruktur

```
frontend/
├── public/
│   ├── logo.png            # Logo (Header)
│   └── logoBig.png         # Logo (Landing Page)
├── src/
│   ├── pages/
│   │   └── LandingPage.tsx # Einstiegsseite mit "Zur App"-Button
│   ├── components/
│   │   ├── UploadForm.tsx  # PDF-Upload inkl. Einstellungen
│   │   ├── JobList.tsx     # Gruppierte Job-Uebersicht
│   │   └── JobCard.tsx     # Einzelner Job-Eintrag
│   ├── hooks/
│   │   └── useJobPolling.ts # Pollt laufende Jobs in Intervallen
│   ├── api.ts               # Backend-Anbindung (fetch-Wrapper)
│   ├── types.ts             # Gemeinsame Typdefinitionen
│   ├── App.tsx               # Hauptanwendung (Upload + Jobliste)
│   └── main.tsx              # Einstiegspunkt inkl. Router-Konfiguration
├── .env.local                # Lokale Umgebungsvariablen
└── package.json
```

## Setup

Voraussetzung: [Node.js](https://nodejs.org/) (empfohlen: aktuelle LTS-Version) und npm.

```bash
# Abhaengigkeiten installieren
npm install

# Entwicklungsserver starten
npm run dev
```

Die App ist anschliessend standardmaessig unter `http://localhost:5173` erreichbar.

## Verfuegbare Skripte

| Skript           | Beschreibung                                      |
|------------------|----------------------------------------------------|
| `npm run dev`    | Startet den Vite-Entwicklungsserver mit HMR        |
| `npm run build`  | Typchecking (`tsc -b`) und Production-Build        |
| `npm run preview`| Zeigt den Production-Build lokal an                |
| `npm run lint`   | Prueft den Code mit ESLint                          |

## Konfiguration

Die Backend-URL wird ueber eine Umgebungsvariable gesteuert:

```env
# .env.local
VITE_API_BASE_URL=/api
```

Ist die Variable nicht gesetzt, faellt die App auf eine fest hinterlegte Standard-URL zurueck (siehe `src/api.ts`). Fuer lokale Entwicklung gegen ein anderes Backend einfach `VITE_API_BASE_URL` in `.env.local` anpassen.

## Routing

| Pfad   | Seite          | Beschreibung                                              |
|--------|----------------|-------------------------------------------------------------|
| `/`    | `LandingPage`  | Einstiegsseite mit Produktvorstellung und "Zur App"-Button |
| `/app` | `App`          | Eigentliche Anwendung: Upload-Formular und Jobuebersicht   |

Die Landing Page leitet per Button-Klick clientseitig (ohne vollen Page-Reload) zu `/app` weiter.

## Backend-API

Das Frontend erwartet ein Backend mit folgenden Endpunkten (siehe `src/api.ts`):

- `POST /jobs` – neuen Vertonungs-Job anlegen (Datei + Query-Parameter)
- `GET /jobs` – alle Jobs auflisten
- `GET /jobs/:jobID` – Status eines einzelnen Jobs abfragen
- `PUT /jobs/:jobID` – Job aktualisieren
- `GET /jobs/:jobID/result` – fertiges Hoerbuch herunterladen
- `GET /health` – Health-Check des Backends
