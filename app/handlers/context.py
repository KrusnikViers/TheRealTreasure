from telegram import Chat, Message, Update
from telegram.ext import CallbackContext

from app.database.connection import DatabaseConnection
from app.database.scoped_session import ScopedSession
from app.database.util import get_with_update
from app.i18n.translations import Translations
from app.models.all import User


class Context(ScopedSession):
    def __init__(self, update: Update, callback_context: CallbackContext, db: DatabaseConnection,
                 translations: Translations):
        super(Context, self).__init__(db)
        self.update = update
        self.callback_context = callback_context
        self.sender = self._maybe_get_user_from_update()
        self._translation = self._get_translation(translations)

    def send_response_message(self, text, **kwargs) -> Message:
        return self.update.effective_chat.send_message(text, **kwargs)

    def command_arguments(self) -> str:
        call_text = self.update.message.text
        divider_index = call_text.find(' ')
        if divider_index == -1:
            return ''
        return call_text[divider_index + 1:].strip()

    def __enter__(self):
        super(Context, self).__enter__()
        self._translation.install()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.update.callback_query:
            self.update.callback_query.answer()
        super(Context, self).__exit__(exc_type, exc_val, exc_tb)

    def _maybe_get_user_from_update(self) -> User:
        user = self.update.effective_user
        if not user:
            return None
        return get_with_update(self.session, User, user.id, login=user.username, name=user.full_name)

    def _get_translation(self, translations):
        if self.update.effective_user:
            return translations.get(self.update.effective_user.language_code)
        return translations.get('')
