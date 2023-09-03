# create db tables
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from db.config import engine, Base
from db.queries import RegionQuery, StateQuery
from functools import partial


async def new_db(session: AsyncSession):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await RegionQuery.create_regions(session)
        await StateQuery.create_states(session)
        print("sqlite db ready")


async def init_db(session: AsyncSession):
    async with engine.begin() as conn:
        await conn.run_sync(partial(Base.metadata.create_all, checkfirst=True))
        regions = await RegionQuery.get_all_regions(session)
        if not regions:
            await RegionQuery.create_regions(session)
        states = await StateQuery.get_all_states(session)
        if not states:
            await StateQuery.create_states(session)
        print("sqlite db ready")
