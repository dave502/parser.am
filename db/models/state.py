from sqlalchemy import Column, Integer, String

from db.config import Base


class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), index=True, unique=True, nullable=False)
