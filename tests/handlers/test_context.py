from unittest.mock import MagicMock, PropertyMock

from telegram import Chat

from app.handlers import context
from tests.base import InBotTestCase


class TestContext(InBotTestCase):
    def test_callback_resolving(self):
        update = MagicMock()
        type(update).effective_user = PropertyMock(return_value=None)
        type(update.effective_chat).type = PropertyMock(return_value=Chat.PRIVATE)
        type(update).message = PropertyMock(return_value=None)
        instance = context.Context(update, MagicMock(), MagicMock(), MagicMock())
        with instance:
            self.assertFalse(instance.update.callback_query.answer.called)
        self.assertTrue(instance.update.callback_query.answer.called)

    def test_effective_user_locale(self):
        effective_user = MagicMock()
        type(effective_user).id = PropertyMock(return_value=0)
        type(effective_user).username = PropertyMock(return_value='login')
        type(effective_user).full_name = PropertyMock(return_value='Test Test')
        type(effective_user).language_code = PropertyMock(return_value='code')
        translations = MagicMock()
        update = MagicMock()
        type(update).effective_user = effective_user
        type(update.effective_chat).type = PropertyMock(return_value=Chat.PRIVATE)
        type(update).message = PropertyMock(return_value=None)
        context.Context(update, MagicMock(), self.connection, translations)
        translations.get.assert_called_once_with('code')

    def test_message_extraction(self):
        update = MagicMock()

        type(update).effective_user = PropertyMock(return_value=None)
        type(update.effective_chat).type = PropertyMock(return_value=Chat.PRIVATE)
        type(update.message).text = PropertyMock(return_value='/command some text after')
        instance = context.Context(update, MagicMock(), MagicMock(), MagicMock())
        self.assertEqual('some text after', instance.command_arguments())

    def test_empty_message_extraction(self):
        update = MagicMock()

        type(update).effective_user = PropertyMock(return_value=None)
        type(update.effective_chat).type = PropertyMock(return_value=Chat.PRIVATE)
        type(update.message).text = PropertyMock(return_value='/command_and_nothing_more')
        instance = context.Context(update, MagicMock(), MagicMock(), MagicMock())
        self.assertEqual('', instance.command_arguments())

    def test_send_response_message(self):
        update = MagicMock()
        instance = context.Context(update, MagicMock(), MagicMock(), MagicMock())
        instance.send_response_message('test_text')
        instance.update.effective_chat.send_message.assert_called_once_with('test_text')
