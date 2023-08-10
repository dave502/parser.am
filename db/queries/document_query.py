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


    # @staticmethod
    # async def get_active_regions(session: AsyncSession) -> list[Region]:
    #     q = await session.execute(select(Region).where(Region.active == True).order_by(Region.id))
    #     return q.scalars().all()

    @staticmethod
    def sync_add_document(session: Session, commit=True, **document)-> Document:
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
        session.flush()
        if commit: session.commit()
        return new_document


    @staticmethod
    async def get_document_by_region_id(region_id: int, session: AsyncSession) -> Document | None:
        q = await session.execute(select(Document).where(Document.region_id == region_id).
                            options(selectinload(Document.region)).
                            order_by(Document.update_date.desc()))
        return q.scalars().first()



    @staticmethod
    def sync_get_document_by_id(document_id: int, session: Session) -> Document | None:
        q = session.execute(select(Document).where(Document.id == document_id))
        return q.scalars().one_or_none()


    @staticmethod
    async def sync_update_document(id: int, session: Session, updates:dict, commit=True):
        session.query(Document).filter(Document.id == id).update(updates)
        if new_status:=updates.get("status_id"):
            new_history_record = History(document_id=id, status_code=new_status)
        session.add(new_history_record)
        session.commit()