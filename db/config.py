from importlib import resources
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

with resources.path(__package__ + ".sqlite", "sqlite.db") as sqlite_path:
    DATABASE_URL = f'sqlite+aiosqlite:///{sqlite_path}'

engine = create_async_engine(DATABASE_URL, future=True, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()
