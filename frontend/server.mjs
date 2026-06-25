import http from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const distDir = path.join(__dirname, 'dist');
const port = Number(process.env.PORT ?? 8080);

function contentType(filePath) {
  if (filePath.endsWith('.js')) return 'application/javascript; charset=utf-8';
  if (filePath.endsWith('.css')) return 'text/css; charset=utf-8';
  if (filePath.endsWith('.png')) return 'image/png';
  if (filePath.endsWith('.svg')) return 'image/svg+xml';
  if (filePath.endsWith('.json')) return 'application/json; charset=utf-8';
  if (filePath.endsWith('.html')) return 'text/html; charset=utf-8';
  return 'application/octet-stream';
}

function runtimeConfigScript() {
  const config = {
    apiBaseUrl: process.env.BACKEND_URL,
    firebaseApiKey: process.env.VITE_FIREBASE_API_KEY,
    firebaseAuthDomain: process.env.VITE_FIREBASE_AUTH_DOMAIN,
    firebaseProjectId: process.env.VITE_FIREBASE_PROJECT_ID,
    firebaseAppId: process.env.VITE_FIREBASE_APP_ID,
  };

  return `window.__LIBRIME_CONFIG__ = ${JSON.stringify(config)};`;
}

const server = http.createServer(async (req, res) => {
  res.setHeader('Cross-Origin-Opener-Policy', 'same-origin-allow-popups');
  const requestUrl = new URL(req.url ?? '/', `http://${req.headers.host ?? 'localhost'}`);
  let pathname = decodeURIComponent(requestUrl.pathname);

  if (pathname === '/runtime-config.js') {
    res.writeHead(200, { 'Content-Type': 'application/javascript; charset=utf-8', 'Cache-Control': 'no-store' });
    res.end(runtimeConfigScript());
    return;
  }

  if (pathname === '/') {
    pathname = '/index.html';
  }

  const candidatePath = path.join(distDir, pathname);

  try {
    const fileStats = await stat(candidatePath);
    if (fileStats.isFile()) {
      const file = await readFile(candidatePath);
      res.writeHead(200, { 'Content-Type': contentType(candidatePath) });
      res.end(file);
      return;
    }
  } catch {
    // fall through to SPA shell
  }

  const indexHtml = await readFile(path.join(distDir, 'index.html'), 'utf8');
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(indexHtml);
});

server.listen(port, () => {
  console.log(`LibriMe frontend listening on ${port}`);
});
