from sqlalchemy import Column, String, BigInteger, Integer

from app.database.base_model import Base


class Player(Base):
    __tablename__ = 'players'

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
