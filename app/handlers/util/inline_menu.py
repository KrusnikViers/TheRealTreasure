from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from app.handlers import actions


class InlineMenu(InlineKeyboardMarkup):
    # Expects a list of rows, where each row is a list of tuples ('Button text', [command, <parameters>])
    def __init__(self, markup: list, close_button_text: str = '', user_id: int = None):
        if close_button_text:
            markup.append([(close_button_text, [actions.Callback.CANCEL])])

        if user_id:
            self._insert_user_id(markup, user_id)

        def encode(data): return ' '.join([str(x) for x in data])
        super(InlineMenu, self).__init__([[InlineKeyboardButton(text, callback_data=encode(data))
                                           for text, data in row] for row in markup])

    @staticmethod
    def _insert_user_id(markup: list, user_id: int):
        for row in markup:
            for text, data in row:
                data.insert(1, user_id)


def callback_data(update: Update) -> tuple:
    # First element is a command identifier.
    return tuple(update.callback_query.data.split()[1:])
