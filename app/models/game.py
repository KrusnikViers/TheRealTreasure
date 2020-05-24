from sqlalchemy import Column, String

from app.database.base_model import Base


class Game(Base):
    __tablename__ = 'games'

    name = Column(String, primary_key=True)
