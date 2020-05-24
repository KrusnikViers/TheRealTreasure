from app.database.scoped_session import ScopedSession
from app.models.all import *
from tests.base import InBotTestCase


class TestUser(InBotTestCase):
    def test_pending_action_update(self):
        with ScopedSession(self.connection) as session:
            user = User(id=0, name='Test')
            session.add(user)

            # Creating new action returns empty sting.
            self.assertEqual('', user.reset_pending_action('action_1', 25))
            self.assertEqual(1, session.query(PendingAction).count())

            # Different actions for different chats.
            self.assertEqual('', user.reset_pending_action('action_2', 35))
            self.assertEqual(2, session.query(PendingAction).count())

            # Replacing an action should return previous one.
            self.assertEqual('action_1', user.reset_pending_action('action_3', 25))
            self.assertEqual(2, session.query(PendingAction).count())

            # Trying to add the same action should also return nothing.
            self.assertEqual('', user.reset_pending_action('action_3', 25))
            self.assertEqual(2, session.query(PendingAction).count())

    def test_mention_name(self):
        with ScopedSession(self.connection):
            user = User(id=0, name='only_name')
            self.assertEqual('only_name', user.mention_name())
