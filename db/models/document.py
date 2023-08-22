from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from db.models.region import Region
from db.config import Base
from sqlalchemy.sql import func


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    region_id = Column(Integer, ForeignKey(Region.id))
    status_code = Column(Integer)
    url = Column(String)
    report_intermediate_docs_link = Column(String)
    report_project_date_start = Column(DateTime)
    report_project_date_end = Column(DateTime)
    update_date = Column(DateTime, onupdate=func.now())

    def to_dict(self):
        return {field.name:getattr(self, field.name) for field in self.__table__.c if field.name != "update_date"}
