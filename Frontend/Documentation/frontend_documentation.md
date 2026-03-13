# 🎧 librime Frontend

**librime** ist das Frontend eines Projekts, das es ermöglicht, PDF- oder Bilddateien hochzuladen, sie serverseitig zu verarbeiten und als Audio-Dateien im Browser wiederzugeben.  
Dieses Frontend wurde mit **React**, **TypeScript**, **Vite** und **Tailwind CSS** umgesetzt.

---

## 🧩 Tech Stack

| Bereich | Technologie |
|----------|-------------|
| Framework | React (TypeScript) |
| Build Tool | Vite |
| Styling | Tailwind CSS |
| Routing | React Router DOM |
| Paketmanager | npm |

---

## 🚀 Projekt Setup

###  React + TypeScript + Vite erstellen
```bash
npm create vite@latest librime -- --template react-ts
cd librime
npm install
```

###  Router hinzufügen
```bash
npm install react-router-dom
```

**`src/main.tsx`**
```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import './index.css'
import App from './App.tsx'

const router = createBrowserRouter([{ path: '/', element: <App /> }])

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
```

---

## Tailwind CSS Setup

### Installation
```bash
npm install -D tailwindcss@^3 postcss autoprefixer
npx tailwindcss init -p
```

### `tailwind.config.js`
```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: { extend: {} },
  plugins: [],
}
```

### `postcss.config.js`
```js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

### `src/index.css`
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

---

##  TypeScript Pfad-Alias
**`tsconfig.json`**
```json
{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ],
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

---

##  Testseite & Bilder

### Bilder
Lege in `public/` zwei Bilder ab:
```
public/
├─ logo.png       # Tab-Icon (Favicon)
├─ logoBig.png    # Beispielbild auf der Seite
```

### Favicon in `index.html`
```html
<link rel="icon" type="image/png" href="/logo.png" />
```

### Beispielinhalt `src/App.tsx`
```tsx
export default function App() {
  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="mx-auto max-w-3xl text-center">
        <h1 className="text-3xl font-bold tracking-tight text-gray-800">
          librime
        </h1>
        <p className="mt-2 text-gray-700">
          React + TypeScript + Vite + Tailwind – Grundsetup steht.
        </p>

        <div className="mt-6 rounded-xl border bg-white p-6 shadow">
          <img
            src="/logoBig.png"
            alt="librime Logo groß"
            className="mx-auto h-40 w-auto"
          />
          <p className="mt-2 text-sm text-gray-600">
            Beispielbild erfolgreich eingebunden.
          </p>
        </div>
      </div>
    </main>
  )
}
```

---

##  Nützliche npm-Befehle

| Befehl | Beschreibung |
|--------|---------------|
| `npm run dev` | Lokalen Entwicklungsserver starten |
| `npm run build` | Produktions-Build erstellen |
| `npm run preview` | Produktions-Build lokal ansehen |

---

##  Troubleshooting

| Problem | Lösung |
|----------|---------|
| **Favicon wird nicht angezeigt** | Browser-Cache leeren oder Query `?v=1` anhängen |
| **Tailwind-Warnung: “content option missing”** | `tailwind.config.js` prüfen |
| **Keine Styles sichtbar** | Tailwind-Direktiven in `index.css` überprüfen |
| **Bild nicht angezeigt** | Datei im `public/`-Ordner vorhanden? Pfad prüfen (`/logoBig.png`) |

---

##  Zusammenfassung

**librime Frontend** ist ein leichtgewichtiges, modernes React-Projekt mit:
-  **TypeScript** für Typsicherheit
-  **Vite** für ultraschnelles Development
-  **Tailwind CSS** für schlankes Styling
-  **React Router** für Navigation  


