import asyncio

from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload
from db.models.document import Document
from db.models.history import History
from db.queries import RegionQuery
from db.config import async_session
from datetime import datetime

class DocumentQuery:

    @staticmethod
    async def get_all_documets(session: AsyncSession) -> list[Document]:
        q = await session.execute(select(Document).order_by(Document.id))
        return q.scalars().all()



    @staticmethod
    async def get_document_by_region_id(region_id: int, session: AsyncSession) -> Document | None:
        q = await session.execute(select(Document).where(Document.region_id == region_id).
                            order_by(Document.update_date.desc()))
        return q.scalars().first()


    # @staticmethod
    # async def get_active_regions(session: AsyncSession) -> list[Region]:
    #     q = await session.execute(select(Region).where(Region.active == True).order_by(Region.id))
    #     return q.scalars().all()

    @staticmethod
    def sync_add_document(session: Session, **document)-> Document:

        new_document = Document(
            id = int(document['id']),
            region_id = RegionQuery.sync_get_region_id(session=session, name=document['region']).id,
            status_code = document['status_id'],
            url = document['url'],
            report_intermediate_docs_link = document.get('report_intermediate_docs_link'),
            report_project_date_start = document.get('report_project_date_start'),
            report_project_date_end = document.get('report_project_date_end')
        )

        new_history_record = History(document_id=document['id'], status_code=document['status_id'])

        session.add(new_document)
        session.add(new_history_record)
        session.commit()

        return new_document


    @staticmethod
    def sync_get_document_by_id(document_id: int, session: Session) -> Document | None:
        return session.execute(select(Document).where(Document.id == document_id)).scalar_one_or_none()
        # return q.scalars().one_or_none()


    @staticmethod
    def sync_update_document(id: int, session: Session, updates:dict) -> int:
        #with session.begin():
        try:
            q = update(Document).where(Document.id == id).values(updates)
            q.execution_options(synchronize_session="fetch")
            res: int = session.execute(q).rowcount
        except Exception as e:
            print(f"update error {e}")
        session.commit()

        if new_status:=updates.get("status_code"):
            try:
                new_history_record = History(document_id=id, status_code=new_status)
                session.add(new_history_record)
            except Exception as e:
                print(f"new history record error {e}")
            session.commit()

        return res
