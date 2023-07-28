from asyncio import exceptions

import requests
# from aiogram.utils.exceptions import BotBlocked
import asyncio
from db.config import async_session
from telegram.config import config
from urllib.parse import urlparse
import logging
from db.queries.subscription_query import SubscriptionQuery


class Informer:

    def __init__(self):
        self.bot = None
        self.loop = None

    hostlogger = logging.getLogger('mylogger.telegram')
    hostlogger.info("Logger has been initialised in the host module")

    @staticmethod
    def notification(doc, date_updated: bool = False) -> str:
        new_notification_text = f"Уважаемый клиент(подписчик), настоящим сообщением уведомляем Вас, " \
                                f"что проект отчёта о результатах государственной кадастровой оценки " \
                                f"в регионе {doc.get('region')} размещён на сайте " \
                                f"государственного бюджетного учреждения по адресу: \n" \
                                f"{doc.get('report_intermediate_docs_link')}.\n" \
                                f"Дата размещения проекта отчёта: {doc.get('report_project_date_start')} \n" \
                                f"Дата окончания срока ознакомления с проектом отчета: {doc.get('report_project_date_end')}\n" \
                                f"Дата окончания приема замечаний к проекту отчета: {doc.get('report_project_date_end')}\n" \
                                f"Замечания к отчёту могут быть направлены в адрес " \
                                f"<a href='{urlparse(doc.get('report_intermediate_docs_link')).netloc}'>" \
                                f"Государственного Бюджетного Учреждения</a>, созданного субъектом Российской Федерации и наделённого " \
                                f"полномочиями, связанными с определением кадастровой стоимости\n" \
                                f"Требования к Замечаниям к проекту отчета содержатся в Статье 14 Федерального закона N 237-ФЗ" \
                                f"\"О государственной кадастровой оценке\" от 03.07.2016"
        date_updated_notification_text = f"Уважаемый клиент(подписчик), настоящим сообщением уведомляем Вас, " \
                                         f"что дата окончания срока ознакомления с проектом отчета в регионе {doc.get('region')} изменилась" \
                                         f"отчёта размещён на сайте государственного бюджетного учреждения по адресу: \n" \
                                         f"{doc.get('report_intermediate_docs_link')}.\n" \
                                         f"Дата размещения проекта отчёта: {doc.get('report_project_date_start')} \n" \
                                         f"Дата окончания срока ознакомления с проектом отчета: {doc.get('report_project_date_end')}\n" \
                                         f"Дата окончания приема замечаний к проекту отчета: {doc.get('report_project_date_end')}\n" \
                                         f"Замечания к отчёту могут быть направлены в адрес " \
                                         f"<a href='{urlparse(doc.get('report_intermediate_docs_link')).netloc}'>" \
                                         f"Государственного Бюджетного Учреждения</a>, созданного субъектом Российской Федерации и наделённого " \
                                         f"полномочиями, связанными с определением кадастровой стоимости\n" \
                                         f"Требования к Замечаниям к проекту отчета содержатся в Статье 14 Федерального закона N 237-ФЗ" \
                                         f"\"О государственной кадастровой оценке\" от 03.07.2016"
        match date_updated:
            case False:
                return new_notification_text
            case True:
                return date_updated_notification_text

    def send_region_notification(self, doc: dict, date_updated: bool = False, only_for_new_users=False):
        # apiToken = config.bot_token.get_secret_value()
        # chatID = '-1001935066797'  # t.me/cadastr
        # apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

        async def async_send_region_notification():

            # async with async_session() as session:
            #     async with session.begin():
            #         subscriptions = await SubscriptionQuery.get_region_subscriptions(doc.get('region'), session=session)
            subscriptions = await SubscriptionQuery.get_region_subscriptions(doc.get('region'), session=async_session)

            if not only_for_new_users:
                users_list = [subscription.user_id for subscription in subscriptions]
            else:
                users_list = [subscription.user_id for subscription in subscriptions if subscription.notice_sent == False]

            count = 0
            try:
                for user_id in users_list:
                    if await self.send_message_to_users_handler(user_id, self.notification(doc, date_updated)):
                        await SubscriptionQuery.set_subscription_notice_sent(
                            user_id=user_id, region=doc.get('region'), session=async_session)
                        count += 1
                    # 20 messages per second (Limit: 30 messages per second)
                    await asyncio.sleep(.05)
            finally:
                logging.info(f"{count} messages successful sent.")

        self.loop.run_in_executor(None, async_send_region_notification)

    #
    # try:
    #     response = requests.post(apiURL, json={'chat_id': chatID, 'text': notification(doc, date_updated)})
    #     print(response.text)
    # except Exception as e:
    #     print(e)

    async def send_message_to_users_handler(
            self, user_id: int, text: str, disable_notification: bool = False
    ) -> bool:
        """
        Safe messages sender
        :param user_id:
        :param text:
        :param disable_notification:
        :return:
        """
        try:
            await self.bot.send_message(
                user_id,
                text,
                disable_notification=disable_notification
            )
        except exceptions.BotBlocked:
            logging.error(f"Target [ID:{user_id}]: blocked by user")
        except exceptions.ChatNotFound:
            logging.error(f"Target [ID:{user_id}]: invalid user ID")
        except exceptions.RetryAfter as e:
            logging.error(
                f"Target [ID:{user_id}]: Flood limit is exceeded. "
                f"Sleep {e.timeout} seconds."
            )
            await asyncio.sleep(e.timeout)
            return await self.bot.send_message(user_id, text)  # Recursive call
        except exceptions.UserDeactivated:
            logging.error(f"Target [ID:{user_id}]: user is deactivated")
        except exceptions.TelegramAPIError:
            logging.exception(f"Target [ID:{user_id}]: failed")
        else:
            logging.info(f"Target [ID:{user_id}]: success")
            return True
        return False


informer = Informer()
