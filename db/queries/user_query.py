from sqlalchemy import update
from sqlalchemy.future import select
# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.user import User


class UserQuery:
    # def __init__(self, db_session: AsyncSession, commit=False):
    #     self.db_session = db_session
    #     self.commit = commit

    @staticmethod
    async def create_user(user_id: int, registration_time: str, session: AsyncSession,
                          accepted_contract=False, referrer=None, commit: bool = True):
        new_user = User(id=user_id, registration_time=registration_time,
                        accepted_contract=accepted_contract, referrer=referrer)
        session.add(new_user)
        await session.flush()
        if commit:
            await session.commit()

    @staticmethod
    async def get_all_users(session: AsyncSession) -> list[User]:
        q = await session.execute(select(User).order_by(User.id))
        return q.scalars().all()

    @staticmethod
    async def get_user_by_id(user_id: int, session: AsyncSession) -> User | None:
        q = await session.execute(select(User).where(User.id == user_id))
        return q.scalars().one_or_none()

    @staticmethod
    async def delete_user(user_id: int, session: AsyncSession) ->  None:
        user = await session.get(User, user_id)
        if user:
            await session.delete(user)
            await session.commit()


    @staticmethod
    def update_user(id: int, session: AsyncSession, updates:dict) -> int:
        #with session.begin():
        try:
            q = update(User).where(User.id == id).values(updates)
            q.execution_options(synchronize_session="fetch")
            res: int = session.execute(q).rowcount
        except Exception as e:
            print(f"update error {e}")
        session.commit()

        return res
