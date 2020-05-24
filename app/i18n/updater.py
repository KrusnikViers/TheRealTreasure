import logging
from pathlib import Path

from babel.messages import catalog, extract, mofile, pofile

SUPPORTED_LANGUAGES = ['ru', 'en']
DEFAULT_LANGUAGE = 'en'


class TranslationsUpdater:
    def __init__(self, locale_dir: Path, sources_dir: Path):
        self.locale_dir = locale_dir
        self.sources_dir = sources_dir

    def is_translations_generated(self) -> bool:
        for lang in SUPPORTED_LANGUAGES:
            if not self.locale_dir.joinpath(lang, 'LC_MESSAGES', 'zordon.mo').is_file():
                return False
        return True

    def regenerate_all(self) -> bool:
        new_catalog = self._build_strings_catalog_from_sources()
        is_complete = True
        for language in SUPPORTED_LANGUAGES:
            self.locale_dir.joinpath(language, 'LC_MESSAGES').mkdir(parents=True, exist_ok=True)
            updated_catalog = self._get_updated_translations(language, new_catalog)
            is_lang_translations_complete = self._is_translations_complete(updated_catalog, language)
            is_complete = is_complete and is_lang_translations_complete
            with self.locale_dir.joinpath(language, 'zordon.po').open(mode='wb') as file:
                pofile.write_po(file, updated_catalog, sort_output=True, width=None, omit_header=True)
            with self.locale_dir.joinpath(language, 'LC_MESSAGES', 'zordon.mo').open(mode='wb') as file:
                mofile.write_mo(file, updated_catalog)
        return is_complete

    def _build_strings_catalog_from_sources(self) -> catalog.Catalog:
        strings_dict = self._get_translatable_strings()
        result = catalog.Catalog()
        for msg, locations in strings_dict.items():
            result.add(msg, locations=locations,)
        return result

    def _get_translatable_strings(self) -> dict:
        strings_list = extract.extract_from_dir(dirname=str(self.sources_dir))
        strings_dict = {}
        for filename, line_num, msg, _, context in strings_list:
            if msg in strings_dict:
                strings_dict[msg].append((filename, line_num))
            else:
                strings_dict[msg] = [(filename, line_num)]
        return strings_dict

    def _get_updated_translations(self, language: str, new_catalog: catalog.Catalog) -> catalog.Catalog:
        current_catalog = self._read_existing_translations_for_language(language)
        current_catalog.update(new_catalog)
        if current_catalog.obsolete:
            obsolete_lines = ', '.join(current_catalog.obsolete.keys())
            logging.warning('Obsolete lines found in {lang}: {lines}'.format(lang=language, lines=obsolete_lines))
        return current_catalog

    def _read_existing_translations_for_language(self, language: str) -> catalog.Catalog:
        file_path = Path(str(self.locale_dir.joinpath(language, 'zordon.po')))
        if file_path.is_file():
            with file_path.open(mode='rb') as file:
                return pofile.read_po(file, locale=language, domain='zordon')
        return catalog.Catalog()

    @staticmethod
    def _check_message_and_get_error(message, language) -> str:
        error_string = ''
        if message.id:
            if not message.string:
                error_string = 'Translation for {msg}({lang}) is missing!'.format(msg=message.id, lang=language)
            elif message.check():
                errors = ', '.join(map(str, message.check()))
                error_string = '{msg}({lang}): {errors}'.format(msg=message.id, lang=language, errors=errors)
            elif message.fuzzy:
                error_string = 'Translation for {msg}({lang}) is fuzzy!'.format(msg=message.id, lang=language)
        return error_string

    @staticmethod
    def _is_translations_complete(strings_catalog: catalog.Catalog, language: str) -> bool:
        is_translations_valid = True
        for msg in strings_catalog:
            error_string = TranslationsUpdater._check_message_and_get_error(msg, language)
            if error_string:
                logging.error(error_string)
                is_translations_valid = False
        return is_translations_valid
