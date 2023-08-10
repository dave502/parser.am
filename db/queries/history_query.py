import asyncio

from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.history import History
from db.config import async_session


class HistoryQuery:

    @staticmethod
    async def add_status(session: AsyncSession, document_id: int, status: int, commit=True):
        new_record = History(document_id = document_id, status_code = status)
        session.add(new_record)
        await session.flush()
        if commit: await session.commit()