import { useCallback, useRef, useState } from 'react';
import { useI18n } from '../i18n';

interface UploadFormProps {
  onSubmit: (params: {
    file: File;
    fileLanguage: string;
    translationLanguage: string;
    voiceID: string;
    splittingID: string;
  }) => void;
  isLoading: boolean;
  submitDisabledReason?: string;
}

const LANGUAGE_OPTIONS = [
  { value: 'en_US', labelKey: 'optionEnglishUs' },
  { value: 'de_DE', labelKey: 'optionGerman' },
  { value: 'fr_FR', labelKey: 'optionFrench' },
];

const VOICE_OPTIONS = [
  { value: 'male_v1', labelKey: 'optionMale' },
  { value: 'female_v1', labelKey: 'optionFemale' },
];

const ENGLISH_US_VOICE_ID = 'female_v1';

const ACCEPTED_FILE_EXTENSIONS = [
  '.png',
  '.jpg',
  '.jpeg',
  '.bmp',
  '.tif',
  '.tiff',
  '.webp',
  '.pdf',
  '.txt',
  '.md',
  '.markdown',
  '.doc',
  '.docx',
  '.odt',
  '.ppt',
  '.pptx',
  '.html',
  '.htm',
  '.csv',
  '.json',
];

const ACCEPTED_FILE_TYPES = ACCEPTED_FILE_EXTENSIONS.join(',');

const SPLITTING_OPTIONS = [
  { value: 'DOCUMENT', labelKey: 'optionWholeDocument' },
  { value: 'PAGE', labelKey: 'optionPage' },
  { value: 'PARAGRAPH', labelKey: 'optionParagraph' },
];

export default function UploadForm({ onSubmit, isLoading, submitDisabledReason }: UploadFormProps) {
  const { t } = useI18n();
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileLanguage, setFileLanguage] = useState('en_US');
  const [translationLanguage, setTranslationLanguage] = useState('en_US');
  const [voiceID, setVoiceID] = useState(ENGLISH_US_VOICE_ID);
  const [splittingID, setSplittingID] = useState('DOCUMENT');
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = useCallback((file: File): boolean => {
    const fileName = file.name.toLowerCase();
    const hasAcceptedExtension = ACCEPTED_FILE_EXTENSIONS.some(extension => fileName.endsWith(extension));

    if (!hasAcceptedExtension) {
      setError(t('uploadUnsupportedFile'));
      return false;
    }

    if (file.size > 50 * 1024 * 1024) {
      setError(t('uploadTooLarge'));
      return false;
    }

    setError(null);
    return true;
  }, [t]);

  const handleDrop = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDragOver(false);

    const file = event.dataTransfer.files[0];
    if (file && validateFile(file)) {
      setSelectedFile(file);
    }
  }, [validateFile]);

  const handleDragOver = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setDragOver(false);
  }, []);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && validateFile(file)) {
      setSelectedFile(file);
    }
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();

    if (submitDisabledReason) {
      setError(submitDisabledReason);
      return;
    }

    if (!selectedFile) {
      setError(t('uploadChooseFile'));
      return;
    }

    onSubmit({
      file: selectedFile,
      fileLanguage,
      translationLanguage,
      voiceID: translationLanguage === 'en_US' ? ENGLISH_US_VOICE_ID : voiceID,
      splittingID,
    });
  };

  const handleTranslationLanguageChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const nextTranslationLanguage = event.target.value;
    setTranslationLanguage(nextTranslationLanguage);

    if (nextTranslationLanguage === 'en_US') {
      setVoiceID(ENGLISH_US_VOICE_ID);
    }
  };

  const clearSelectedFile = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div
        onClick={() => fileInputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`
          relative cursor-pointer rounded-2xl border-2 border-dashed p-10 text-center transition-all duration-200
          ${dragOver
            ? 'scale-[1.01] border-orange-500 bg-orange-100'
            : selectedFile
              ? 'border-green-400 bg-green-50'
              : 'border-orange-200 bg-white/80 hover:border-orange-400 hover:bg-orange-50'
          }
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED_FILE_TYPES}
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
              onClick={clearSelectedFile}
              className="text-xs text-red-500 underline hover:text-red-700"
            >
              {t('uploadRemoveFile')}
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div className={`flex h-14 w-14 items-center justify-center rounded-full transition-colors ${dragOver ? 'bg-orange-200' : 'bg-orange-100'}`}>
              <svg className={`h-7 w-7 transition-colors ${dragOver ? 'text-orange-700' : 'text-orange-500'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <p className="font-semibold text-stone-800">{t('uploadDropFile')}</p>
            </div>
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

      {submitDisabledReason && (
        <div className="flex items-center gap-2 rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">
          <svg className="h-4 w-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2 2a1 1 0 001.414-1.414L11 9.586V6z" clipRule="evenodd" />
          </svg>
          {submitDisabledReason}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700">
            {t('uploadSourceLanguage')}
          </label>
          <select
            value={fileLanguage}
            onChange={(event) => setFileLanguage(event.target.value)}
            className="w-full rounded-lg border border-orange-200 bg-white px-3 py-2.5 text-sm shadow-sm focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-200"
          >
            {LANGUAGE_OPTIONS.map(option => (
              <option key={option.value} value={option.value}>{t(option.labelKey)}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700">
            {t('uploadTargetLanguage')}
          </label>
          <select
            value={translationLanguage}
            onChange={handleTranslationLanguageChange}
            className="w-full rounded-lg border border-orange-200 bg-white px-3 py-2.5 text-sm shadow-sm focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-200"
          >
            {LANGUAGE_OPTIONS.map(option => (
              <option key={option.value} value={option.value}>{t(option.labelKey)}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700">
            {t('uploadVoice')}
          </label>
          <select
            value={voiceID}
            onChange={(event) => setVoiceID(event.target.value)}
            disabled={translationLanguage === 'en_US'}
            className="w-full rounded-lg border border-orange-200 bg-white px-3 py-2.5 text-sm shadow-sm focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-200 disabled:cursor-not-allowed disabled:bg-orange-50 disabled:text-stone-500"
          >
            {(translationLanguage === 'en_US'
              ? VOICE_OPTIONS.filter(option => option.value === ENGLISH_US_VOICE_ID)
              : VOICE_OPTIONS
            ).map(option => (
              <option key={option.value} value={option.value}>{t(option.labelKey)}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700">
            {t('uploadSplitting')}
          </label>
          <select
            value={splittingID}
            onChange={(event) => setSplittingID(event.target.value)}
            className="w-full rounded-lg border border-orange-200 bg-white px-3 py-2.5 text-sm shadow-sm focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-200"
          >
            {SPLITTING_OPTIONS.map(option => (
              <option key={option.value} value={option.value}>{t(option.labelKey)}</option>
            ))}
          </select>
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading || !selectedFile || Boolean(submitDisabledReason)}
        className="
          flex w-full items-center justify-center gap-2 rounded-xl bg-orange-600 px-6 py-3.5 text-base font-semibold text-white shadow-md shadow-orange-900/10
          transition-all duration-200 hover:bg-orange-700 hover:shadow-lg active:scale-[0.98]
          disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none
        "
      >
        {isLoading ? (
          <>
            <svg className="h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            {t('uploadInProgress')}
          </>
        ) : (
          <>
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
            {t('uploadStart')}
          </>
        )}
      </button>
    </form>
  );
}
