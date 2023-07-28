from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref

from db.models.user import User
from db.config import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    date = Column(DateTime)
    amount = Column(Integer)
    invoice_payload = Column(String(64))
    telegram_payment_charge_id = Column(String(32))
    provider_payment_charge_id = Column(String(40))

    user = relationship(
        User,
        backref=backref(
            "payments", order_by="Payment.date", cascade="all, delete-orphan"
        ),
    )
