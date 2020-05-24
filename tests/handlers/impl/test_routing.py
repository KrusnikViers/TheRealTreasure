from app.models.all import *
from tests.base import InBotTestCase, ScopedSession


class TestBasicHandlers(InBotTestCase):
    def test_huge_ids(self):
        huge_id = 1 << 62

        with ScopedSession(self.connection) as session:
            new_user = User(id=huge_id, name='New user')
            session.add(new_user)

        with ScopedSession(self.connection) as session:
            self.assertEqual(huge_id, session.query(User).first().id)
