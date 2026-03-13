# app_server.py
import os
import sys
import uuid
import threading
import asyncio
from time import time
from flask import Flask, json, make_response, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS

# ---------- Pfade vorbereiten ----------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # .../AIModule/standalone
AIMODULE_DIR = os.path.dirname(CURRENT_DIR)               # .../AIModule
if AIMODULE_DIR not in sys.path:
    sys.path.insert(0, AIMODULE_DIR)

from app_pkg.FeatureWorker import FeatureWorker

# ---------- Flask Setup ----------
app = Flask(__name__)
CORS(app)  # Erlaubt Anfragen vom Live-Server / Frontend
app.config['PROPAGATE_EXCEPTIONS'] = True

# Einheitliche JSON-Fehlerantworten:
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal Server Error"}), 500

@app.errorhandler(Exception)
def unhandled(e):
    # In Produktion bitte verfeinern und kein Exception-Detail nach außen geben
    return jsonify({"error": f"Unhandled exception: {e}"}), 500

UPLOAD_FOLDER = os.path.join(AIMODULE_DIR, "runtime_uploads")
OUTPUT_FOLDER = os.path.join(AIMODULE_DIR, "runtime_audio")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Optionales Referenz-Audio
REF_AUDIO_PATH = os.path.join(AIMODULE_DIR, "AiModule", "app_pkg", "Resources", "Audio", "unbenannt.wav")
if not os.path.exists(REF_AUDIO_PATH):
    REF_AUDIO_PATH = None

# ---------- In-Memory Job Store (Demo) ----------
# job_id -> {
#   "status": "queued|running|done|error",
#   "download": str|None,         # erster Download-Link (Abwärtskompatibilität)
#   "downloads": [str, ...]|None, # mehrere Download-Links (neu)
#   "error": str|None,
#   "started": ts,
#   "progress": int,
#   "language": "de|en",          # UI-Sprache
#   "from_lang": "de|en",         # Übersetzungs-Quelle
#   "to_lang": "de|en",           # Übersetzungs-Ziel
#   "read_mode": "document|pages|paragraphs"  # Einlese-Modus (neu)
# }
jobs = {}

def _new_event_loop():
    """Isolierten Event Loop für Hintergrund-Thread erzeugen (falls Worker.run async ist)."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop

# ---------- UI-Sprache aus Request extrahieren ----------
def get_lang_from_request(req) -> str:
    """
    UI-Sprache ermitteln. Reihenfolge:
    1) Header 'X-Language'
    2) FormData-Feld 'language'
    3) Query-Parameter 'lang'
    4) Default 'de'
    Ergebnis ist strikt 'de' oder 'en'.
    """
    lang = (req.headers.get("X-Language")
            or req.form.get("language")
            or req.args.get("lang")
            or "de").lower().strip()
    return "de" if lang == "de" else "en"

# ---------- Übersetzungs-Sprachen (Source/Target) extrahieren ----------
SUPPORTED = {"de", "en"}

def _norm_lang(x: str | None, default: str) -> str:
    x = (x or default).lower().strip()
    return x if x in SUPPORTED else default

def get_from_to_langs(req) -> tuple[str, str]:
    """
    Liefert ('from_lang','to_lang') jeweils 'de' oder 'en'.
    Reihenfolge:
    1) Header: X-From-Lang / X-To-Lang
    2) FormData-Felder: from_lang / to_lang
    3) Query-Parameter: from / to
    4) Defaults: from='en', to='de'
    """
    from_lang = (req.headers.get("X-From-Lang")
                 or req.form.get("from_lang")
                 or req.args.get("from")
                 or "en")
    to_lang   = (req.headers.get("X-To-Lang")
                 or req.form.get("to_lang")
                 or req.args.get("to")
                 or "de")
    return _norm_lang(from_lang, "en"), _norm_lang(to_lang, "de")

# ---------- Einlese-Modus extrahieren (neu) ----------
READ_MODES = {"document", "pages", "paragraphs"}

def get_read_mode_from_request(req) -> str:
    """
    Liest den Einlese-Modus. Erlaubte Werte:
    - 'document'   (Ganzes Dokument)
    - 'pages'      (Seitenweise)
    - 'paragraphs' (Absatzweise)
    Reihenfolge:
    1) Header 'X-Read-Mode'
    2) FormData-Feld 'read_mode'
    3) Query-Parameter 'mode'
    4) Default 'document'
    """
    mode = (req.headers.get("X-Read-Mode")
            or req.form.get("read_mode")
            or req.args.get("mode")
            or "document").lower().strip()
    return mode if mode in READ_MODES else "document"

# ---------- Hilfsfunktionen (Ergebnis-Normalisierung) ----------
def _ensure_abs(path: str) -> str:
    """
    Liefert einen absoluten Pfad zur erzeugten Datei.
    Akzeptiert sowohl absolute Pfade als auch Dateinamen im OUTPUT_FOLDER.
    """
    if not path:
        return ""
    p = os.path.abspath(path)
    if os.path.exists(p):
        return p
    # ggf. nur Dateiname -> im OUTPUT_FOLDER prüfen
    candidate = os.path.abspath(os.path.join(OUTPUT_FOLDER, os.path.basename(path)))
    return candidate if os.path.exists(candidate) else ""

def _normalize_audio_outputs(result) -> list[str]:
    """
    Akzeptiert verschiedene Rückgabeformen vom Worker und liefert eine Liste
    existierender Audio-Pfade (absolut).
      - dict mit key 'audio' (str)
      - dict mit key 'audios' / 'audio_files' / 'downloads' (list[str])
      - list[str]
    """
    paths: list[str] = []
    if isinstance(result, dict):
        # einzelne Datei
        if isinstance(result.get("audio"), str):
            paths = [result["audio"]]
        # mehrere Dateien – gängige Varianten
        elif isinstance(result.get("audios"), list):
            paths = result["audios"]
        elif isinstance(result.get("audio_files"), list):
            paths = result["audio_files"]
        elif isinstance(result.get("downloads"), list):
            paths = result["downloads"]
        # Fallback: keys durchsuchen
        else:
            for k in ("files", "outputs"):
                v = result.get(k)
                if isinstance(v, list):
                    paths = v
                    break
    elif isinstance(result, list):
        paths = result

    # Absolut und existent filtern
    final = []
    for p in paths:
        ap = _ensure_abs(str(p))
        if ap and os.path.exists(ap):
            final.append(ap)
    return final

# ---------- Hintergrund-Job ----------
def process_job(
    job_id: str,
    input_path: str,
    desired_name: str,
    ref_audio: str | None,
    output_folder: str,
    ui_language: str,
    from_lang: str,
    to_lang: str,
    read_mode: str,           # neu
):
    """Hintergrund-Verarbeitung: ruft FeatureWorker.run auf und aktualisiert den Job-Status."""
    jobs[job_id]["status"] = "running"
    try:
        worker = FeatureWorker(tts_output_dir=output_folder, from_lang=from_lang, to_lang=to_lang)

        # Async run() synchron ausführen
        loop = _new_event_loop()
        try:
            # read_mode an Worker geben (rückwärtskompatibel mit Fallback)
            try:
                result = loop.run_until_complete(worker.run(
                    input_file=input_path,
                    ref_audio=ref_audio,
                    filename=desired_name,
                    read_mode=read_mode,          # <--- neu
                ))
            except TypeError:
                # Falls die aktuelle Worker-Signatur read_mode noch nicht kennt
                result = loop.run_until_complete(worker.run(
                    input_file=input_path,
                    ref_audio=ref_audio,
                    filename=desired_name
                ))
        finally:
            loop.close()

        # Ergebnis normalisieren
        audio_files = _normalize_audio_outputs(result)
        if not audio_files:
            # Fallback: bisheriger Rückgabewert 'audio'
            audio_path = result.get("audio") if isinstance(result, dict) else None
            if audio_path:
                ap = _ensure_abs(audio_path)
                if ap:
                    audio_files = [ap]

        if not audio_files:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = "Audioausgabe wurde nicht erzeugt"
            return

        # Download-Routen vorbereiten
        rel_links = [f"/download/{os.path.basename(p)}" for p in audio_files]
        jobs[job_id]["status"] = "done"
        # Abwärtskompatibilität: erster Link weiterhin unter 'download'
        jobs[job_id]["download"] = rel_links[0]
        # Neu: vollständige Liste
        jobs[job_id]["downloads"] = rel_links

    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = f"{e}"

# ---------- Routes ----------
@app.route('/upload', methods=['POST'])
def upload_file():
    up_file = request.files.get('file')
    if not up_file or up_file.filename == '':
        return jsonify({"error": "Keine Datei übermittelt"}), 400

    # UI-Sprache (für Servermeldungen/Defaults)
    ui_language = get_lang_from_request(request)  # 'de' / 'en'

    # Source/Target lesen (für Übersetzung in der Pipeline)
    from_lang, to_lang = get_from_to_langs(request)  # ('en','de') etc.

    # Einlese-Modus (neu)
    read_mode = get_read_mode_from_request(request)  # 'document'|'pages'|'paragraphs'

    safe_name = secure_filename(up_file.filename)

    # Eindeutige Namen, damit parallele Uploads sich nicht überschreiben
    uid = uuid.uuid4().hex[:8]
    input_filename = f"{uid}_{safe_name}"
    input_path = os.path.join(UPLOAD_FOLDER, input_filename)
    up_file.save(input_path)

    base_name, _ = os.path.splitext(safe_name)
    desired_name = f"{base_name}_{uid}"

    # Job registrieren (inkl. UI-, Übersetzungs-Sprachen & Einlese-Modus)
    job_id = uuid.uuid4().hex
    jobs[job_id] = {
        "status": "queued",
        "download": None,
        "downloads": None,
        "error": None,
        "started": time(),
        "progress": 0,
        "language": ui_language,   # UI-Sprache (de/en)
        "from_lang": from_lang,    # Übersetzungs-Quelle (de/en)
        "to_lang": to_lang,        # Übersetzungs-Ziel (de/en)
        "read_mode": read_mode,    # Einlese-Modus (document/pages/paragraphs)
    }

    t = threading.Thread(
        target=process_job,
        args=(job_id, input_path, desired_name, REF_AUDIO_PATH, OUTPUT_FOLDER,
              ui_language, from_lang, to_lang, read_mode),  # <- read_mode mitgeben
        daemon=True
    )
    t.start()

    payload = {"status": "accepted", "job_id": job_id}
    resp = make_response(json.dumps(payload), 202)
    resp.headers["Content-Type"] = "application/json; charset=utf-8"
    resp.headers["Cache-Control"] = "no-store"
    return resp

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/status/<job_id>', methods=['GET'])
def status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Unbekannte job_id"}), 404
    return jsonify(job)

@app.route('/download/<path:filename>')
def download_file(filename):
    path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(path):
        return jsonify({"error": "Datei nicht gefunden"}), 404
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    # Wichtig: use_reloader=False, sonst doppelte Threads im Debug-Modus
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
