import asyncio

from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from db.models.state import State
from db.config import async_session


class StateQuery:

    @staticmethod
    async def create_states(session) -> None:
        states: dict[int, str] = \
            {
                0: "оценка отменена",
                1: "сформирован перечень объектов",
                2: "заключен договор",
                3: "ознакомление с проектом отчёта об определении",
                4: "подготовлен проект",
                5: "принято решение",
                6: "результаты определения",
                7: "подготовлен отчёт",
                8: "ознакомление с проектом отчета об итогах",
            }
        await session.execute(insert(State),
                              [
                                  {
                                      "id": idx,
                                      "name": name,
                                  }
                                  for idx, name in states.items()
                              ])
        await session.flush()
        await session.commit()

    @staticmethod
    async def get_all_states(session: AsyncSession) -> list[State]:
        q = await session.execute(select(State).order_by(State.id))
        return q.scalars().all()


    @staticmethod
    async def get_state_name(session: AsyncSession, id: int) -> str | None:
        q = await session.execute(select(State).where(State.id == id))
        region = q.scalars().one_or_none()
        return region.name if region else None
