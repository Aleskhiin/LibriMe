import argostranslate.package
import argostranslate.translate
from .BaseFeature import BaseFeature
from app_pkg.Logger.Logging_setup import logger

class TranslatorFeature(BaseFeature):

    def __init__(self):
        self.from_lang = 'en'
        self.to_lang = 'de'
        self.text = 'Übersetzungstest'

    def install_language_package(self, from_code='en', to_code='de'):
        logger.info("Start it install language package for translator.")
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        package_to_install = next(
            filter(lambda x: x.from_code == from_code and x.to_code == to_code, available_packages),
            None
        )
        if package_to_install:
            package_path = package_to_install.download()
            argostranslate.package.install_from_path(package_path)
            logger.info(f"Language installed: {from_code} → {to_code}")
        else:
            logger.warning(f"No language could be found for {from_code} → {to_code}")

    def translate_text(self, text, from_lang='en', to_lang='de'):
        logger.info(f"Start the translation of the text from '{from_lang}' to '{to_lang}'")
        installed_languages = argostranslate.translate.get_installed_languages()
        from_lang_obj = next((lang for lang in installed_languages if lang.code == from_lang), None)
        to_lang_obj = next((lang for lang in installed_languages if lang.code == to_lang), None)

        if from_lang_obj and to_lang_obj:
            logger.info(f"Translate the following text:\n{text}")
            translation = from_lang_obj.get_translation(to_lang_obj)
            return translation.translate(text)
        else:
            logger.warning("Übersetzung nicht verfügbar. Sprachpaket fehlt.")
            return "Übersetzung nicht verfügbar. Sprachpaket fehlt."
    
    def configure(self, from_lang='en', to_lang='de', text='Übersetzungstest'):
        logger.info("Configure TranslatorFeature.")

        self.text = text
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.install_language_package(from_lang, to_lang)

    def process(self) -> str:
        logger.info("Start translation feature.")
        tranlated_text = self.translate_text(
            text=self.text,
            from_lang=self.from_lang,
            to_lang=self.to_lang
        )
        logger.info("Finish the translation feature and return the translated text.")
        return tranlated_text         



def main():
    translator = TranslatorFeature()
    translator.configure(from_lang='en', to_lang='de', text='It is only a test.')

    print("Übersetzung:", translator.process())


if __name__ == "__main__":
    main()