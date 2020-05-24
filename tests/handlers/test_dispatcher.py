from unittest.mock import MagicMock, PropertyMock

from flexiconf import Configuration
from telegram import Chat

from app.database.scoped_session import ScopedSession
from app.handlers.dispatcher import Dispatcher
from app.handlers.filters import Filter
from app.handlers.util.reports import ReportsSender
from app.models.all import User
from tests.base import BaseTestCase, InBotTestCase, MatcherAny


class TestDispatcher(BaseTestCase):
    def test_inner_handling(self):
        updater = MagicMock()
        instance = Dispatcher(updater, MagicMock(), MagicMock())
        updater.dispatcher.add_handler.assert_called()

        handler_function = MagicMock()

        # Do not handle messages from other bots.
        update = MagicMock()
        type(update.effective_chat).type = Chat.GROUP
        type(update).callback_query = PropertyMock(return_value=None)
        type(update.effective_user).is_bot = PropertyMock(return_value=True)
        instance._handler(handler_function, [], MagicMock(), update)
        self.assertFalse(handler_function.called)

        # Do not handle message of wrong type.
        type(update.effective_user).is_bot = PropertyMock(return_value=False)
        instance._handler(handler_function, [Filter.PRIVATE], update, MagicMock())
        self.assertFalse(handler_function.called)

        instance._handler(handler_function, [Filter.GROUP], update, MagicMock())
        handler_function.assert_called_once()


class TestDispatcherEx(InBotTestCase):
    def test_exception_caught(self):
        with ScopedSession(self.connection) as session:
            user = User(id=1234, login='test', name='Super User')
            session.add(user)

        configuration = Configuration([])
        configuration.set('superuser', 'test')
        bot = MagicMock()
        updater = MagicMock()
        type(updater).bot = PropertyMock(return_value=bot)
        ReportsSender.instance = ReportsSender(bot, configuration)

        instance = Dispatcher(updater, self.connection, MagicMock())
        updater.dispatcher.add_handler.assert_called()

        handler_function = MagicMock()
        handler_function.side_effect = Exception('something bad')

        update = MagicMock()
        type(update.effective_chat).type = Chat.PRIVATE
        type(update).callback_query = PropertyMock(return_value=None)
        type(update).effective_user = PropertyMock(return_value=None)
        type(update).message = PropertyMock(return_value=None)

        self.assertRaises(Exception, instance._handler, handler_function, [Filter.INCOMPLETE_DATA], update, MagicMock())
        handler_function.assert_called_once()
        bot.send_message.assert_called_once_with(1234, MatcherAny())

    def test_no_superuser_no_crash(self):
        configuration = MagicMock()
        type(configuration).superuser_login = PropertyMock(return_value='test')
        bot = MagicMock()
        updater = MagicMock()
        type(updater).bot = PropertyMock(return_value=bot)
        ReportsSender.instance = ReportsSender(bot, configuration)

        instance = Dispatcher(updater, self.connection, MagicMock())
        updater.dispatcher.add_handler.assert_called()

        handler_function = MagicMock()
        handler_function.side_effect = Exception('something bad')

        update = MagicMock()
        type(update.effective_chat).type = Chat.PRIVATE
        type(update).callback_query = PropertyMock(return_value=None)
        type(update).effective_user = PropertyMock(return_value=None)
        type(update).message = PropertyMock(return_value=None)

        self.assertRaises(Exception, instance._handler, handler_function, [Filter.INCOMPLETE_DATA], update, MagicMock())
        handler_function.assert_called_once()
        self.assertFalse(bot.send_message.called)
