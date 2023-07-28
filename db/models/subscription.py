from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, String, Time
from db.models.user import User
from db.models.payment import Payment
from db.models.region import Region
from db.config import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import and_


class Subscripton(Base):
    __tablename__ = "subscriptons"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    region_id = Column(Integer, ForeignKey(Region.id))
    payment_id = Column(Integer, ForeignKey(Payment.id))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    notice_sent = Column(Boolean, default=False)
    notice_date = Column(DateTime)
    scheduled = Column(Integer)
    notice_text = Column(String)
    send_from_time = Column(Time)
    send_upto_time = Column(Time)

    user = relationship(
        User,
        backref=backref(
            "subscriptons", order_by="Subscripton.end_time", cascade="all, delete-orphan"
        ),
    )

    region = relationship(
        Region,
        backref=backref(
            "subscriptons", order_by="Subscripton.end_time", cascade="all, delete-orphan"
        ),
    )