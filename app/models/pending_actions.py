from sqlalchemy import BigInteger, Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

from app.database.base_model import Base


class PendingAction(Base):
    __tablename__ = 'pending_actions'

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    action = Column(String, nullable=False)

    user = relationship("User", back_populates="pending_actions")
