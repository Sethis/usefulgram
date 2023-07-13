

from typing import Dict, Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery

from usefulgram.parsing.decode import DecodeCallbackData
from usefulgram.lazy import LazyEditing


class StackerMiddleware(BaseMiddleware):
    def __init__(self, separator: str = "/"):
        self.separator = separator

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ):
        if not isinstance(event, CallbackQuery):
            return await handler(event, data)

        data["decoder"] = DecodeCallbackData(event.data, self.separator)
        data["lazy"] = LazyEditing(event)

        return await handler(event, data)
