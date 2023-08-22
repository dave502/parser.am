import json
import pathlib
import sys
import os
sys.path.insert(0, os.getenv("ROOT_DIR", '/home/dave/DEV/ReestrParser'))
import asyncio
import datetime
from aiogram import Bot, Dispatcher, exceptions
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from db.queries import SubscriptionQuery
from telegram.config import config
from telegram.handlers import router
from telegram.msgs import notice_text
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from db.init_db import new_db, init_db
from db.config import async_session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.middlewares import DbSessionMiddleware
from logger.logger import setup_logger, TG_LOGGER_NAME


async def main():
    async def send_message_to_user(user_id: int, text: str, disable_notification: bool = False) -> bool:
        """
        Safe messages sender
        :param user_id:
        :param text:
        :param disable_notification:
        :return:
        """
        try:
            logger.info(f"Sending message to user {user_id}")
            await bot.send_message(
                user_id,
                text,
                disable_notification=disable_notification
            )
        except exceptions.BotBlocked:
            logger.error(f"Target [ID:{user_id}]: blocked by user")
        except exceptions.ChatNotFound:
            logger.error(f"Target [ID:{user_id}]: invalid user ID")
        except exceptions.RetryAfter as e:
            logger.error(
                f"Target [ID:{user_id}]: Flood limit is exceeded. "
                f"Sleep {e.timeout} seconds."
            )
            await asyncio.sleep(e.timeout)
            return await bot.send_message(user_id, text) is None  # Recursive call
        except exceptions.UserDeactivated:
            logger.error(f"Target [ID:{user_id}]: user is deactivated")
        except exceptions.TelegramAPIError:
            logger.exception(f"Target [ID:{user_id}]: failed")
        else:
            logger.info(f"Target [ID:{user_id}]: success")
            return True
        return False

    async def send_notifications():
        logger.info("Scheduled notifications sending starts")
        async with async_session() as _session:
            async with session.begin():
                subscriptions = await SubscriptionQuery.get_scheduled_subscriptions(_session)
                try:
                    for subscription in subscriptions:
                        data_dict = json.loads(subscription.notice_text)
                        if await send_message_to_user(subscription.user_id, notice_text(data_dict)):
                            await SubscriptionQuery.set_subscription_notice_sent(
                                user_id=subscription.user_id,
                                region=subscription.region_id,
                                session=_session,
                                commit=False)
                        # 20 messages per second (Limit: 30 messages per second)
                        await asyncio.sleep(.05)
                finally:
                    if subscriptions:
                        logger.info(f"notification for user {subscription.user_id} "
                                    f"with region {subscription.region_id} was successful sent")
                    else:
                        logger.info(f"no any notifications to send")

    bot = Bot(token=config.bot_token.get_secret_value(), parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(DbSessionMiddleware(session_pool=async_session))
    dp.callback_query.middleware(CallbackAnswerMiddleware())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)

    async with async_session() as session:
        async with session.begin():
            await init_db(session)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_notifications, 'interval', hours=1)
    scheduler.start()

    try:
        logger.info(f"Bot started")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    app_path = pathlib.Path(__file__).parent.resolve().parents[0]
    logger = setup_logger(TG_LOGGER_NAME, f'{app_path}/logs/{TG_LOGGER_NAME}.log')
    logger.info("Logger has been initialized")

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
