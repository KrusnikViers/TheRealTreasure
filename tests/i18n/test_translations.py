from app.core.info import APP_DIR
from app.i18n import translations
from tests.base import BaseTestCase


class TestTranslations(BaseTestCase):
    @staticmethod
    def get_release_translations():
        return translations.Translations(APP_DIR.joinpath('i18n'), APP_DIR)

    def test_locale_cut(self):
        self.assertEqual('ru', translations.Translations.normalise_locale('Ru-Ru'))

    def test_locale_original(self):
        self.assertEqual('xx', translations.Translations.normalise_locale('xx'))

    def test_get_no_language_code(self):
        instance = self.get_release_translations()
        self.assertEqual(instance.translations[translations.DEFAULT_LANGUAGE], instance.get(None))

    def test_get_fallback(self):
        instance = self.get_release_translations()
        self.assertEqual(instance.translations[translations.DEFAULT_LANGUAGE], instance.get('xx'))

    def test_get_correct_code(self):
        instance = self.get_release_translations()
        self.assertTrue('ru' in translations.SUPPORTED_LANGUAGES)
        self.assertNotEqual(translations.DEFAULT_LANGUAGE, 'ru')
        self.assertEqual(instance.translations['ru'], instance.get('ru'))
