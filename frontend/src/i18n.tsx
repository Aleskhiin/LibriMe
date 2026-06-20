import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';

export type UiLanguage = 'de' | 'en';

type Translations = Record<string, string>;

const TRANSLATIONS: Record<UiLanguage, Translations> = {
  de: {
    appNewAudiobookTitle: 'Neues Hörbuch erstellen',
    appNewAudiobookSubtitle: 'Lade eine Datei hoch und wähle deine Einstellungen.',
    appSupportedFormats: 'Unterstützte Formate',
    appMyJobs: 'Meine Jobs',
    appJobsLoading: 'Aufträge werden geladen.',
    appNoJobsStarted: 'Noch keine Aufträge gestartet.',
    appOneJobTotal: '1 Auftrag insgesamt',
    appManyJobsTotal: '{count} Aufträge insgesamt',
    appRefresh: 'Aktualisieren',
    footerImprint: 'Impressum',
    appFooter: 'LibriMe - Datei zu Hörbuch - Powered by OCR & TTS',
    appListError: 'Jobliste konnte nicht geladen werden.',
    appUploadUnknownError: 'Unbekannter Fehler beim Upload.',
    appJobsLoadingBlock: 'Jobs werden geladen. Bitte warte kurz.',
    appActiveJobBlock: 'Bitte warte, bis der aktuell verarbeitete Job abgeschlossen ist.',

    landingTitle: 'Verwandle Dateien in Hörbücher',
    landingSubtitle: 'Lade dein Dokument hoch und LibriMe erstellt dir automatisch eine hochwertige Audio-Version.',
    landingCta: 'Zur App',
    landingUploadTitle: 'Dokumente hochladen',
    landingUploadText: 'Einfach per Drag & Drop oder Dateiauswahl, bis 50 MB.',
    landingTtsTitle: 'Automatische Vertonung',
    landingTtsText: 'Text-Extraktion und Sprachsynthese laufen vollautomatisch im Hintergrund.',
    landingReadyTitle: 'Fertig zum Anhören',
    landingReadyText: 'Fortschritt live verfolgen und das fertige Hörbuch direkt herunterladen.',
    landingFooter: 'LibriMe - Datei zu Hörbuch.',
    imprintBackHome: 'Zur Startseite',
    imprintBackApp: 'Zur App',
    imprintTitle: 'Impressum',
    imprintSubtitle: 'Informationen zum Open-Source-Projekt LibriMe.',
    imprintProviderTitle: 'Diensteanbieter',
    imprintProjectName: 'Projekt',
    imprintContactTitle: 'Kontakt',
    imprintEmail: 'E-Mail',
    imprintEmailValue: 'Noch zu ergänzen',
    imprintResponsibleTitle: 'Inhaltlich verantwortlich',
    imprintResponsibleValue: 'LibriMe Team',
    imprintDevelopersTitle: 'Entwicklung',
    imprintRole: 'Rolle',
    imprintOpenSourceTitle: 'Open Source',
    imprintOpenSourceText: 'LibriMe ist ein Open-Source-Projekt und wird unter der MIT-Lizenz veröffentlicht.',
    imprintLicense: 'Lizenz',
    imprintRepository: 'GitHub Repository',

    languageSwitchLabel: 'Website-Sprache wählen',
    languageGerman: 'Deutsch',
    languageEnglish: 'Englisch',

    uploadUnsupportedFile: 'Dieses Dateiformat wird nicht unterstützt.',
    uploadTooLarge: 'Die Datei darf maximal 50 MB groß sein.',
    uploadChooseFile: 'Bitte wähle eine Datei aus.',
    uploadDropFile: 'Datei hier ablegen oder klicken zum Auswählen',
    uploadRemoveFile: 'Datei entfernen',
    uploadSourceLanguage: 'Ausgangssprache',
    uploadTargetLanguage: 'Zielsprache',
    uploadVoice: 'Stimme',
    uploadSplitting: 'Ausgabe-Aufteilung',
    uploadInProgress: 'Wird hochgeladen...',
    uploadStart: 'Vertonung starten',

    optionEnglishUs: 'English (US)',
    optionGerman: 'Deutsch',
    optionFrench: 'Französisch',
    optionSpanish: 'Spanisch',
    optionMale: 'Männlich (v1)',
    optionFemale: 'Weiblich (v1)',
    optionWholeDocument: 'Ganzes Dokument',
    optionPage: 'Seitenweise',
    optionParagraph: 'Absatzweise',

    jobNoJobs: 'Noch keine Jobs',
    jobNoJobsText: 'Lade eine Datei hoch, um dein erstes Hörbuch zu erstellen.',
    jobActiveSection: 'In Bearbeitung ({count})',
    jobCompletedSection: 'Abgeschlossen ({count})',
    jobFailedSection: 'Fehlgeschlagen ({count})',
    jobQueued: 'Warteschlange',
    jobRunning: 'Wird verarbeitet',
    jobCompleted: 'Abgeschlossen',
    jobFailed: 'Fehlgeschlagen',
    jobJustNow: 'Gerade eben',
    jobWaiting: 'Warte auf Verarbeitung...',
    jobProcessing: 'Wird verarbeitet...',
    jobAudioUnsupported: 'Dein Browser unterstützt kein Audio-Element.',
    jobDownloadFailed: 'Download fehlgeschlagen.',
    jobDownloading: 'Wird geladen...',
    jobDownload: 'Herunterladen',
    jobRetry: 'Erneut versuchen',
  },
  en: {
    appNewAudiobookTitle: 'Create new audiobook',
    appNewAudiobookSubtitle: 'Upload a file and choose your settings.',
    appSupportedFormats: 'Supported formats',
    appMyJobs: 'My jobs',
    appJobsLoading: 'Loading jobs.',
    appNoJobsStarted: 'No jobs started yet.',
    appOneJobTotal: '1 job total',
    appManyJobsTotal: '{count} jobs total',
    appRefresh: 'Refresh',
    footerImprint: 'Legal notice',
    appFooter: 'LibriMe - file to audiobook - Powered by OCR & TTS',
    appListError: 'Could not load job list.',
    appUploadUnknownError: 'Unknown upload error.',
    appJobsLoadingBlock: 'Jobs are loading. Please wait a moment.',
    appActiveJobBlock: 'Please wait until the job currently being processed is finished.',

    landingTitle: 'Turn files into audiobooks',
    landingSubtitle: 'Upload your document and LibriMe automatically creates a high-quality audio version.',
    landingCta: 'Open app',
    landingUploadTitle: 'Upload documents',
    landingUploadText: 'Use drag & drop or file selection, up to 50 MB.',
    landingTtsTitle: 'Automatic narration',
    landingTtsText: 'Text extraction and speech synthesis run automatically in the background.',
    landingReadyTitle: 'Ready to listen',
    landingReadyText: 'Track progress live and download the finished audiobook directly.',
    landingFooter: 'LibriMe - file to audiobook.',
    imprintBackHome: 'Back to home',
    imprintBackApp: 'Open app',
    imprintTitle: 'Legal notice',
    imprintSubtitle: 'Information about the LibriMe open-source project.',
    imprintProviderTitle: 'Service provider',
    imprintProjectName: 'Project',
    imprintContactTitle: 'Contact',
    imprintEmail: 'Email',
    imprintEmailValue: 'To be added',
    imprintResponsibleTitle: 'Responsible for content',
    imprintResponsibleValue: 'LibriMe team',
    imprintDevelopersTitle: 'Development',
    imprintRole: 'Role',
    imprintOpenSourceTitle: 'Open source',
    imprintOpenSourceText: 'LibriMe is an open-source project released under the MIT License.',
    imprintLicense: 'License',
    imprintRepository: 'GitHub repository',

    languageSwitchLabel: 'Choose website language',
    languageGerman: 'German',
    languageEnglish: 'English',

    uploadUnsupportedFile: 'This file format is not supported.',
    uploadTooLarge: 'The file must be 50 MB or smaller.',
    uploadChooseFile: 'Please choose a file.',
    uploadDropFile: 'Drop file here or click to select',
    uploadRemoveFile: 'Remove file',
    uploadSourceLanguage: 'Source language',
    uploadTargetLanguage: 'Target language',
    uploadVoice: 'Voice',
    uploadSplitting: 'Output splitting',
    uploadInProgress: 'Uploading...',
    uploadStart: 'Start narration',

    optionEnglishUs: 'English (US)',
    optionGerman: 'German',
    optionFrench: 'French',
    optionSpanish: 'Spanish',
    optionMale: 'Male (v1)',
    optionFemale: 'Female (v1)',
    optionWholeDocument: 'Whole document',
    optionPage: 'By page',
    optionParagraph: 'By paragraph',

    jobNoJobs: 'No jobs yet',
    jobNoJobsText: 'Upload a file to create your first audiobook.',
    jobActiveSection: 'In progress ({count})',
    jobCompletedSection: 'Completed ({count})',
    jobFailedSection: 'Failed ({count})',
    jobQueued: 'Queued',
    jobRunning: 'Processing',
    jobCompleted: 'Completed',
    jobFailed: 'Failed',
    jobJustNow: 'Just now',
    jobWaiting: 'Waiting for processing...',
    jobProcessing: 'Processing...',
    jobAudioUnsupported: 'Your browser does not support the audio element.',
    jobDownloadFailed: 'Download failed.',
    jobDownloading: 'Downloading...',
    jobDownload: 'Download',
    jobRetry: 'Try again',
  },
};

interface I18nContextValue {
  language: UiLanguage;
  setLanguage: (language: UiLanguage) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
}

const I18nContext = createContext<I18nContextValue | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<UiLanguage>(() => {
    const storedLanguage = localStorage.getItem('librime-ui-language');
    return storedLanguage === 'en' || storedLanguage === 'de' ? storedLanguage : 'de';
  });

  useEffect(() => {
    localStorage.setItem('librime-ui-language', language);
    document.documentElement.lang = language;
  }, [language]);

  const value = useMemo<I18nContextValue>(() => ({
    language,
    setLanguage: setLanguageState,
    t: (key, params) => {
      const template = TRANSLATIONS[language][key] ?? TRANSLATIONS.de[key] ?? key;
      if (!params) {
        return template;
      }

      return Object.entries(params).reduce(
        (text, [paramKey, paramValue]) => text.replaceAll(`{${paramKey}}`, String(paramValue)),
        template,
      );
    },
  }), [language]);

  return (
    <I18nContext.Provider value={value}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within LanguageProvider');
  }
  return context;
}
