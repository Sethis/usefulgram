

from typing import Optional

import asyncio

from aiogram import Dispatcher, Bot
from aiogram.types import Message, CallbackQuery, ErrorEvent

from usefulgram.middlewares import StackerMiddleware, ThrottlingMiddleware
from usefulgram.filters import BasePydanticFilter

from usefulgram.keyboard import Builder, Row, Button
from usefulgram.lazy import LazyEditor, LazySender


# Place for your perfect token
TOKEN = ""


dp = Dispatcher()


# StackerMiddleware add the lazy and other usefulgram things in handlers
dp.update.outer_middleware(StackerMiddleware())

# The awesome trottling middleware
# WHen simple = False, middleware do not ignore all limit message
# But it raise error which you can work
dp.update.outer_middleware(ThrottlingMiddleware(simple=False))


# Create the filter and the dataclass in one class
class ExampleFilter(BasePydanticFilter):
    value: Optional[int] = None


@dp.message()
async def start_clicker(_message: Message, sender: LazySender):
    text = "It's first page and your value is <b>0</b>"

    markup = Builder(
        Row(
            Button("+1", ExampleFilter(prefix="change", value=1))
        )
    )

    # This is will send our menu
    await sender.send(text, reply_markup=markup)


@dp.callback_query(ExampleFilter(prefix="change"))
async def change_keyboard(
        _callback: CallbackQuery,
        editor: LazyEditor,
        value: int
):
    text = f"Your perfect values is: <b>{value}</b>"

    markup = Builder(
        Row(
            Button("+1", ExampleFilter(prefix="change", value=value+1))
        )
    )

    # Will change text and keyboard
    await editor.edit(text=text, reply_markup=markup)


@dp.error()
async def send_throttling(error: ErrorEvent):
    if error.update.callback_query:
        return await error.update.callback_query.answer(
            "You are hit a limit", show_alert=True
        )


async def main():
    bot = Bot(TOKEN, parse_mode="HTML")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
