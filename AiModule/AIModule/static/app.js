// ==================== Sprach-Setup (UI) ====================
const langSelect  = document.getElementById('language');
const htmlEl      = document.documentElement;
// UI-Knoten
const taglineEl   = document.getElementById('tagline');
const subtitleEl  = document.getElementById('subtitle');
const dropZone    = document.getElementById('drop-zone');
const fileInput   = document.getElementById('fileInput');
const form        = document.getElementById('uploadForm');
const statusDiv   = document.getElementById('status');
const downloadLink = document.getElementById('download-link');
const downloadsDiv = document.getElementById('downloads');
const uploadBtn   = document.getElementById('upload-btn');
const langLabel   = document.getElementById('language-label');
// Übersetzungs-Sprachen
const fromLabel   = document.getElementById('from-label');
const toLabel     = document.getElementById('to-label');
const fromSelect  = document.getElementById('from-lang');
const toSelect    = document.getElementById('to-lang');
const swapBtn     = document.getElementById('swap-btn');
// Einlese-Modus
const modeLabel   = document.getElementById('mode-label');
const modeSelect  = document.getElementById('read-mode');

// UI-Texte (nur Oberflächentexte)
const UI_TEXTS = {
  de: {
    langLabel: 'Anzeigesprache:',
    tagline: '"Freedom starts in your ear."',
    subtitle: 'Datei Upload & Download',
    drop: 'Ziehe deine Datei hierher oder klicke zum Auswählen',
    uploadBtn: '📤 Hochladen',
    download: '📥 Datei herunterladen',
    fromLabel: 'Ausgangssprache:',
    toLabel: 'Zielsprache:',
    modeLabel: 'Einlesemodus:',
    modeOptions: {
      document: 'Ganzes Dokument',
      pages: 'Seitenweise',
      paragraphs: 'Abschnittsweise',
    },
    uploading: 'Datei wird hochgeladen...',
    started: 'Verarbeitung gestartet...',
    processing: (s) => `Wird verarbeitet... (${s})`,
    done: 'Fertig!',
    multipleFiles: 'Mehrere Dateien verfügbar:',
    errorPrefix: 'Fehler: ',
    timeout: 'Timeout: Verarbeitung dauert zu lange',
    statusJsonErr: (ct) => `Status-Antwort kein JSON (Content-Type: ${ct}).`,
    expectJson: (ct) => `Erwartete JSON-Antwort, bekam Content-Type: "${ct}".`,
    uploadFailed: (code) => `Upload fehlgeschlagen: HTTP ${code}.`,
    noJobId: (data) => `Upload-Antwort ohne job_id. Daten: ${JSON.stringify(data)}`
  },
  en: {
    langLabel: 'Display language:',
    tagline: '"Freedom starts in your ear."',
    subtitle: 'File Upload & Download',
    drop: 'Drag your file here or click to select',
    uploadBtn: '📤 Upload',
    download: '📥 Download file',
    fromLabel: 'Source language:',
    toLabel: 'Target language:',
    modeLabel: 'Reading mode:',
    modeOptions: {
      document: 'Whole document',
      pages: 'Per page',
      paragraphs: 'Per paragraph',
    },
    uploading: 'Uploading file...',
    started: 'Processing started...',
    processing: (s) => `Processing... (${s})`,
    done: 'Done!',
    multipleFiles: 'Multiple files available:',
    errorPrefix: 'Error: ',
    timeout: 'Timeout: Processing takes too long',
    statusJsonErr: (ct) => `Status response is not JSON (Content-Type: ${ct}).`,
    expectJson: (ct) => `Expected JSON response, got Content-Type: "${ct}".`,
    uploadFailed: (code) => `Upload failed: HTTP ${code}.`,
    noJobId: (data) => `Upload response missing job_id. Data: ${JSON.stringify(data)}`
  }
};

function getUILang() {
  return localStorage.getItem('libriMeLang') || 'de';
}
function setUILang(lang) {
  localStorage.setItem('libriMeLang', lang);
  htmlEl.lang = lang;
}
function applyUILanguage() {
  const lang = getUILang();
  const t = UI_TEXTS[lang];
  if (langLabel)   langLabel.textContent = t.langLabel;
  if (taglineEl)   taglineEl.textContent = t.tagline;
  if (subtitleEl)  subtitleEl.textContent = t.subtitle;
  if (fromLabel)   fromLabel.textContent = t.fromLabel;
  if (toLabel)     toLabel.textContent = t.toLabel;
  if (modeLabel)   modeLabel.textContent = t.modeLabel;
  // Modus-Optionstexte anpassen
  if (modeSelect) {
    [...modeSelect.options].forEach(opt => {
      const key = opt.value;
      if (t.modeOptions[key]) opt.textContent = t.modeOptions[key];
    });
  }
  // Drop-Zone Default-Text nur setzen, wenn keine Datei gewählt
  if (dropZone && (!fileInput || !fileInput.files || fileInput.files.length === 0)) {
    dropZone.textContent = t.drop;
  }
  if (downloadLink) downloadLink.textContent = t.download;
  if (uploadBtn)    uploadBtn.textContent = t.uploadBtn;
  htmlEl.lang = lang;
}

// Init UI-Sprache
if (langSelect) {
  langSelect.value = getUILang();
  applyUILanguage();
  langSelect.addEventListener('change', () => {
    setUILang(langSelect.value);
    applyUILanguage(); // kein Reload
  });
} else {
  setUILang(getUILang());
  applyUILanguage();
}

// ==================== Übersetzungs-Sprachen (from/to) ====================
// Swap-Button: Ausgangs- und Zielsprache tauschen
if (swapBtn) {
  swapBtn.addEventListener('click', () => {
    const from = fromSelect.value;
    const to = toSelect.value;
    fromSelect.value = to;
    toSelect.value = from;
  });
}

// ==================== Drag & Drop ====================
dropZone.addEventListener('click', () => {
  fileInput.click();
});
dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('dragover');
});
dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('dragover');
});
dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file) {
    fileInput.files = e.dataTransfer.files;
    dropZone.textContent = file.name;
  }
});

// ==================== Upload & Polling ====================
function t() {
  return UI_TEXTS[getUILang()];
}

function renderMultipleDownloads(urls) {
  downloadsDiv.innerHTML = '';
  const title = document.createElement('div');
  title.style.margin = '0.5rem 0';
  title.textContent = t().multipleFiles;
  downloadsDiv.appendChild(title);

  const list = document.createElement('ol');
  list.style.paddingLeft = '1.2rem';

  urls.forEach((u, i) => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = u;
    a.textContent = `📥 ${i + 1}`;
    a.download = '';
    li.appendChild(a);
    list.appendChild(li);
  });
  downloadsDiv.appendChild(list);
  downloadsDiv.style.display = 'block';
  downloadLink.style.display = 'none';
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  statusDiv.textContent = t().uploading;
  downloadLink.style.display = "none";
  downloadsDiv.style.display = "none";
  downloadsDiv.innerHTML = "";

  const formData = new FormData(form);
  // Einlese-Modus auch in FormData mitschicken
  formData.append('read_mode', modeSelect ? modeSelect.value : 'document');
  // Optional: from/to ebenfalls mitschicken (neben Headern)
  formData.append('from_lang', fromSelect.value);
  formData.append('to_lang', toSelect.value);

  try {
    const response = await fetch('http://localhost:5000/upload', {
      method: 'POST',
      body: formData,
      headers: {
        // UI-Sprache
        'X-Language': getUILang(),
        // Übersetzungsparameter
        'X-From-Lang': fromSelect.value, // 'de' / 'en'
        'X-To-Lang'  : toSelect.value,   // 'de' / 'en'
        // Einlese-Modus
        'X-Read-Mode': modeSelect ? modeSelect.value : 'document'
      }
    });

    if (!(response.status === 202 || response.status === 200)) {
      const bodyPreview = await response.clone().text().catch(() => '');
      console.error('Upload-Fehlerbody:', bodyPreview);
      throw new Error(`${t().uploadFailed(response.status)} Body:\n${bodyPreview.slice(0, 300)}`);
    }
    const ct = response.headers.get('content-type') || '';
    if (!ct.includes('application/json')) {
      const bodyPreview = await response.clone().text().catch(() => '');
      console.error('Unerwarteter Content-Type:', ct, 'Body:', bodyPreview);
      throw new Error(`${t().expectJson(ct)} Body:\n${bodyPreview.slice(0, 300)}`);
    }

    let data;
    try {
      data = await response.json();
    } catch (parseErr) {
      const bodyPreview = await response.clone().text().catch(() => '');
      console.error('JSON-Parse-Fehler:', parseErr, 'Body:', bodyPreview);
      throw new Error(`JSON-Parse-Error: ${parseErr.message}`);
    }
    const { job_id, error } = (data && typeof data === 'object') ? data : {};
    if (error) throw new Error(error);
    if (!job_id) {
      console.error('Antwortdaten:', data);
      throw new Error(t().noJobId(data));
    }

    statusDiv.textContent = t().started;

    // Polling
    const pollIntervalMs = 2000;
    const maxWaitMs = 30 * 60 * 1000; // 30 min
    const startedAt = Date.now();
    const poll = async () => {
      const r = await fetch(`http://localhost:5000/status/${job_id}`, {
        cache: 'no-store',
        headers: {
          'X-Language' : getUILang(),
          'X-From-Lang': fromSelect.value,
          'X-To-Lang'  : toSelect.value
        }
      });
      if (!r.ok) throw new Error(`Status-Fehler: ${r.status}`);
      const ctStatus = r.headers.get('content-type') || '';
      if (!ctStatus.includes('application/json')) {
        const statusBody = await r.clone().text().catch(() => '');
        throw new Error(`${t().statusJsonErr(ctStatus)} Body:\n${statusBody.slice(0,300)}`);
      }
      let st;
      try {
        st = await r.json();
      } catch (err) {
        const statusBody = await r.clone().text().catch(() => '');
        console.error('Status JSON-Parse-Fehler:', err, 'Body:', statusBody);
        throw new Error(`Status JSON-Parse-Error: ${err.message}`);
      }

      if (st.status === 'done') {
        statusDiv.textContent = t().done;
        // Mehrere Downloads bevorzugen, falls vorhanden
        if (Array.isArray(st.downloads) && st.downloads.length > 0) {
          const urls = st.downloads.map(p => `http://localhost:5000${p}`);
          renderMultipleDownloads(urls);
        } else if (st.download) {
          downloadLink.href = "http://localhost:5000" + st.download;
          downloadLink.textContent = t().download;
          downloadLink.style.display = "block";
          downloadsDiv.style.display = "none";
        }
        return;
      }
      if (st.status === 'error') {
        throw new Error(st.error || "Unknown processing error");
      }

      statusDiv.textContent = t().processing(st.status);
      if (Date.now() - startedAt > maxWaitMs) {
        throw new Error(t().timeout);
      }
      setTimeout(poll, pollIntervalMs);
    };
    setTimeout(poll, pollIntervalMs);

  } catch (error) {
    statusDiv.textContent = t().errorPrefix + error.message;
    console.error(error);
  }
});
``