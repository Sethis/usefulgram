

import asyncio

from aiogram import Dispatcher, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from usefulgram.middlewares import StackerMiddleware, ThrottlingMiddleware
from usefulgram.keyboard import Builder, Row, Button
from usefulgram.filters import BasePydanticFilter
from usefulgram.lazy import LazySender


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
    markup = Builder(
        Row(
            Button("Later", ExampleFilter(prefix="later"))
        )
    )

    # This is will send keyboard with empty text message
    await sender.send(reply_markup=markup)


@dp.callback_query(ExampleFilter(prefix="later"))
async def change_keyboard(
        _callback: CallbackQuery,
        sender: LazySender
):
    text = "You're great"

    markup = Builder(
        Row(
            Button("Remove keyboard", ExampleFilter(prefix="remove"))
        )
    )

    # It will change text and keyboard
    # Also it will answer to callback
    await sender.send(text=text, reply_markup=markup)


@dp.callback_query(ExampleFilter(prefix="remove"))
async def remove_keyboard(
        callback: CallbackQuery,
        sender: LazySender
):
    # Will remove keyboard
    # It will not respond to callback, thanks
    await sender.send("Bye bye!", autoanswer=False)

    await callback.answer()


async def main():
    bot = Bot(TOKEN, parse_mode="HTML")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
