

import asyncio

from aiogram import Dispatcher, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from usefulgram.middlewares import StackerMiddleware, ThrottlingMiddleware
from usefulgram.keyboard import Builder, Row, Button
from usefulgram.filters import BasePydanticFilter
from usefulgram.lazy import LazyEditor, LazySender


# Place for your perfect token
TOKEN = "TOKEN"


dp = Dispatcher()


# StackerMiddleware add the lazy and other usefulgram things in handlers
dp.update.outer_middleware(StackerMiddleware())

# The awesome trottling middleware
dp.callback_query.outer_middleware(ThrottlingMiddleware())


# Create the filter and the dataclass in one class
class ExampleFilter(BasePydanticFilter):
    pass


@dp.message(Command(commands=["start"]))
async def start_clicker(_message: Message, sender: LazySender):
    text = "It's first page"

    markup = Builder(
        Row(
            Button("Later", ExampleFilter(prefix="later"))
        )
    )

    # This is will send our menu
    await sender.send(text, reply_markup=markup)


@dp.callback_query(ExampleFilter(prefix="later"))
async def change_keyboard(
        _callback: CallbackQuery,
        editor: LazyEditor
):
    text = "You're great"

    markup = Builder(
        Row(
            Button("Remove keyboard", ExampleFilter(prefix="remove"))
        )
    )

    # Will change text and keyboard
    await editor.edit(text=text, reply_markup=markup)


@dp.callback_query(ExampleFilter(prefix="remove"))
async def remove_keyboard(
        _callback: CallbackQuery,
        editor: LazyEditor
):
    # Will remove keyboard
    await editor.edit()


async def main():
    bot = Bot(TOKEN, parse_mode="HTML")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
