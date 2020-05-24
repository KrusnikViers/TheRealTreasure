from sqlalchemy import Column, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base_model import Base
from app.models.user import User


class Player(Base):
    __tablename__ = 'players'

    name = Column(String, primary_key=True)

    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
