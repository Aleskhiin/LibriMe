import { useI18n, type UiLanguage } from '../i18n';

const OPTIONS: Array<{ language: UiLanguage; flag: string; labelKey: string }> = [
  { language: 'de', flag: '🇩🇪', labelKey: 'languageGerman' },
  { language: 'en', flag: '🇺🇸', labelKey: 'languageEnglish' },
];

export default function LanguageToggle() {
  const { language, setLanguage, t } = useI18n();

  return (
    <div className="flex items-center gap-1 rounded-full border border-orange-200 bg-white/70 p-1 shadow-sm" aria-label={t('languageSwitchLabel')}>
      {OPTIONS.map(option => {
        const isActive = option.language === language;

        return (
          <button
            key={option.language}
            type="button"
            onClick={() => setLanguage(option.language)}
            title={t(option.labelKey)}
            aria-label={t(option.labelKey)}
            aria-pressed={isActive}
            className={`flex h-9 w-9 items-center justify-center rounded-full text-lg transition-colors ${
              isActive
                ? 'bg-orange-600 shadow-sm'
                : 'hover:bg-orange-100'
            }`}
          >
            <span aria-hidden="true">{option.flag}</span>
          </button>
        );
      })}
    </div>
  );
}
