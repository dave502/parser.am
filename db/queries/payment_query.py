from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models.payment import Payment


class PaymentQuery:
    """
    DAL (Data Access Layer) class
    """
    #
    # def __init__(self, db_session: AsyncSession, commit=False):
    #     self.db_session = db_session
    #     self.commit = commit

    @staticmethod
    async def add_payment(session: AsyncSession, commit=True, **data):
        new_payment = Payment(
                        user_id=data["user"],
                        date=data["date"],
                        amount=data["total_amount"],
                        invoice_payload=data["invoice_payload"],
                        telegram_payment_charge_id=data["telegram_payment_charge_id"],
                        provider_payment_charge_id=data["provider_payment_charge_id"]
                        )
        session.add(new_payment)
        await session.flush()
        if commit: await session.commit()
        return new_payment.id

    @staticmethod
    async def get_all_payments(session: AsyncSession) -> list[Payment]:
        q = await session.execute(select(Payment).order_by(Payment.date))
        return q.scalars().all()

    @staticmethod
    async def get_user_payments(user_id: int, session: AsyncSession) -> list[Payment]:
        q = await session.execute(select(Payment).where(Payment.user_id == user_id).order_by(Payment.date))
        return q.scalars().all()
