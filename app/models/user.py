from sqlalchemy import BigInteger, Column, String
from sqlalchemy.orm import relationship, object_session

from app.database.base_model import Base
from app.models.pending_actions import PendingAction


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    login = Column(String)
    name = Column(String, nullable=False)

    pending_actions = relationship("PendingAction")

    def mention_name(self):
        return '@' + self.login if self.login else self.name

    def _maybe_find_pending_action(self, chat_id: int) -> PendingAction:
        for pending_action in self.pending_actions:
            if pending_action.chat_id == chat_id:
                return pending_action
        return None

    def _update_existing_action(self, pending_action: PendingAction, action_string: str) -> bool:
        if not action_string:
            object_session(self).delete(pending_action)
        elif pending_action.action != action_string:
            pending_action.action = action_string
        else:
            return False
        return True

    # Returns previous pending action string (if any).
    def reset_pending_action(self, action_string: str, chat_id: int) -> str:
        existing_action = self._maybe_find_pending_action(chat_id)
        if existing_action:
            previous_action_string = existing_action.action
            if self._update_existing_action(existing_action, action_string):
                return previous_action_string
        elif action_string:
            self.pending_actions.append(PendingAction(user_id=self.id, chat_id=chat_id, action=action_string))
        return ''
