from telegram import Chat, Update

from app.handlers.util.inline_menu import callback_data


def _check_personal_callback(update: Update):
    if update.callback_query is None or not update.effective_user:
        return False
    data = callback_data(update)
    return len(data) > 0 and int(data[0]) == update.effective_user.id


class Filter:
    # Messages from groups and supergroups.
    GROUP = 1
    # Messages from private chats.
    PRIVATE = 2
    # Message is a callback from an inline menu button.
    CALLBACK = 10
    # Same as previous, but also checks that the first argument of the callback data is equal to the sender's id.
    PERSONAL_CALLBACK = 11

    # Let pass the message with no effective_chat, effective_user or message.
    INCOMPLETE_DATA = 30

    _CHECKS = {
        GROUP: lambda x: x.effective_chat.type in [Chat.GROUP, Chat.SUPERGROUP],
        PRIVATE: lambda x: x.effective_chat.type == Chat.PRIVATE,
        CALLBACK: lambda x: x.callback_query is not None,
        PERSONAL_CALLBACK: _check_personal_callback,
    }

    _NO_CHECKS = {
        INCOMPLETE_DATA
    }

    @staticmethod
    def _basic_filters(update: Update) -> bool:
        if update.effective_chat and update.effective_chat.type not in [Chat.GROUP, Chat.SUPERGROUP, Chat.PRIVATE]:
            return False
        if update.effective_user and update.effective_user.is_bot: return False
        return True

    @staticmethod
    def _completeness_filters(filters: list, update: Update) -> bool:
        if Filter.INCOMPLETE_DATA in filters:
            return True
        if not update.effective_user or not update.effective_chat:
            return False
        return Filter.CALLBACK in filters or Filter.PERSONAL_CALLBACK in filters or update.message

    @staticmethod
    def apply(filters: list, update: Update):
        if not Filter._basic_filters(update) or not Filter._completeness_filters(filters, update):
            return False
        for filter_value in filters:
            if not (filter_value in Filter._NO_CHECKS or Filter._CHECKS[filter_value](update)):
                return False
        return True
