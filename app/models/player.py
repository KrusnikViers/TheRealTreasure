from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.database.base_model import Base
from app.models.user import User


class Player(Base):
    __tablename__ = 'players'

    name = Column(String, primary_key=True)

    user = relationship("User")
