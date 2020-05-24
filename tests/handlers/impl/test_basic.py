from unittest.mock import MagicMock, PropertyMock
from flexiconf import Configuration

from app.database.scoped_session import ScopedSession
from app.handlers.impl import basic, routing
from app.handlers.util.reports import ReportsSender
from app.models.all import *
from tests.base import InBotTestCase


class TestBasicHandlers(InBotTestCase):
    def test_help_or_start_private(self):
        context = MagicMock()
        type(context).group = PropertyMock(return_value=None)
        basic.on_help_or_start(context)
        context.send_response_message.assert_called_once_with('Template v1.0.0_help_for_private')

    def test_help_or_start_group(self):
        context = MagicMock()
        basic.on_help_or_start(context)
        context.send_response_message.assert_called_once_with('Template v1.0.0_help_for_group')

    def test_user_report_sent(self):
        configuration = Configuration([])
        configuration.set('superuser', 'test')
        bot = MagicMock()
        updater = MagicMock()
        type(updater).bot = PropertyMock(return_value=bot)
        ReportsSender.instance = ReportsSender(bot, configuration)

        with ScopedSession(self.connection) as session:
            superuser = User(id=1234, login='test', name='Super User')
            session.add(superuser)
            user = User(id=0, login='reporter', name='Reporting User')
            session.add(user)

            context = MagicMock()
            type(context).sender = PropertyMock(return_value=user)
            type(context).session = PropertyMock(return_value=session)
            type(context.update.effective_chat).id = 777
            basic.on_user_report_request(context)
            context.send_response_message.assert_called_once_with('waiting_for_Reporting User_report')
            context.send_response_message.reset_mock()
            session.flush()

            type(context.update.message).message_id = PropertyMock(return_value=4321)
            routing.dispatch_bare_message(context)
            context.send_response_message.assert_called_once_with('Reporting User_report_sent')
            bot.forward_message.assert_called_once_with(1234, 777, 4321)
            self.assertEqual(0, session.query(PendingAction).count())

    def test_user_report_cancelled(self):
        with ScopedSession(self.connection) as session:
            user = User(id=0, login='reporter', name='Reporting User')
            session.add(user)

            context = MagicMock()
            type(context).sender = PropertyMock(return_value=user)
            type(context).session = PropertyMock(return_value=session)
            type(context.update.effective_chat).id = 777
            basic.on_user_report_request(context)
            context.send_response_message.assert_called_once_with('waiting_for_Reporting User_report')
            context.send_response_message.reset_mock()
            session.flush()

            type(context.update.message).id = PropertyMock(return_value=4321)
            basic.on_reset_action(context)
            context.send_response_message.assert_called_once_with('pending_action_cancelled')
