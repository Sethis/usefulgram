

"""
This code based on
https://github.com/wakaree/simple_echo_bot/blob/main/middlewares/throttling.py
"""

from typing import Callable, Dict, Any, Awaitable, MutableMapping, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, User

from cachetools import TTLCache

from usefulgram.enums import Const


class ThrottlingMiddleware(BaseMiddleware):
    RATE_LIMIT = 0.7
    ANSWER_TEXT = Const.TROTTLING_ANSWER

    def __init__(self, rate_limit: float = RATE_LIMIT, answer_text: str = ANSWER_TEXT) -> None:
        self._cache: MutableMapping[int, None] = TTLCache(maxsize=10_000, ttl=rate_limit)
        self._answer_text = answer_text

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Optional[Any]:
        user: Optional[User] = data.get("event_from_user", None)

        if user is not None:
            if user.id in self._cache:
                self._cache[user.id] = None

                if isinstance(event, CallbackQuery):
                    return await self.trottling_answer(self._answer_text, event)

                return

            self._cache[user.id] = None

        return await handler(event, data)

    @staticmethod
    async def trottling_answer(text: str, callback: CallbackQuery):
        return await callback.answer(text, show_alert=True)
