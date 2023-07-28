from db.config import async_session
from db.dal.user_dal import UserDAL
from db.dal.region_dal import RegionDAL
from db.dal.payment_dal import PaymentDAL
from db.dal.subscription_dal import SubscriptionDAL


async def get_user_dal(commit=False):
    async with async_session() as session:
        async with session.begin():
            return UserDAL(session, commit=commit)


async def get_region_dal(commit=False):
    async with async_session() as session:
        async with session.begin():
            return RegionDAL(session, commit=commit)


async def get_payment_dal(commit=False):
    async with async_session() as session:
        async with session.begin():
            return PaymentDAL(session, commit=commit)


async def get_subscription_dal(commit=False):
    async with async_session() as session:
        async with session.begin():
            return SubscriptionDAL(session, commit=commit)



