import enum

from sqlalchemy import and_
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from db.models.subscription import Subscripton
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from db.models.user import User
from db.queries import RegionQuery

NoticeType = enum.IntEnum(
    value='NoticeType',
    names='new_info updated_info',
)


class SubscriptionQuery:
    # def __init__(self, db_session: AsyncSession, commit=False):
    #     self.db_session = db_session
    #     self.commit = commit

    @staticmethod
    async def add_subscription(user_id: int,
                               region_id: int,
                               payment_id: int,
                               start_time: datetime,
                               end_time: datetime,
                               session: AsyncSession,
                               commit=True):
        new_subscription = Subscripton(
            user_id=user_id,
            region_id=region_id,
            payment_id=payment_id,
            start_time=start_time,
            end_time=end_time
        )

        session.add(new_subscription)
        await session.flush()
        if commit: await session.commit()

    @staticmethod
    async def get_all_subscriptions(session: AsyncSession) -> list[Subscripton]:
        q = await session.execute(select(Subscripton).order_by(Subscripton.end_time))
        return q.scalars().all()

    @staticmethod
    async def get_user_subscriptions(user_id: int, session: AsyncSession, only_actual: bool = True) -> list[
        Subscripton]:
        today = datetime.today()
        queries = [Subscripton.user_id == user_id]
        if only_actual:
            queries.append(Subscripton.end_time >= today)
        q = await session.execute(select(Subscripton).
                                  where(and_(*queries)).
                                  order_by(Subscripton.end_time).options(selectinload(Subscripton.region), selectinload(Subscripton.user)))
        return q.scalars().all()

    @staticmethod
    async def set_subscription_notice_sent(user_id: int, region: int | str, session: AsyncSession, commit=True):
        q = None
        match region:
            case int():
                q = update(Subscripton). \
                    where((Subscripton.region_id == region) & (Subscripton.user_id == user_id)). \
                    values(notice_sent=True, notice_date=datetime.now(), scheduled=None, notice_text=None)
            case str():
                q = update(Subscripton). \
                    where((Subscripton.region.name == region) & (Subscripton.user_id == user_id)). \
                    values(notice_sent=True, notice_date=datetime.now(), scheduled=None, notice_text=None)
        q.execution_options(synchronize_session="fetch")
        await session.execute(q)
        if commit:
            await session.commit()

    @staticmethod
    def set_subscription_notice_scheduled(region: int | str,
                                          notice_type: NoticeType,
                                          text: str,
                                          session: Session,
                                          only_for_new_users: bool = False):
        q = None
        today = datetime.today()
        extra_queries = []

        if isinstance(region, str):
            region = RegionQuery.sync_get_region_id(session=session, name=region).id

        if only_for_new_users:
            extra_queries.append(Subscripton.notice_sent == False)

        q = update(Subscripton). \
            where(and_(Subscripton.region_id == region, Subscripton.end_time >= today, *extra_queries)). \
            values(scheduled=notice_type, notice_text=text)
        q.execution_options(synchronize_session="fetch")
        session.execute(q)
        session.commit()

    @staticmethod
    async def get_region_subscriptions(region: int | str, session: AsyncSession, actual=True) -> list[Subscripton]:
        today = datetime.today()
        q = None

        match region:
            case int():
                q = await session.execute(select(Subscripton).
                                          where(and_(Subscripton.region_id == region, Subscripton.end_time >= today)).
                                          order_by(Subscripton.end_time))
            case str():
                q = await session.execute(select(Subscripton).
                                          where(and_(Subscripton.region.name == region, Subscripton.end_time >= today)).
                                          order_by(Subscripton.end_time))
        return q.scalars().all()

    @staticmethod
    async def get_scheduled_subscriptions(session: AsyncSession) -> list[Subscripton]:

        q = await session.execute(select(Subscripton).where(Subscripton.scheduled != 0))
        return q.scalars().all()

    @staticmethod
    async def commit(session: AsyncSession):
        await session.commit()
