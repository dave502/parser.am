from aiogram.fsm.storage.memory import MemoryStorage

from config import config
import asyncio
from aiogram import Bot, Dispatcher
from handlers import questions, different_types, group_games, usernames, common, ordering_food
#from middlewares.weekend import WeekendCallbackMiddleware
import logging


async def main():

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # ~ Объект бот
    bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")

    # ~ Диспетчер (корневой роутер)
    # ~ параметр storage=MemoryStorage() нужен для конечного автомата.
    # ! MemoryStorage хранит данные в оперативной памяти, поэтому не рекомендуется использовать его в реальных проектах
    # ~ Доступные хранилища можно посмотреть в репозитории
    # ~ https://github.com/aiogram/aiogram/tree/dev-3.x/aiogram/fsm/storage
    dp = Dispatcher(storage=MemoryStorage())

    # ~ подключение роутеров к диспетчеру (важен порядок импортов!
    # ~ - роутеры будут обрабатывать сообщение по очереди, пока не найдётся нужный фильтр):
    dp.include_routers(questions.router,
                       group_games.router,
                       usernames.router,
                       # in_pm.router, events_in_group.router,
                       # bot_in_group.router, admin_changes_in_group.router
                       common.router,
                       ordering_food.router)  # different_types.router,
    dp.callback_query.outer_middleware(WeekendCallbackMiddleware())  # подключается мидлварь (на все колбэки)
    # Альтернативный вариант регистрации роутеров по одному на строку
    # dp.include_router(questions.router)
    # dp.include_router(different_types.router)

    # Подгрузка списка админов
    #admins = await bot.get_chat_administrators(config.main_chat_id)
    #admin_ids = {admin.user.id for admin in admins}


    # ~ Запуск процесса поллинга новых апдейтов
    # await dp.start_polling(bot)
    # ~ пропускаем все накопленные входящие
    await bot.delete_webhook(drop_pending_updates=True)
    #await dp.start_polling(bot)
    #await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), admins=admin_ids)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == '__main__':
    asyncio.run(main())
