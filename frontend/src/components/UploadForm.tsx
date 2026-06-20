import { useRef, useState, useCallback } from 'react';

interface UploadFormProps {
  onSubmit: (params: {
    file: File;
    fileLanguage: string;
    translationLanguage: string;
    voiceID: string;
    splittingID: string;
  }) => void;
  isLoading: boolean;
}

const LANGUAGE_OPTIONS = [
  { value: 'en_US', label: 'English (US)' },
  { value: 'de_DE', label: 'Deutsch' },
  { value: 'fr_FR', label: 'Français' },
  { value: 'es_ES', label: 'Español' },
];

const VOICE_OPTIONS = [
  { value: 'male_v1', label: 'Männlich (v1)' },
];

const SPLITTING_OPTIONS = [
  { value: 'DOCUMENT', label: 'Ganzes Dokument' },
  { value: 'PAGE', label: 'Seitenweise' },
  { value: 'PARAGRAPH', label: 'Absatzweise' },
];

export default function UploadForm({ onSubmit, isLoading }: UploadFormProps) {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileLanguage, setFileLanguage] = useState('en_US');
  const [translationLanguage, setTranslationLanguage] = useState('de_DE');
  const [voiceID, setVoiceID] = useState('male_v1');
  const [splittingID, setSplittingID] = useState('DOCUMENT');
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const ACCEPTED_TYPES = ['application/pdf'];

  const validateFile = (file: File): boolean => {
    if (!ACCEPTED_TYPES.includes(file.type)) {
      setError('Nur PDF-Dateien sind erlaubt.');
      return false;
    }
    if (file.size > 50 * 1024 * 1024) {
      setError('Die Datei darf maximal 50 MB groß sein.');
      return false;
    }
    setError(null);
    return true;
  };

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && validateFile(file)) {
      setSelectedFile(file);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setDragOver(false);
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && validateFile(file)) {
      setSelectedFile(file);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Bitte wähle eine PDF-Datei aus.');
      return;
    }
    onSubmit({ file: selectedFile, fileLanguage, translationLanguage, voiceID, splittingID });
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Drag & Drop Zone */}
      <div
        onClick={() => fileInputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`
          relative cursor-pointer rounded-2xl border-2 border-dashed p-10 text-center transition-all duration-200
          ${dragOver
            ? 'border-indigo-500 bg-indigo-50 scale-[1.01]'
            : selectedFile
              ? 'border-green-400 bg-green-50'
              : 'border-gray-300 bg-gray-50 hover:border-indigo-400 hover:bg-indigo-50'
          }
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={handleFileChange}
        />

        {selectedFile ? (
          <div className="flex flex-col items-center gap-3">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-green-100">
              <svg className="h-7 w-7 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div>
              <p className="font-semibold text-gray-800">{selectedFile.name}</p>
              <p className="text-sm text-gray-500">{formatFileSize(selectedFile.size)}</p>
            </div>
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); setSelectedFile(null); if (fileInputRef.current) fileInputRef.current.value = ''; }}
              className="text-xs text-red-500 underline hover:text-red-700"
            >
              Datei entfernen
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div className={`flex h-14 w-14 items-center justify-center rounded-full transition-colors ${dragOver ? 'bg-indigo-100' : 'bg-gray-100'}`}>
              <svg className={`h-7 w-7 transition-colors ${dragOver ? 'text-indigo-600' : 'text-gray-400'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <p className="font-semibold text-gray-700">PDF-Datei hier ablegen</p>
              <p className="text-sm text-gray-500">oder klicken zum Auswählen</p>
            </div>
            <p className="text-xs text-gray-400">PDF-Dateien bis 50 MB</p>
          </div>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
          <svg className="h-4 w-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          {error}
        </div>
      )}

      {/* Einstellungen */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700">
            Ausgangssprache
          </label>
          <select
            value={fileLanguage}
            onChange={(e) => setFileLanguage(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          >
            {LANGUAGE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700">
            Zielsprache (Stimme)
          </label>
          <select
            value={translationLanguage}
            onChange={(e) => setTranslationLanguage(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          >
            {LANGUAGE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700">
            Stimme
          </label>
          <select
            value={voiceID}
            onChange={(e) => setVoiceID(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          >
            {VOICE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700">
            Ausgabe-Aufteilung
          </label>
          <select
            value={splittingID}
            onChange={(e) => setSplittingID(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          >
            {SPLITTING_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading || !selectedFile}
        className="
          w-full rounded-xl bg-indigo-600 px-6 py-3.5 text-base font-semibold text-white shadow-md
          transition-all duration-200
          hover:bg-indigo-700 hover:shadow-lg
          active:scale-[0.98]
          disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none
          flex items-center justify-center gap-2
        "
      >
        {isLoading ? (
          <>
            <svg className="h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Wird hochgeladen…
          </>
        ) : (
          <>
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
            Vertonung starten
          </>
        )}
      </button>
    </form>
  );
}
