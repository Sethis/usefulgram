

import asyncio
from typing import Optional

from datetime import datetime, date

from aiogram import Dispatcher, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from usefulgram.middlewares import StackerMiddleware, ThrottlingMiddleware
from usefulgram.utils.calendar_manager import (
    calendar_manager,
    CalendarDateFilter,
    CalendarInfoButton,
    CalendarChangeButton,
    en_calendar
)

from usefulgram.lazy import LazyEditor, LazySender
from usefulgram.enums import CalendarEnum

# Place for your perfect token
TOKEN = ""


dp = Dispatcher()


# The awesome trottling middleware
dp.callback_query.outer_middleware(ThrottlingMiddleware())

# StackerMiddleware add the lazy and other usefulgram things in handlers
dp.update.outer_middleware(StackerMiddleware())


# This is optional, you can not inherit and use default CalendarDateFilter
class CalendarResult(CalendarDateFilter):
    location: Optional[str] = None


@dp.message(Command(commands=["start"]))
async def start_calendar(_message: Message, sender: LazySender):
    current_datetime = datetime.now()

    # The class can also be inherited
    # so that other parameters can be passed to it
    result_class = CalendarResult(
        prefix="calendar_result",
        location="first page"
    )

    # text params is optional,
    # so it generates an empty text with the keyboard
    return await calendar_manager.show(
        sender=sender,
        month=current_datetime.month,
        year=current_datetime.year,
        result_class=result_class,
        localization_class=en_calendar
    )


@dp.callback_query(CalendarInfoButton(button_type=CalendarEnum.DATE))
async def send_calendar_date_info(callback: CallbackQuery):
    await callback.answer("You clicked on the date. Why?", show_alert=True)


@dp.callback_query(CalendarInfoButton())
async def send_calendar_info(callback: CallbackQuery):
    await callback.answer("This interface button", show_alert=True)


@dp.callback_query(CalendarChangeButton())
async def change_calendar_page(
        _callback: CallbackQuery,
        year: int,
        month: int,
        editor: LazyEditor,
        sender: LazySender
):

    result_class = CalendarResult(
        prefix="calendar_result", location="another page"
    )

    return await calendar_manager.show(
        text="Hello from the example of the usefulgram calendar",
        sender=sender,
        month=month,
        year=year,
        result_class=result_class,
        localization_class=en_calendar,
        editor=editor
    )


@dp.callback_query(CalendarResult())
async def send_result(
        _callback: CallbackQuery,
        date_value: date,
        location: str,
        editor: LazyEditor,
        sender: LazySender
):
    await editor.edit()

    await sender.send(
        f"Your location: <b>{location}</b>"
        f"\nYou chose: <b>{date_value}</b>"
    )


async def main():
    bot = Bot(TOKEN, parse_mode="HTML")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
