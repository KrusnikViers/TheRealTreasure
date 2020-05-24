import traceback

from flexiconf import Configuration
from telegram import Bot

from app.database.connection import DatabaseConnection
from app.database.scoped_session import ScopedSession
from app.handlers.context import Context
from app.models.all import User


class ReportsSender:
    # Global instance, being initialized by the main bot class.
    instance = None

    def __init__(self, bot: Bot, configuration: Configuration):
        self.bot = bot
        self.superuser_login = configuration.get_string('superuser', default=None)

    @classmethod
    def _find_superuser(cls, session) -> User:
        if cls.instance and cls.instance.superuser_login:
            return session.query(User).filter_by(login=cls.instance.superuser_login).one_or_none()
        return None

    @classmethod
    def report_exception(cls, connection: DatabaseConnection):
        with ScopedSession(connection) as session:
            superuser = cls._find_superuser(session)
            if superuser:
                cls.instance.bot.send_message(superuser.id, traceback.format_exc())

    @classmethod
    def forward_user_message(cls, context: Context):
        superuser = cls._find_superuser(context.session)
        if superuser:
            cls.instance.bot.forward_message(superuser.id,
                                             context.update.effective_chat.id,
                                             context.update.message.message_id)
