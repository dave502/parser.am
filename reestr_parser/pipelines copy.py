# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pathlib
import sqlite3
from importlib import resources

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from pymongo.collection import Collection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from reestr_parser.settings import BD_PARAMS
from urllib.parse import urlparse
from urllib.parse import parse_qs
from datetime import datetime
from reestr_parser.msgs import new_notice, date_updated_notice
from db.queries import RegionQuery, SubscriptionQuery, NoticeType
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
        client = MongoClient(**BD_PARAMS)
        self.mongo_base = client.reestr
        # start_date - документы с датой, раньше start_date не рассматриваются
        # self.start_date = datetime.datetime.now() - datetime.timedelta(days=365)
        # self.csv_logger = CSVLogger()

        with resources.path("db", "sqlite.db") as sqlite_path:
            engine = create_engine(f'sqlite:///{sqlite_path}', echo=True)  # future=True,
        Session = sessionmaker()
        Session.configure(bind=engine)
        self.session = Session()

    def process_item(self, item, spider):

        # если год web_документа меньше текущего года -> пропуск
        if int(item['year']) < datetime.today().year:
            return item # ! None

        # document exists in database
        item_in_database: bool = True
        # document should be saved to database
        save_item_to_db: bool = False

        # get web document's ID from the url
        item['_id'] = self.get_url_id(item['url'])
        # get web document's field in dict
        item = {field: value.strip() for (field, value) in item.items() if value}

        logger.debug(f"processing item with region {item['region']} ({item['url']})")

        # init mongo database
        collection: Collection = self.mongo_base[spider.name]

        # look for document in database by ID
        doc = collection.find_one({'_id': item['_id']})

        # если web_документа в БД нет -> запись web_документа в БД (как неактивного)
        if not doc:
            item['active'] = False
            doc = collection.insert_one(item)
            item_in_database = False
            logger.info(f"add region {item['region']} ({item['url']}) to mongodb")

        # получение статусов web_документа и DB_документа
        web_doc_status_code = [key_words in item.get('status').lower() for key_words in STATUSES].index(True)
        db_doc_status_code = [key_words in doc.get('status').lower() for key_words in STATUSES].index(True)

        logger.debug(f"region {item['region']} has status {web_doc_status_code}, old status is {db_doc_status_code}")

        # если статус web_документа знаком
        if web_doc_status_code:
            # и статус != 1 ("сформирован перечень объектов") or
            #             2 ("заключен договор") or
            #             4 ("подготовлен проект") or
            #             5 ("принято решение")
            if web_doc_status_code not in [1, 2, 4, 5]:
                # set db_document as inactive
                collection.update_one({'_id': item['_id']}, {'$set': {'active': False}})
                # set document's region as inactive
                RegionQuery.sync_set_region_active(item['region'], self.session, False)
                logger.debug(f"region {item['region']} was deactivated")
            else:
                # документ следует обновить в mongo db
                save_item_to_db = True

                # set db_document as active
                collection.update_one({'_id': item['_id']}, {'$set': {'active': True}})
                RegionQuery.sync_set_region_active(item['region'], self.session)
                logger.debug(f"region {item['region']} set activated")

                # is document status is "подготовлен проект"
                if web_doc_status_code == 4:
                    # дата окончания приёма замечаний
                    item_report_project_date_end = item.get('report_project_date_end')

                    if db_doc_status_code != 4:
                        # статус документа изменился с 1, 2, 5 на 4("подготовлен проект")
                        # send notifications to users with subscriptions to web_document's region
                        SubscriptionQuery.set_subscription_notice_scheduled(region=item.get("region"),
                                                                            notice_type=NoticeType.new_info,
                                                                            text=new_notice(item),
                                                                            session=self.session)
                        # informer.send_region_notification(item)
                    else:
                        # статус документа был 4
                        # если статус "подготовлен проект" не менялся, то отправляем уведомления только новым
                        # пользователям, которые ешё не получали уведомления
                        SubscriptionQuery.set_subscription_notice_scheduled(region=item.get("region"),
                                                                            notice_type=NoticeType.new_info,
                                                                            text=new_notice(item),
                                                                            session=self.session,
                                                                            only_for_new_users=True)
                        logger.info(f"State for region {item['region']} has changed to 'подготовлен проект'. "
                                    f"Notifications about new state was written to sql database")

                        if item_report_project_date_end != doc.get('report_project_date_end'):
                            # if "report_project_date_end" changed send notifications to users
                            SubscriptionQuery.set_subscription_notice_scheduled(region=item.get("region"),
                                                                                notice_type=NoticeType.updated_info,
                                                                                text=date_updated_notice(item),
                                                                                session=self.session)
                            logger.info(f"Report's final date for region {item['region']} has changed from "
                                        f"{doc.get('report_project_date_end')} to {item_report_project_date_end}."
                                        f"Notifications about updating was written to sql database")

                    # если до окончания приёма замечаний остаётся меньше суток
                    date_today = datetime.now().date()
                    date_project_end = datetime.strptime(item_report_project_date_end, "%d.%m.%Y").date()
                    if (date_project_end - date_today).days <= 1:
                        # пометка документа неактивным
                        collection.update_one({'_id': item['_id']}, {'$set': {'active': False}})
                        # пометка региона неактивным
                        RegionQuery.sync_set_region_active(region=item['region'], session=self.session, active=False)
                        logger.info(f"One day to report's final date remains for region {item['region']}"
                                    f"The region was deactivated")
                    else:
                        # пометка документа активным
                        collection.update_one({'_id': item['_id']}, {'$set': {'active': True}})
                        # пометка региона активным
                        RegionQuery.sync_set_region_active(region=item['region'], session=self.session)
                        logger.debug(f"There are more then one day to report's final date remains for "
                                     f"region {item['region']}. The region was activated")

        if save_item_to_db:
            updated_fields = {field: item[field] for field in item if item.get(field) != doc.get(field)}
            if len(updated_fields):
                # ! restore

                # collection.update_one({'_id': item['_id']}, {'$set': updated_fields})
                logger.debug(f"Document for region {item['region']} was updated in mongo db")

        csv_logger.info(get_row_data(**item,
                                       in_db=item_in_database,
                                       status_id=web_doc_status_code,
                                       old_status_id=db_doc_status_code
                                       if web_doc_status_code != db_doc_status_code else ""))
        # self.csv_logger.write_doc(**item,
        #                           in_db=item_in_database,
        #                           status_id=web_doc_status_code,
        #                           old_status_id=db_doc_status_code if web_doc_status_code != db_doc_status_code else ""
        #                           )

        return item #if save_item_to_db else None

    @staticmethod
    def get_url_id(url):
        parsed_url = urlparse(url)
        item_id = parse_qs(parsed_url.query).get("id")[0]
        return item_id
