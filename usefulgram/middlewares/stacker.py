

from typing import Dict, Any, Awaitable, Callable, Optional

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, CallbackQuery

from usefulgram.exceptions import BotIsUndefined
from usefulgram.parsing.decode import DecodeCallbackData
from usefulgram.lazy import LazyEditing


class StackerMiddleware(BaseMiddleware):
    def __init__(self, stable: bool = False, separator: str = "/"):
        self.separator = separator
        self.stable = stable

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ):
        if not isinstance(event, CallbackQuery):
            return await handler(event, data)

        bot: Optional[Bot] = data.get("bot", None)

        if bot is None:
            raise BotIsUndefined

        data["decoder"] = DecodeCallbackData(
            callback_data=event.data,
            separator=self.separator
        )

        data["lazy"] = LazyEditing(
            callback=event,
            bot=bot,
            stable=self.stable
        )

        return await handler(event, data)
