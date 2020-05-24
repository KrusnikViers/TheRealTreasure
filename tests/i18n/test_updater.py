import os
import shutil
from collections import Counter
from pathlib import Path

from app.core.info import APP_DIR
from app.i18n import updater
from tests.base import BaseTestCase


class TestStringsUpdater(BaseTestCase):
    test_dir = Path(os.path.realpath(__file__)).parent.joinpath('data')

    def test_default_language(self):
        self.assertIsNotNone(updater.DEFAULT_LANGUAGE)
        self.assertTrue(updater.DEFAULT_LANGUAGE in updater.SUPPORTED_LANGUAGES)

    def test_all_release_strings_are_valid(self):
        instance = updater.TranslationsUpdater(APP_DIR.joinpath('i18n'), APP_DIR)
        self.assertTrue(instance.regenerate_all())
        self.assertTrue(instance.is_translations_generated())

    def test_empty_translations(self):
        locale_dir = self.test_dir.joinpath('locale_empty')
        locale_dir.mkdir(parents=True)
        self.assertFalse(os.listdir(locale_dir))

        instance = updater.TranslationsUpdater(locale_dir, self.test_dir.joinpath('source'))
        self.assertFalse(instance.is_translations_generated())
        self.assertFalse(instance.regenerate_all())
        self.assertEqual(Counter(updater.SUPPORTED_LANGUAGES), Counter(os.listdir(locale_dir)))

        shutil.rmtree(locale_dir)

    def test_translations_obsolete(self):
        locale_dir = self.test_dir.joinpath('locale_obsolete')
        self.assertEqual(os.listdir(locale_dir), ['zordon.po'])
        for language in updater.SUPPORTED_LANGUAGES:
            locale_dir.joinpath(language).mkdir(parents=True)
            shutil.copyfile(locale_dir.joinpath('zordon.po'), locale_dir.joinpath(language, 'zordon.po'))

        instance = updater.TranslationsUpdater(locale_dir, self.test_dir.joinpath('source'))
        self.assertFalse(instance.is_translations_generated())
        self.assertTrue(instance.regenerate_all())

        for language in updater.SUPPORTED_LANGUAGES:
            shutil.rmtree(locale_dir.joinpath(language))

    def test_translations_fuzzy(self):
        locale_dir = self.test_dir.joinpath('locale_fuzzy')
        self.assertEqual(os.listdir(locale_dir), ['zordon.po'])
        for language in updater.SUPPORTED_LANGUAGES:
            locale_dir.joinpath(language).mkdir(parents=True)
            shutil.copyfile(locale_dir.joinpath('zordon.po'), locale_dir.joinpath(language, 'zordon.po'))

        instance = updater.TranslationsUpdater(locale_dir, self.test_dir.joinpath('source'))
        self.assertFalse(instance.is_translations_generated())
        self.assertFalse(instance.regenerate_all())
        self.assertEqual(Counter(updater.SUPPORTED_LANGUAGES + ['zordon.po']), Counter(os.listdir(locale_dir)))

        for language in updater.SUPPORTED_LANGUAGES:
            shutil.rmtree(locale_dir.joinpath(language))

    def test_translations_error(self):
        locale_dir = self.test_dir.joinpath('locale_error')
        self.assertEqual(os.listdir(locale_dir), ['zordon.po'])
        for language in updater.SUPPORTED_LANGUAGES:
            locale_dir.joinpath(language).mkdir(parents=True)
            shutil.copyfile(locale_dir.joinpath('zordon.po'), locale_dir.joinpath(language, 'zordon.po'))

        instance = updater.TranslationsUpdater(locale_dir, self.test_dir.joinpath('source'))
        self.assertFalse(instance.is_translations_generated())
        self.assertFalse(instance.regenerate_all())
        self.assertEqual(Counter(updater.SUPPORTED_LANGUAGES + ['zordon.po']), Counter(os.listdir(locale_dir)))

        for language in updater.SUPPORTED_LANGUAGES:
            shutil.rmtree(locale_dir.joinpath(language))
