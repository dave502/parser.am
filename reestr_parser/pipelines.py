# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pathlib
import sqlite3
from importlib import resources

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
# from pymongo import MongoClient
# from pymongo.collection import Collection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from reestr_parser.settings import BD_PARAMS
from urllib.parse import urlparse
from urllib.parse import parse_qs
from datetime import datetime
from telegram.msgs import new_notice, date_updated_notice
from db.queries import RegionQuery, SubscriptionQuery, DocumentQuery, NoticeType
from logger.logger import get_logger, REGION_CHANGES, setup_logger, ALL_REGIONS_CSV
from logger.data import get_row_data

app_path = pathlib.Path(__file__).parent.resolve().parents[0]
logger = get_logger(REGION_CHANGES)
csv_logger = get_logger(ALL_REGIONS_CSV)

STATUSES = [
    "оценка отменена",
    "сформирован перечень объектов",
    "заключен договор",
    "ознакомление с проектом отчёта об определении",
    "подготовлен проект",
    "принято решение",
    "результаты определения",
    "подготовлен отчёт",
    "ознакомление с проектом отчета об итогах",
]


class ReestrParserPipeline:
    def __init__(self):
        #client = MongoClient(**BD_PARAMS)
        #self.mongo_base = client.reestr
        # start_date - документы с датой, раньше start_date не рассматриваются
        # self.start_date = datetime.datetime.now() - datetime.timedelta(days=365)
        # self.csv_logger = CSVLogger()

        sqlite_path = app_path / "db"/ "sqlite" / "sqlite.db" #resources.path("db.sqlite", "sqlite.db")
        self.engine = create_engine(f'sqlite:///{sqlite_path}', echo=True)  # future=True,
        #Session = sessionmaker(self.engine)"
        self.Session = sessionmaker(self.engine)


        #Session.configure(bind=self.engine)
        #self.session = Session()

    def __del__(self):
        ...
        # if self.session:
        #     self.session.close()

    def process_item(self, item, spider):

        with self.Session() as session:

            # если год web_документа не равен текущему году -> пропуск
            if int(item['year']) != datetime.today().year:
                return item # ! None

            # document exists in database
            item_in_database: bool = True
            # document should be saved to database
            save_item_to_db: bool = False

            region_is_active = False

            # get web document's ID from the url
            item['id'] = self.get_url_id(item['url'])

            # get web document's field in dict
            item = {field: value.strip() for (field, value) in item.items() if value}

            item['id'] = int(item['id'])
            item['status_id'] = [key_words in item.get('status').lower() for key_words in STATUSES].index(True)
            item['report_project_date_start'] = datetime.strptime(item.get('report_project_date_start'), '%d.%m.%Y') if \
                item.get('report_project_date_start') else None
            item['report_project_date_end'] = datetime.strptime(item.get('report_project_date_end'), '%d.%m.%Y') if \
                item.get('report_project_date_end') else None

            logger.debug(f"processing item with region {item['region']} ({item['url']})")

            # init mongo database
            # collection: Collection = self.mongo_base[spider.name]

            # look for document in database by ID
            #doc = collection.find_one({'_id': item['_id']})
            doc = DocumentQuery.sync_get_document_by_id(document_id=item['id'], session=session)

            # если web_документа в БД нет -> запись web_документа в БД (как неактивного)
            if not doc:
                item['active'] = False
                #doc = collection.insert_one(item)
                doc = DocumentQuery.sync_add_document(**item, session=session)
                item_in_database = False
                logger.info(f"add region {item['region']} ({item['url']}) to database")

            # получение статусов web_документа и DB_документа
            web_doc_status_code = item['status_id']
            db_doc_status_code = doc.status_code

            logger.debug(f"region {item['region']} has status {web_doc_status_code}, old status is {db_doc_status_code}")

            # если статус web_документа знаком
            if web_doc_status_code:
                # и статус != 1 ("сформирован перечень объектов") or
                #             2 ("заключен договор") or
                #             4 ("подготовлен проект") or
                #             5 ("принято решение")
                if web_doc_status_code not in [1, 2, 4, 5]:
                    # set db_document as inactive
                    #collection.update_one({'_id': item['_id']}, {'$set': {'active': False}})
                    # set document's region as inactive
                    # RegionQuery.sync_set_region_active(item['region'], session, False)
                    # logger.debug(f"region {item['region']} was deactivated")

                    if web_doc_status_code != db_doc_status_code:
                        save_item_to_db = True
                else:
                    # документ следует обновить в базе данных
                    save_item_to_db = True

                    # set db_document as active
                    #collection.update_one({'_id': item['_id']}, {'$set': {'active': True}})
                    # RegionQuery.sync_set_region_active(item['region'], session)
                    # logger.debug(f"region {item['region']} set activated")

                    region_is_active = True

                    # is document status is "подготовлен проект"
                    if web_doc_status_code == 4:
                        # дата окончания приёма замечаний
                        item_report_project_date_end =  item.get('report_project_date_end').date()

                        notice_dict = {
                                "region":item['region'],
                                "report_intermediate_docs_link":item.get('report_intermediate_docs_link'),
                                "report_project_date_start":item.get('report_project_date_start').strftime("%d.%m.%Y"),
                                "report_project_date_end":item.get('report_project_date_end').strftime("%d.%m.%Y"),
                            }

                        if db_doc_status_code != 4:
                            # статус документа изменился с 1, 2, 5 на 4("подготовлен проект")
                            # send notifications to users with subscriptions to web_document's region
                            SubscriptionQuery.set_subscription_notice_scheduled(region=item.get("region"),
                                                                                notice_type=NoticeType.new_info,
                                                                                text=json.dumps(notice_dict),
                                                                                session=session)
                            logger.info(f"State for region {item['region']} has changed from '{STATUSES[db_doc_status_code]}' "
                                        f"to 'подготовлен проект'. Notifications about new state was written to sql database")

                            # informer.send_region_notification(item)
                        else:
                            # статус документа был 4
                            # если статус "подготовлен проект" не менялся, то отправляем уведомления только новым
                            # пользователям, которые ешё не получали уведомления
                            SubscriptionQuery.set_subscription_notice_scheduled(region=item.get("region"),
                                                                                notice_type=NoticeType.new_info,
                                                                                text=json.dumps(notice_dict),
                                                                                session=session,
                                                                                only_for_new_users=True)
                            logger.info(f"State for region {item['region']} is 'подготовлен проект'. "
                                        f"Notifications for new users about new state was written to sql database")

                            if item_report_project_date_end != doc.report_project_date_end.date():
                                # if "report_project_date_end" changed send notifications to users
                                notice_dict["type"] = "update"
                                SubscriptionQuery.set_subscription_notice_scheduled(region=item.get("region"),
                                                                                    notice_type=NoticeType.updated_info,
                                                                                    text=json.dumps(notice_dict),
                                                                                    session=session)
                                logger.info(f"Report's final date for region {item['region']} has changed "
                                            f"from {doc.report_project_date_end.strftime('%d.%m.%Y')} "
                                            f"to {item_report_project_date_end.strftime('%d.%m.%Y')}. "
                                            f"Notifications about updating was written to sql database")

                        # если до окончания приёма замечаний остаётся меньше суток
                        date_today = datetime.now().date()
                        #date_project_end = datetime.strptime(item_report_project_date_end, "%d.%m.%Y").date()
                        if (item_report_project_date_end - date_today).days <= 1:
                            # пометка документа неактивным
                            #collection.update_one({'_id': item['_id']}, {'$set': {'active': False}})
                            # пометка региона неактивным
                            #RegionQuery.sync_set_region_active(region=item['region'], session=session, active=False)
                            region_is_active = False
                            logger.info(f"One day to report's final date remains for region {item['region']} "
                                        f"The region will be deactivated")
                        # else:
                        #     # пометка документа активным
                        #     #collection.update_one({'_id': item['_id']}, {'$set': {'active': True}})
                        #     # пометка региона активным
                        #     RegionQuery.sync_set_region_active(region=item['region'], session=session)
                        #     logger.debug(f"There are more then one day to report's final date remains for "
                        #                 f"region {item['region']}. The region was activated")

                RegionQuery.sync_set_region_active(item['region'], session, region_is_active)
                logger.debug(f"region {item['region']} set to activated" if region_is_active else "deactivated")

            if save_item_to_db:

                web_doc = {
                    'id': item['id'],
                    'status_code':item['status_id'],
                    'url':item['url'],
                    'report_intermediate_docs_link':item.get('report_intermediate_docs_link'),
                    'report_project_date_start':item.get('report_project_date_start'),
                    'report_project_date_end':item.get('report_project_date_end'),
                }
                updated_fields = {field: web_doc[field] for field in web_doc if web_doc.get(field) != getattr(doc, field)}
                # updated_fields['update_date'] = datetime.now()

                if len(updated_fields):
                    logger.debug(f"Updated fields for region {item['region']}: {updated_fields}")
                    res = DocumentQuery.sync_update_document(id=item['id'], session=session, updates=updated_fields)
                    logger.info(f"Document for region {item['region']} was updated in database ({res}): {updated_fields}")
                else:
                    logger.debug(f"There are no fields to update for region {item['region']}")

            csv_logger.info(get_row_data(**item,
                                        in_db=item_in_database,
                                        old_status_id=db_doc_status_code if web_doc_status_code != db_doc_status_code else ""))

        return item #if save_item_to_db else None

    @staticmethod
    def get_url_id(url):
        parsed_url = urlparse(url)
        item_id = parse_qs(parsed_url.query).get("id")[0]
        return item_id