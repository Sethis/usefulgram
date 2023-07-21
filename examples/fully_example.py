

import asyncio

from typing import Optional
from datetime import datetime

from aiogram import Dispatcher, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from usefulgram.middlewares import StackerMiddleware, ThrottlingMiddleware
from usefulgram.keyboard import Builder, Row, Button
from usefulgram.filters import BasePydanticFilter
from usefulgram.lazy import LazyEditing


# Place for your perfect token
TOKEN = ""


dp = Dispatcher()


# StackerMiddleware add the lazy and other usefulgram things in handlers
dp.callback_query.outer_middleware(StackerMiddleware())

# The awesome trottling middleware
dp.callback_query.outer_middleware(ThrottlingMiddleware())


# Create the filter and the dataclass in one class
class ClickerData(BasePydanticFilter):
    prefix: str = "information"
    value: Optional[int] = None
    dt_value: Optional[datetime] = None


def get_markup_by_params(value: int, datetime_value: datetime):
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

    spaces = " " * 4  # This is for more perfect visualizations

    seconds_text = f"{spaces}Time between taps: {round_seconds}{spaces}"

    return Builder(
        Row(Button(value, ClickerData())),
        Row(
            Button("-1", minus_instance),
            Button("+1", plus_instance)
        ),
        Row(Button(seconds_text, ClickerData()))
    )


@dp.message(Command(commands=["start"]), flags={"start": True})
async def start_message(message: Message):
    markup = get_markup_by_params(0, datetime.now())

    await message.answer("UsefulClicker", reply_markup=markup)


@dp.callback_query(ClickerData(prefix="changing"))
async def changing_event(_callback: CallbackQuery, value: int, dt_value: datetime, lazy: LazyEditing):
    markup = get_markup_by_params(value, dt_value)

    await lazy.edit(reply_markup=markup)


@dp.callback_query(ClickerData(prefix="information"))
async def information_answer(callback: CallbackQuery):
    await callback.answer("It is information button", show_alert=True)


async def main():
    bot = Bot(TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
