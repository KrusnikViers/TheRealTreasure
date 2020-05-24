import functools

from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler, Updater, CallbackContext
from telegram.ext.filters import Filters

from app.database.connection import DatabaseConnection
from app.handlers.actions import Callback
from app.handlers.context import Context
from app.handlers.filters import Filter
from app.handlers.impl import basic, routing
from app.handlers.util.reports import ReportsSender
from app.i18n.translations import Translations


class Dispatcher:
    def __init__(self, updater: Updater, db_connection: DatabaseConnection,
                 translations: Translations):
        self.db = db_connection
        self.translations = translations
        self.updater = updater
        self._bind_all(updater)

    def _handler(self, handler_function, input_filters: list, update: Update, callback_context: CallbackContext):
        if not Filter.apply(input_filters, update):
            return

        try:
            with Context(update, callback_context, self.db, self.translations) as context:
                handler_function(context)
        except Exception as exc:
            ReportsSender.report_exception(self.db)
            raise exc

    def _make_handler(self, raw_callable, input_filters: list):
        return functools.partial(Dispatcher._handler, self, raw_callable, input_filters)

    def command_handler(self, commands_list: list, raw_callable,
                        input_filters: list = list()) -> CommandHandler:
        return CommandHandler(commands_list, self._make_handler(raw_callable, input_filters))

    def callback_handler(self, command: int, raw_callable,
                         input_filters: list = list(),
                         has_params: bool = False) -> CallbackQueryHandler:
        def make_callback_pattern(callback_command: int, has_parameters: bool) -> str:
            return '^{0}{1}$'.format(str(callback_command), '\ .+' if has_parameters else '')

        return CallbackQueryHandler(self._make_handler(raw_callable, input_filters + [Filter.CALLBACK]),
                                    pattern=make_callback_pattern(command, has_params))

    # Modify this method to add new handlers
    def _bind_all(self, updater: Updater):
        handlers = [
            self.command_handler(['start', 'help'], basic.on_help_or_start),
            self.command_handler(['cancel'], basic.on_reset_action),
            self.command_handler(['report'], basic.on_user_report_request),
            self.callback_handler(Callback.CANCEL, basic.on_reset_action),

            # Special empty handler to let bot update user statuses even from non-message events.
            MessageHandler(Filters.all, self._make_handler(routing.dispatch_bare_message, [Filter.INCOMPLETE_DATA])),
        ]

        for handler in handlers:
            updater.dispatcher.add_handler(handler)
