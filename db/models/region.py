from sqlalchemy import Column, Integer, String, Boolean

from db.config import Base


class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), index=True, unique=True, nullable=False)
    active = Column(Boolean, default=False)
