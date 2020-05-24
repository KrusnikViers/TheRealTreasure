from unittest.mock import MagicMock, patch

import app.core.bot
import app.database.connection
from app.handlers.util.reports import ReportsSender
from tests.base import BaseTestCase, MatcherAny


class TestLaunch(BaseTestCase):
    @patch('app.core.bot.Updater', new=MagicMock())
    @patch('app.core.bot.DatabaseConnection', new=MagicMock())
    def test_polling(self):
        ReportsSender.instance = None
        zordon_bot = app.core.bot.Bot()
        zordon_bot.run()

        zordon_bot.updater.start_polling.assert_called_once_with()
        zordon_bot.updater.dispatcher.add_handler.assert_called_with(MatcherAny())
        self.assertFalse(zordon_bot.updater.start_webhook.called)
        self.assertIsNotNone(ReportsSender.instance)
