from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from importlib import resources
from db.queries import DocumentQuery
import sys

"""
make changes in document's staus in db
command format:
    db_test.py <document_1 id> <status id> <document_2 id> <status id> ... <document_n id> <status id>
command example:
    python db_test.py 20941 5 23134 5
"""

sqlite_path = "/bot/db/sqlite/sqlite.db" #resources.path("db.sqlite", "sqlite.db")
engine = create_engine(f'sqlite:///{sqlite_path}', echo=True)  # future=True,
Session = sessionmaker(engine)

with Session() as session:
    id_status_list = list(zip(sys.argv[1::2], sys.argv[2::2]))

    for id, status in id_status_list:
        res = DocumentQuery.sync_update_document(id=int(id), session=session, updates={'status_code': int(status)})
