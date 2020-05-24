from unittest.mock import MagicMock, PropertyMock

from telegram import Chat

from app.handlers.filters import Filter
from tests.base import BaseTestCase


class TestInputFilters(BaseTestCase):
    def test_is_valid(self):
        update = MagicMock()

        type(update).effective_chat = PropertyMock(return_value=None)
        type(update.effective_user).is_bot = PropertyMock(return_value=False)
        self.assertFalse(Filter.apply([], update))

        type(update).effective_chat = PropertyMock(return_value=MagicMock())
        type(update.effective_chat).type = Chat.CHANNEL
        self.assertFalse(Filter.apply([], update))

        type(update.effective_chat).type = Chat.PRIVATE
        self.assertTrue(Filter.apply([Filter.PRIVATE], update))
        self.assertTrue(Filter.apply([Filter.PRIVATE, Filter.CALLBACK], update))

        type(update.effective_chat).type = Chat.GROUP
        self.assertTrue(Filter.apply([Filter.GROUP, Filter.CALLBACK], update))

        type(update.effective_chat).type = Chat.SUPERGROUP
        self.assertTrue(Filter.apply([Filter.GROUP], update))

        self.assertFalse(Filter.apply([Filter.PERSONAL_CALLBACK], update))
        type(update).callback_query = PropertyMock(return_value=None)
        self.assertFalse(Filter.apply([Filter.PERSONAL_CALLBACK], update))
        type(update.effective_user).id = PropertyMock(return_value=1234)
        type(update).callback_query = PropertyMock(return_value=MagicMock())
        type(update.callback_query).data = PropertyMock(return_value='command 1234 some other data')
        self.assertTrue(Filter.apply([Filter.PERSONAL_CALLBACK], update))

    def test_all_filters_covered(self):
        filters = [x for x in Filter.__dict__.values() if isinstance(x, int)]
        for filter_value in filters:
            self.assertTrue(filter_value in Filter._CHECKS or filter_value in Filter._NO_CHECKS)
