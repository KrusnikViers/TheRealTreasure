from unittest.mock import MagicMock, PropertyMock

from telegram import InlineKeyboardButton

from app.handlers import actions
from app.handlers.util import inline_menu
from tests.base import BaseTestCase


class TestInlineMenu(BaseTestCase):
    def test_callback_data(self):
        update = MagicMock()
        type(update.callback_query).data = PropertyMock(return_value='123 1 False What?')
        self.assertEqual(('1', 'False', 'What?'), inline_menu.callback_data(update))

    def test_close_button(self):
        menu = inline_menu.InlineMenu([[('manual_close', [actions.Callback.CANCEL, 'test', 'what?'])]], 'close_button')
        self.assertEqual(['0 test what?', '0'], [x[0].callback_data for x in menu.inline_keyboard])
        self.assertEqual([[InlineKeyboardButton('manual_close', callback_data='0 test what')],
                          [InlineKeyboardButton('close_button', callback_data='0')]], menu.inline_keyboard)

    def test_user_id(self):
        menu = inline_menu.InlineMenu([[('manual_close', [actions.Callback.CANCEL, 'test', 'what?'])]], 'close_button',
                                      user_id=1234)
        self.assertEqual(['0 1234 test what?', '0 1234'], [x[0].callback_data for x in menu.inline_keyboard])
        self.assertEqual([[InlineKeyboardButton('manual_close', callback_data='0 test what')],
                          [InlineKeyboardButton('close_button', callback_data='0')]], menu.inline_keyboard)
