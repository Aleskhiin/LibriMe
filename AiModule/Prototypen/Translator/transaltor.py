import argostranslate.package
import argostranslate.translate

def install_language_package(from_code='en', to_code='de'):
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        filter(lambda x: x.from_code == from_code and x.to_code == to_code, available_packages),
        None
    )
    if package_to_install:
        package_path = package_to_install.download()
        argostranslate.package.install_from_path(package_path)
        print(f"Sprachpaket installiert: {from_code} → {to_code}")
    else:
        print(f"Kein Sprachpaket gefunden für {from_code} → {to_code}")

def translate_text(text, from_lang='en', to_lang='de'):
    installed_languages = argostranslate.translate.get_installed_languages()
    from_lang_obj = next((lang for lang in installed_languages if lang.code == from_lang), None)
    to_lang_obj = next((lang for lang in installed_languages if lang.code == to_lang), None)

    if from_lang_obj and to_lang_obj:
        translation = from_lang_obj.get_translation(to_lang_obj)
        return translation.translate(text)
    else:
        return "[Übersetzung nicht verfügbar. Sprachpaket fehlt.]"
    

if __name__ == "__main__":
    install_language_package('en', 'de')  # Nur beim ersten Start nötig

    while True:
        text = input("Text eingeben (Englisch → Deutsch, 'exit' zum Beenden): ")
        if text.lower() == "exit":
            break
        print("Übersetzung:", translate_text(text, 'en', 'de'))