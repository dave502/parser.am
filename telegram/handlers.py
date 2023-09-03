# https://surik00.gitbooks.io/aiogram-lessons/content/chapter5.html
# https://yookassa.ru/docs/support/payments/onboarding/integration/cms-module/telegram
# https://core.telegram.org/bots/api#sendinvoice
# https://vc.ru/services/734221-priem-platezhey-v-telegram-kak-nastroit-oplatu-v-chate
import json
import logging
import os
import pathlib
from datetime import datetime
from dateutil.relativedelta import relativedelta
from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods.answer_pre_checkout_query import AnswerPreCheckoutQuery
from aiogram.types import Message, ContentType
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from sqlalchemy.ext.asyncio import AsyncSession
import telegram.messages as msgs

from db.queries import RegionQuery, SubscriptionQuery, PaymentQuery, UserQuery, DocumentQuery

from telegram import kb
from telegram.config import config
from telegram.utils import ttl_lru_cache
from logger.logger import TG_LOGGER_NAME, PROCEDURES_LOGGER_NAME, REGION_CHANGES

import glob

logger = logging.getLogger(TG_LOGGER_NAME)
PRICE_FOR_REGION = 10
ADMIN_ID = 180328814
#ZIPJSON_KEY = 'base64(zip(o))'

router = Router()
active_regions: dict[int:str] = {}


@ttl_lru_cache(seconds_to_live=3600)  # кэширование результата функции на 1 час
async def get_active_regions(session: AsyncSession):
    global active_regions
    logger.debug("active regions updating")
    try:
        # query active regions from database
        active_regions = await RegionQuery.get_active_regions(session)
        # objects to dictionary
        active_regions = {region.id: region.name for region in active_regions}
        logger.debug(f"{len(active_regions)} active_regions")
    except Exception as e:
        logger.critical(f"An error occurred while creating a record with user in the database! {e}")


class Ordering(StatesGroup):
    selecting_regions = State()
    paying = State()
    paying_success = State()


# import zlib, base64
# def json_zip(j):
#     j = {
#         ZIPJSON_KEY: base64.b64encode(
#             zlib.compress(
#                 json.dumps(j).encode('utf-8')
#             )
#         ).decode('ascii')
#     }
#     return j


# def json_unzip(j, insist=True):
#     try:
#         assert (j[ZIPJSON_KEY])
#         assert (set(j.keys()) == {ZIPJSON_KEY})
#     except:
#         if insist:
#             raise RuntimeError("JSON not in the expected format {" + str(ZIPJSON_KEY) + ": zipstring}")
#         else:
#             return j
#     try:
#         j = zlib.decompress(base64.b64decode(j[ZIPJSON_KEY]))
#     except:
#         raise RuntimeError("Could not decode/unzip the contents")

#     try:
#         j = json.loads(j)
#     except:
#         raise RuntimeError("Could interpret the unzipped contents")
#     return j


async def show_contract(msg: Message, user_id: int, session: AsyncSession):
    """
    Показать текст контракта
    :param msg:
    :param user_id:
    :param session:
    :return:
    """
    user = None
    try:
        # try to find user by id in database
        user = await UserQuery.get_user_by_id(user_id, session=session)
    except Exception as e:
        logger.critical(f"An error occurred while creating a record with user in the database! {e}")

    if user:
        # if user found just show him the contract
        await msg.answer(msgs.contract)
        await msg.answer(msgs.contract_accepted)
    else:
        # else show contract and button to accept
        await msg.answer(msgs.contract, reply_markup=kb.accept_contract_menu)


# reply_markup=types.ReplyKeyboardRemove())#
"""
************************   CALLBACKS   ************************
"""


#
# @router.message(F.text == "Меню")
# @router.message(F.text == "Выйти в меню")
# @router.message(F.text == "◀️ Выйти в меню")
# async def menu(msg: Message):
#     await msg.answer(msgs.menu, reply_markup=kb.menu)


@router.callback_query(F.data == "active_regions")
async def clb_active_regions(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    Вывод текста с активными регионами
    :param session:
    :param callback:
    :param state:
    :return:
    """
    # clear the previous menu buttons
    callback.message.reply_markup.inline_keyboard.clear()
    await callback.message.edit_reply_markup(callback.inline_message_id, callback.message.reply_markup)

    # update list of active regions from database
    await get_active_regions(session)
    if len(active_regions):
        # show list of active regions
        #regions = [f"<a href={DocumentQuery.get_document_by_region_id(id).url}>{name}</a>" for id, name in active_regions]
        await callback.message.answer(text=msgs.active_regions_title + "\n⦁" +
                                           "\n⦁".join(active_regions.values()))
    else:
        # show text "no active regions"
        await callback.message.answer(text=msgs.no_active_regions_title)
    await callback.answer()


@router.callback_query(kb.CheckedCallbackFactory.filter(F.action == "check"))
async def clb_check_regions(callback: CallbackQuery, callback_data: kb.CheckedCallbackFactory, session: AsyncSession, state: FSMContext):
    """
    Обработка выбора регионов
    :param session:
    :param callback:
    :param callback_data:
    :return:
    """

    await state.clear()
    await state.set_state(Ordering.selecting_regions)

    # update list of active regions from database
    await get_active_regions(session)

    if len(active_regions):

        # new_reply_markup - updated list of regions
        new_reply_markup = callback.message.reply_markup
        # get index of checked element
        index = callback_data.index
        if not callback_data.checked:
            # if element was not checked - add ✔️ before its text
            new_reply_markup.inline_keyboard[index][0].text = "✔️ " + active_regions[int(callback_data.value)]
        else:
            # if element was checked - remove ✔️ before its text
            new_reply_markup.inline_keyboard[index][0].text = active_regions[int(callback_data.value)]

        # invert element's checked state
        callback_data.checked = not callback_data.checked

        # add updated region list back to new_reply_markup (pack() transforms callback_data to string)
        new_reply_markup.inline_keyboard[index][0].callback_data = callback_data.pack()

        # calculate the total sum of checked regions
        total = sum([PRICE_FOR_REGION for item in callback.message.reply_markup.inline_keyboard
                     if 'True' in item[0].callback_data])

        # set calculated sum to the callback value of the last button of list
        total_callback = kb.CheckedCallbackFactory.unpack(new_reply_markup.inline_keyboard[-1][0].callback_data)
        total_callback.value = total
        new_reply_markup.inline_keyboard[-1][0].callback_data = total_callback.pack()

        # add calculated sum to the text of last button of list
        new_reply_markup.inline_keyboard[-1][0].text = f"🟥 Итого {total} руб. " \
                                                       f"{'Нажмите для оплаты ' if total else ''}🟥"

        # replace list of regions with updated list
        await callback.message.edit_reply_markup(callback.inline_message_id, new_reply_markup)
        # add payment button
        await callback.answer(reply_markup=kb.payment_button)
    else:
        # show text "no active regions"
        await callback.message.answer(text=msgs.no_active_regions_title)
        logger.critical(f"Empty list with active regions after selecting!")


@router.callback_query(kb.CheckedCallbackFactory.filter(F.action == "pay"))
async def clb_make_payment(callback: CallbackQuery, callback_data: kb.CheckedCallbackFactory, session: AsyncSession, state: FSMContext):
    global active_regions
    """
    Отправка платежа после подтверждения выбора регионов
    :param callback:
    :param callback_data:
    :return:
    """

    await state.set_state(Ordering.paying)

    if not active_regions:
        await get_active_regions(session)
    if not active_regions:
        await callback.message.answer("Произошла ошибка. Нет активных регионов.")
        logger.critical(f"Empty list with active regions after payment!")
        await callback.answer()

    logger.info(f"user {callback.from_user.id} trying to pay")
    # get selected regions
    selected_regions = [reg.value for item in callback.message.reply_markup.inline_keyboard[:-1]
                        if (
                            reg := (lambda x: x if x.checked else None)(
                                kb.CheckedCallbackFactory.unpack(item[0].callback_data)
                            )
                        )
                        ]

    # stop if no one region was checked
    if not selected_regions:
        await callback.answer("Ни один регион не выбран", show_alert=True)
        await callback.answer()
        return

    # get current user's subscriptions
    user_subscriptions = await SubscriptionQuery.get_user_subscriptions(callback.from_user.id, session)

    # stop if any of selected regions is in user's subscriptions
    intersection = list(set([subs.region.id for subs in user_subscriptions]) & set(selected_regions))
    if intersection:
        await callback.message.answer(
            f"Вы уже подписаны на регион {', '.join([active_regions[i] for i in intersection])}"
            f"\nСделайте выбор ещё раз",
            reply_markup=kb.create_list_of_regions_kb(active_regions))
        await callback.answer()
        return

    # total object for payment system
    total = types.LabeledPrice(label=msgs.labeled_price,
                               amount=int(callback_data.value) * 100)

    # payment token  for payment system
    payment_token = config.payments_provider_token.get_secret_value()

    # payload dict  for payment system
    payload_dict = {
        'user': callback.from_user.id,
        'sum': callback_data.value,
        'date': datetime.now().isoformat(),
        'regions': selected_regions
    }

    await state.update_data(payload=json.dumps(payload_dict))

    del payload_dict['regions']

    # string with selected regions' names
    selected_regions_names_list = ', '.join([active_regions[reg] for reg in selected_regions])

    # if testing payment
    if payment_token.split(':')[1] == 'TEST':
        try:
            # await callback.message.answer('pre_buy_demo_alert')
            await callback.message.answer_invoice(title=msgs.payment_title,
                                                description=msgs.payment_desc + selected_regions_names_list,
                                                provider_token=payment_token,
                                                currency=msgs.currency,
                                                is_flexible=False,  # True если конечная цена зависит от способа доставки
                                                prices=[total],
                                                start_parameter='time-machine-example',
                                                payload=json.dumps(payload_dict),
                                                need_email=True,
                                                send_email_to_provider=True,
                                                provider_data=f'{{'
                                                                f'"receipt":{{'
                                                # f'"email":"example@example.com", '
                                                                f'"items":[{{'
                                                                f'"description": "{msgs.payment_title}",'
                                                                f'"quantity": "1.00",'
                                                                f'"amount":{{ '
                                                                f'"value": "{callback_data.value}",'
                                                                f'"currency" : "{msgs.currency.upper()}"'
                                                                f'}},'
                                                                f'"vat_code": 1'
                                                                f'}}'
                                                                f']}}'
                                                                f'}}'
                                              )
        except Exception as e:
            logger.critical(f"Error {e} while user {callback.from_user.id} sent payment {callback_data.value} {msgs.currency}")
    logger.info(f"user {callback.from_user.id} sent payment {callback_data.value} {msgs.currency}")
    await callback.answer()


@router.pre_checkout_query(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    logger.info(f"process_pre_checkout_query")
    await AnswerPreCheckoutQuery(pre_checkout_query_id=pre_checkout_query.id, ok=True)


# @router.message()
# async def message_handler(msg: Message):
#     await msg.answer(f"Твой ID: {msg.from_user.id}")


@router.callback_query(F.data == "contract")
async def clb_show_contract(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    Показать текст контракта
    :param session:
    :param callback:
    :param state:
    :return:
    """
    # await state.set_state(Gen.text_prompt)
    # await callback.message.edit_text(msgs.license_agreement)

    # clear previous menu
    callback.message.reply_markup.inline_keyboard.clear()
    await callback.message.edit_reply_markup(callback.inline_message_id, callback.message.reply_markup)
    # show contract
    await show_contract(callback.message, callback.from_user.id, session)
    await callback.answer()


@router.callback_query(F.data == "bot_info")
async def clb_bot_info(callback: CallbackQuery, state: FSMContext):
    """
    Вывод информации о боте
    :param callback:
    :param state:
    :return:
    """
    # clear previous menu
    callback.message.reply_markup.inline_keyboard.clear()
    await callback.message.edit_reply_markup(callback.inline_message_id, callback.message.reply_markup)
    # show bot info
    await callback.message.answer(msgs.bot_info, reply_markup=kb.second_menu)
    await callback.answer()


@router.callback_query(F.data == "accept_contract")
async def clb_accept_contract(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    Вывод сообщения о принятии лицензионого соглашения
    И предложения выбрать регионы
    :param session:
    :param callback:
    :param state:
    :return:
    """

    try:
        # if the user has accepted the contract put him in database
        await UserQuery.create_user(callback.from_user.id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), session)
    except Exception as e:
        logging.critical(f"An error occurred while creating a record with user in the database! {e}")
        await callback.answer()
        return

    logger.info(f"the user {callback.from_user.id} has accepted the contract")

    # clear previous menu
    callback.message.reply_markup.inline_keyboard.clear()
    await callback.message.edit_reply_markup(callback.inline_message_id, callback.message.reply_markup)

    # show text that contract is accepted
    await callback.message.answer(msgs.contract_accepted)

    # update list of active regions from database
    await get_active_regions(session)

    if len(active_regions):
        await callback.message.answer(msgs.select_regions, reply_markup=kb.create_list_of_regions_kb(active_regions))
    else:
        await callback.message.answer(text=msgs.no_active_regions_title)
    await callback.answer()


"""
************************   COMMANDS   ************************
"""


@router.message(Command("start"))
async def cmd_start(msg: Message):
    """
    выводит стартовое меню:
        - инфо о работе бота
        - договор
        - список активных регионов
    :param msg:
    :return:
    """
    await msg.answer(msgs.greetings.format(name=msg.from_user.full_name), reply_markup=kb.first_menu)


@router.message(Command("bot_info"))
async def cmd_bot_info(msg: Message):
    """
    Вывод информации о боте
    :return:
    """
    await msg.answer(msgs.bot_info)


@router.message(Command("active_regions"))
async def cmd_active_regions(msg: Message, session: AsyncSession):
    """
    Вывод текста с активными регионами
    :param msg:
    :param session:
    :return:
    """
    await get_active_regions(session)
    if len(active_regions):
        #regions = [f"<a href='{(await DocumentQuery.get_document_by_region_id(id, session)).url}'>{name}</a>" for id, name in active_regions.items()]
        await msg.answer(text=msgs.active_regions_title + "\n⦁" +
                              "\n⦁".join(active_regions.values()))
    else:
        await msg.answer(text=msgs.no_active_regions_title)


@router.message(Command("contract"))
async def cmd_show_contract(msg: Message, session: AsyncSession):
    """
    Показать текст контракта
    :return:
    """
    await show_contract(msg, msg.from_user.id, session)


@router.message(Command("regions"))
# @router.message(F.text == "Выбрать регионы")
async def cmd_choose_regions(msg: Message, session: AsyncSession):
    """
    Вывод списка для выбора региона
    :param session:
    :param msg:
    :return:
    """
    user = await UserQuery.get_user_by_id(msg.from_user.id, session)
    if user:
        await get_active_regions(session)
        if len(active_regions):
            await msg.answer(text=msgs.active_regions_title)
            await msg.answer(text=msgs.check_regions, reply_markup=kb.create_list_of_regions_kb(active_regions))
        else:
            await msg.answer(text=msgs.no_active_regions_title)
    else:
        await msg.answer(
            text="Для выбора регионов и дальнейшей оплаты необходимо согласиться с условиями договора аказания услуг",
            reply_markup=kb.agreement_menu)
    # await msg.answer(text=msgs.check_regions, reply_markup=kb.list_of_regions_kb)


@router.message(lambda msg: msg.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(msg: Message, session: AsyncSession, state: FSMContext):
    """
    вызывается после подтверждения приёма платежа от платёжной системы
    :param msg:
    :param session:
    :return:
    """

    # get payment info from message
    payment_info = msg.successful_payment.dict()

    logger.info(f"payment from user {msg.from_user.id} for {msg.successful_payment.total_amount // 100}"
                f" {msgs.currency} is successful")

    # send message with sum to user about successful payment
    await msg.answer(
        msgs.successful_payment.format(
            total_amount=msg.successful_payment.total_amount // 100,
            currency=msg.successful_payment.currency
        )
    )
    # Сохранить всю необходимую информацию об оплате и пользователе в базу
    try:
        payment_id = await PaymentQuery.add_payment(session=session,
                                                    user=msg.from_user.id,
                                                    date=datetime.now(),
                                                    **payment_info)
    except Exception as e:
        logging.critical(f"An error occurred while creating a record with payment of user {msg.from_user.id} for"
                         f" {msg.successful_payment.total_amount // 100} {msgs.currency} in the database! {e}")
        return

    # get payload with the all user's order information
    # payload = json.loads(payment_info.get('invoice_payload'))

    payment_data = await state.get_data()
    payload = json.loads(payment_data["payload"])
    await state.clear()

    payment_time = datetime.fromisoformat(payload['date'])

    # обновить информацию о подписках для каждого региона
    try:
        for region in payload['regions']:
            await SubscriptionQuery.add_subscription(
                user_id=payload['user'],
                region_id=region,
                payment_id=payment_id,
                start_time=payment_time,
                end_time=payment_time + relativedelta(months=1),  # ! add payed time period
                session=session
            )
        await SubscriptionQuery.commit(session)
    except Exception as e:
        logging.critical(f"An error occurred while creating a records with subscriptions of user {msg.from_user.id} "
                         f"with payload {payment_info.get('invoice_payload')} in the database! {e}")

    await msg.answer(msgs.service_activated)
    # show user's subscriptions
    await cmd_show_subscription_info(msg, session)


@router.message(Command("subs_info"))
async def cmd_show_subscription_info(msg: Message, session: AsyncSession):
    """
    Вывод информации о подписке
    :return:
    """
    user_subscriptions = None
    try:
        user_subscriptions = await SubscriptionQuery.get_user_subscriptions(msg.from_user.id, session)
    except Exception as e:
        logging.critical(f"An error occurred while getting subscriptions for user {msg.from_user.id} "
                         f"from the database! {e}")
    if user_subscriptions:
        # show user's subscriptions
        str_subs = '\n'.join(
            [f"{subscription.region.name} по {subscription.end_time.date()}" for subscription in user_subscriptions])
        await msg.answer(f"Ваши действующие подписки:\n" + str_subs)
    else:
        await msg.answer(f"сейчас у Вас нет действующих подписок")


"""
************************   ADMIN COMMANDS   ************************
"""


@router.message(Command("adminpanel"))
async def cmd_start(msg: Message):
    if msg.from_user.id == ADMIN_ID:
        await msg.answer('Добро пожаловать в Админ-Панель!', reply_markup=kb.admin_menu())


@router.message(F.text == "👨 Пользователи")
async def show_users(msg: Message, session: AsyncSession):
    if msg.from_user.id == ADMIN_ID:
        users = await UserQuery.get_all_users(session)
        await msg.answer(f'Всего {len(users)} зарегистрированных пользователей: ' + "\n" +
                         "\n⦁".join([f'{user.id} : {user.registration_time}' for user in users]))


@router.message(F.text == "💳 Оплаты")
async def show_users(msg: Message, session: AsyncSession):
    if msg.from_user.id == ADMIN_ID:
        payments = await PaymentQuery.get_all_payments(session)
        await msg.answer(f'Список всех платежей: ' + "\n⦁" +
                         "\n⦁".join([f'user {payment.user_id} : date {payment.date} : sum {payment.amount / 100}'
                                     for payment in payments]))


@router.message(F.text == "📃 Лог telegram")
async def show_users(msg: Message, session: AsyncSession):
    if msg.from_user.id == ADMIN_ID:
        app_path = pathlib.Path(__file__).parent.resolve().parents[0]
        log = FSInputFile(f'{app_path}/logs/{TG_LOGGER_NAME}.log')
        await msg.answer_document(log)


@router.message(F.text == "Все процедуры")
async def show_users(msg: Message, session: AsyncSession):
    if msg.from_user.id == ADMIN_ID:
        app_path = pathlib.Path(__file__).parent.resolve().parents[0]
        log = FSInputFile(f'{app_path}/logs/{PROCEDURES_LOGGER_NAME}.log')
        await msg.answer_document(log)


@router.message(F.text == "Все Регионы")
async def show_users(msg: Message, session: AsyncSession):
    if msg.from_user.id == ADMIN_ID:
        app_path = pathlib.Path(__file__).parent.resolve().parents[0]
        log_path = app_path / "logs"
        print(log_path)
        files = list(filter(os.path.isfile, glob.glob(str(log_path) + "/*.csv")))
        log = FSInputFile(max(files))
        await msg.answer_document(log)


@router.message(F.text == "Изменения")
async def show_users(msg: Message, session: AsyncSession):
    if msg.from_user.id == ADMIN_ID:
        app_path = pathlib.Path(__file__).parent.resolve().parents[0]
        log = FSInputFile(f'{app_path}/logs/{REGION_CHANGES}.log')
        await msg.answer_document(log)


@router.message(F.text == "Удалиться")
async def delete_user(msg: Message, session: AsyncSession):
    await UserQuery.delete_user(msg.from_user.id, session)


@router.message(F.text == "▶️ Start cron")
async def show_users(msg: Message, session: AsyncSession):
    if msg.from_user.id == ADMIN_ID:
        app_path = pathlib.Path(__file__).parent.resolve().parents[0]
        cron_log = app_path / 'logs/cron.log'
        os.system("/usr/local/bin/python /bot/reestr_parser/crawl.py")


@router.message(F.text == "⏲ Лог cron")
async def show_users(msg: Message, session: AsyncSession):
    if msg.from_user.id == ADMIN_ID:
        app_path = pathlib.Path(__file__).parent.resolve().parents[0]
        cron_log = app_path / 'logs/cron.log'
        if os.stat(cron_log).st_size == 0:
            await msg.answer('В cron лог отсутсвует содержимое')
        else:
            log = FSInputFile(cron_log)
            await msg.answer_document(log)


@router.message(F.text == "◀️ Выйти")
async def show_users(msg: Message, session: AsyncSession):
    if msg.from_user.id == ADMIN_ID:
        await msg.answer(text="Выход", reply_markup=types.ReplyKeyboardRemove())
