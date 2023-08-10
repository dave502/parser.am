import asyncio

from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from db.models.region import Region
from db.config import async_session


class RegionQuery:
    # def __init__(self, db_session=AsyncSession, commit=False):
    #     self.db_session = db_session
    #     self.commit = commit

    @staticmethod
    async def create_regions(session) -> None:
        regions: dict[int, str] = \
            {
                1: "Республика Адыгея",
                2: "Республика Башкортостан",
                3: "Республика Бурятия",
                4: "Республика Алтай",
                5: "Республика Дагестан",
                6: "Республика Ингушетия",
                7: "Кабардино-Балкарская Республика",
                8: "Республика Калмыкия",
                9: "Карачаево-Черкесская Республика",
                10: "Республика Карелия",
                11: "Республика Коми",
                12: "Республика Марий Эл",
                13: "Республика Мордовия",
                14: "Республика Саха (Якутия)",
                15: "Республика Северная Осетия",
                16: "Республика Татарстан",
                17: "Республика Тыва",
                18: "Удмуртская Республика",
                19: "Республика Хакасия",
                20: "Чеченская Республика",
                21: "Чувашская Республика",
                22: "Алтайский край",
                23: "Краснодарский край",
                24: "Красноярский край",
                25: "Приморский край",
                26: "Ставропольский край",
                27: "Хабаровский край",
                28: "Амурская область",
                29: "Архангельская область",
                30: "Астраханская область",
                31: "Белгородская область",
                32: "Брянская область",
                33: "Владимирская область",
                34: "Волгоградская область",
                35: "Вологодская область",
                36: "Воронежская область",
                37: "Ивановская область",
                38: "Иркутская область",
                39: "Калининградская область",
                40: "Калужская область",
                41: "Камчатский край",
                42: "Кемеровская область - Кузбасс",
                43: "Кировская область",
                44: "Костромская область",
                45: "Курганская область",
                46: "Курская область",
                47: "Ленинградская область",
                48: "Липецкая область",
                49: "Магаданская область",
                50: "Московская область",
                51: "Мурманская область",
                52: "Нижегородская область",
                53: "Новгородская область",
                54: "Новосибирская область",
                55: "Омская область",
                56: "Оренбургская область",
                57: "Орловская область",
                58: "Пензенская область",
                59: "Пермский край",
                60: "Псковская область",
                61: "Ростовская область",
                62: "Рязанская область",
                63: "Самарская область",
                64: "Саратовская область",
                65: "Сахалинская область",
                66: "Свердловская область",
                67: "Смоленская область",
                68: "Тамбовская область",
                69: "Тверская область",
                70: "Томская область",
                71: "Тульская область",
                72: "Тюменская область",
                73: "Ульяновская область",
                74: "Челябинская область",
                75: "Забайкальский край",
                76: "Ярославская область",
                77: "Москва",
                78: "Санкт-Петербург",
                79: "Еврейская А.обл.",
                83: "Ненецкий АО",
                86: "Ханты-Мансийский АО",
                87: "Чукотский АО",
                89: "Ямало-Ненецкий АО",
                90: "Запорожская область",
                91: "Республика Крым",
                92: "Севастополь",
                93: "Донецкая Народная Республика",
                94: "Луганская Народная Республика",
                95: "Херсонская область`",
            }
        await session.execute(insert(Region),
                              [
                                  {
                                      "id": idx,
                                      "name": name,
                                      "active": False
                                  }
                                  for idx, name in regions.items()
                              ])
        await session.flush()
        await session.commit()

    @staticmethod
    async def get_all_regions(session: AsyncSession) -> list[Region]:
        q = await session.execute(select(Region).order_by(Region.id))
        return q.scalars().all()


    @staticmethod
    async def get_active_regions(session: AsyncSession) -> list[Region]:
        q = await session.execute(select(Region).where(Region.active == True).order_by(Region.id))
        return q.scalars().all()


    @staticmethod
    async def get_region_id(session: AsyncSession, name: str) -> Region:
        q = await session.execute(select(Region).where(Region.name == name))
        return q.scalars().one_or_none()


    @staticmethod
    def sync_get_region_id(session: Session, name: str) -> Region:
        q = session.execute(select(Region).where(Region.name == name))
        return q.scalars().one_or_none()


    @staticmethod
    async def get_region_by_id(region_id: int, session: AsyncSession) -> Region:
        q = await session.execute(select(Region).where(Region.id == region_id))
        return q.scalars().one()

    @staticmethod
    async def update_region(region_id: int, name: str | None, active: bool | None, session: AsyncSession, commit=True):
        q = update(Region).where(Region.id == region_id)
        if name:
            q = q.values(name=name)
        if active:
            q = q.values(active=active)
        q.execution_options(synchronize_session="fetch")
        await session.execute(q)
        await session.commit()

    @staticmethod
    async def set_region_active(region: int | str, session: AsyncSession, active: bool = True, commit=True):
        q = None
        match region:
            case int():
                q = update(Region).where(Region.id == region).values(active=active)
            case str():
                q = update(Region).where(Region.name == region).values(active=active)
        q.execution_options(synchronize_session="fetch")
        await session.execute(q)
        await session.commit()

    @staticmethod
    def sync_set_region_active(region: int | str,  session: Session, active: bool = True, commit=True):
        q = None
        match region:
            case int():
                q = update(Region).where(Region.id == region).values(active=active)
            case str():
                q = update(Region).where(Region.name == region).values(active=active)
        q.execution_options(synchronize_session="fetch")
        session.execute(q)
        session.commit()

        # async def get_session_and_run():
        #     async with async_session() as session:
        #         async with session.begin():
        #             await RegionQuery.set_region_active(region, session, active, commit)
        #
        # loop = asyncio.get_running_loop()
        # loop.run_until_complete(get_session_and_run())
