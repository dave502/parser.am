from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from db.models.document import Document
from db.config import Base
from datetime import datetime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func


class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey(Document.id))
    status_code = Column(Integer)
    update_date = Column(DateTime, default=func.now())

    document = relationship(
        Document,
        backref=backref(
            "history", order_by="History.update_date", cascade="all, delete-orphan"
        ),
    )