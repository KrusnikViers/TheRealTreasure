import gettext
import logging
import pathlib

from app.i18n.updater import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, TranslationsUpdater


class Translations:
    def __init__(self, locale_dir: pathlib.Path, sources_dir: pathlib.Path):
        self.translations = {}
        updater = TranslationsUpdater(locale_dir, sources_dir)
        if not updater.is_translations_generated():
            logging.info('Precompiled translations not found, regenerating...')
            updater.regenerate_all()
        for language in SUPPORTED_LANGUAGES:
            self.translations[language] = gettext.translation('zordon',
                                                              localedir=str(locale_dir),
                                                              languages=[language])

    @staticmethod
    def normalise_locale(global_locale: str):
        return global_locale.split('-')[0].lower() if global_locale else global_locale

    def get(self, locale: str):
        locale = self.normalise_locale(locale)
        if locale in SUPPORTED_LANGUAGES:
            return self.translations[locale]
        return self.translations[DEFAULT_LANGUAGE]
