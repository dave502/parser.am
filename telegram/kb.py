from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def admin_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text="👨 Пользователи"),
        KeyboardButton(text="💳 Оплаты"),
    )
    builder.row(
        KeyboardButton(text="📃 Лог telegram"),
        KeyboardButton(text="Все процедуры"),
    )
    builder.row(
        KeyboardButton(text="Все Регионы"),
        KeyboardButton(text="Изменения"),
    )
    builder.row(
        KeyboardButton(text="◀️ Выйти"),
    )
    return builder.as_markup()


first_menu = [
    [InlineKeyboardButton(text="ℹ️ Узнать подробности о работе бота", callback_data="bot_info")],
    [InlineKeyboardButton(text="🧾 Открыть договор об оказании услуг", callback_data="contract")],
    [InlineKeyboardButton(text="🔎 Список доступных регионов", callback_data="active_regions")],
]
first_menu = InlineKeyboardMarkup(inline_keyboard=first_menu)

second_menu = [
    [InlineKeyboardButton(text="🧾 Открыть договор об оказании услуг", callback_data="contract")],
    [InlineKeyboardButton(text="🔎 Список доступных регионов", callback_data="active_regions")],
]
second_menu = InlineKeyboardMarkup(inline_keyboard=second_menu)

agreement_menu = [
    [InlineKeyboardButton(text="🧾 Открыть договор об оказании услуг", callback_data="contract")],
]
agreement_menu = InlineKeyboardMarkup(inline_keyboard=agreement_menu)

accept_contract_menu = [
    [InlineKeyboardButton(text="📝 Принять условия договора", callback_data="accept_contract")],
]
accept_contract_menu = InlineKeyboardMarkup(inline_keyboard=accept_contract_menu)
#

payment_button = [
    [KeyboardButton(text="Итого к оплате \n Нажмите, чтобы оплатить", pay=True)],
]
payment_button = ReplyKeyboardMarkup(keyboard=payment_button,
                                     resize_keyboard=True,
                                     callback_data="pay")


"""
Кнопки для выбора регионов
"""


class CheckedCallbackFactory(CallbackData, prefix="region_"):
    action: str = "check"
    checked: bool = False
    index: int | None
    value: int


def create_list_of_regions_kb(regions) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    [builder.button(text=region,
                    callback_data=CheckedCallbackFactory(index=i, value=idx),
                    )
     for i, (idx, region) in enumerate(regions.items())]
    builder.button(
        text="🟥 Нажмите, чтобы завершить выбор 🟥 ", callback_data=CheckedCallbackFactory(action="pay", value=0),
        pay=True
    )
    builder.adjust(1)

    return builder.as_markup()
