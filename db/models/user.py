from sqlalchemy import Column, Integer, String, Boolean
from db.config import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    registration_time = Column(String)
    referrer = Column(String(10))
    accepted_contract = Column(Boolean, default=False)

    def __str__(self):
        return f'user {self.id=} was registered at {self.registration_time}, ' \
               f'contract was{" not" if not self.accepted_contract else ""} accepted'
