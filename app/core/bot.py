import logging

from flexiconf import ArgsLoader, Configuration, JsonLoader
from telegram.ext import Updater

from app.core.info import APP_DIR, ROOT_DIR
from app.core.utils import global_logging_init
from app.database.connection import DatabaseConnection
from app.handlers.dispatcher import Dispatcher
from app.handlers.util.reports import ReportsSender
from app.i18n.translations import Translations


class Bot:
    def __init__(self):
        self.updater: Updater = None
        self.configuration: Configuration = None
        self.database_connection: DatabaseConnection = None
        self.translations: Translations = None

    def run(self):
        self._set_up()
        logging.info('Launching bot: ' + str(self.updater.bot.get_me()))
        self.updater.start_polling()
        # This call will lock execution until worker threads are stopped with SIGINT(2), SIGTERM(15) or SIGABRT(6).
        self.updater.idle()

    def _set_up(self):
        global_logging_init()

        self.configuration = Configuration([
            JsonLoader(str(ROOT_DIR / 'configuration.json')),
            ArgsLoader()
        ])

        self.database_connection = DatabaseConnection(self.configuration)
        self.translations = Translations(APP_DIR.joinpath('i18n'), APP_DIR)
        self.updater = Updater(token=self.configuration.get_string('telegram_bot_token', default=""), use_context=True)
        self.dispatcher = Dispatcher(self.updater, self.database_connection, self.translations)

        ReportsSender.instance = ReportsSender(self.updater.bot, self.configuration)
