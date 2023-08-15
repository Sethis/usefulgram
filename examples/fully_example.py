

import asyncio

from typing import Optional
from datetime import datetime

from aiogram import Dispatcher, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.filters import Command

from usefulgram.middlewares import StackerMiddleware, ThrottlingMiddleware

from usefulgram.keyboard import Builder, Row, Button
from usefulgram.filters import BasePydanticFilter
from usefulgram.lazy import LazyEditor, LazySender


# Place for your perfect token
TOKEN = ""


dp = Dispatcher()


# StackerMiddleware add the lazy and other usefulgram things in handlers
dp.update.outer_middleware(StackerMiddleware())

# The awesome trottling middleware
# More examples of throttling see in throttling_examples
dp.update.outer_middleware(ThrottlingMiddleware())


# Create the filter and the dataclass in one class
class ClickerData(BasePydanticFilter):
    prefix: str = "information"
    value: Optional[int] = None
    dt_value: Optional[datetime] = None


def get_markup_by_params(
        value: int,
        datetime_value: datetime
) -> InlineKeyboardMarkup:

    current_datetime = datetime.now()

    dt_delta = current_datetime - datetime_value
    round_seconds = round(dt_delta.total_seconds(), 1)

    # Get the dataclass by params
    minus_instance = ClickerData(
        prefix="changing",
        value=value - 1,
        dt_value=current_datetime
    )

    plus_instance = ClickerData(
        prefix="changing",
        value=value + 1,
        dt_value=current_datetime
    )

    seconds_text = f"Time between taps: {round_seconds}"

    return Builder(
        Row(Button(value, ClickerData(prefix="stop", value=value))),
        Row(
            Button("-1", minus_instance),
            Button("+1", plus_instance)
        ),
        Row(Button(seconds_text, ClickerData()))
    )


@dp.message(Command(commands=["start"]))
async def start_clicker(_message: Message, sender: LazySender):
    markup = get_markup_by_params(0, datetime.now())

    # This is will send our menu
    await sender.send("The perfect UsefulClicker", reply_markup=markup)


@dp.callback_query(ClickerData(prefix="changing"))
async def change_keyboard(
        _callback: CallbackQuery,
        value: int,
        dt_value: datetime,
        editor: LazyEditor
):

    markup = get_markup_by_params(value, dt_value)

    await editor.edit(reply_markup=markup)  # This will only edit the keyboard


@dp.callback_query(ClickerData(prefix="information"))
async def send_information_answer(callback: CallbackQuery):
    await callback.answer("This is an information button", show_alert=True)


@dp.callback_query(ClickerData(prefix="stop"))
async def stop_clicker(
        _callback: CallbackQuery,
        value: int,
        sender: LazySender,
        editor: LazyEditor
):
    await editor.edit()  # This will edit the keyboard and save the text

    await sender.send(f"Your number is <b>{value}</b>")


async def main():
    bot = Bot(TOKEN, parse_mode="HTML")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
