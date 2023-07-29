

from abc import ABC, abstractmethod

from typing import Dict, Any

from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject


class BaseDatabasePrefixFilter(BaseFilter, ABC):
    _prefix: str
    _data: Dict[str, Any]

    def __init__(self, prefix: str, **kwargs):
        self._prefix = prefix
        self._data = kwargs

    async def __call__(self, _event: TelegramObject):
        prefix = await self.get_prefix(self._data)

        return prefix == self._prefix

    @abstractmethod
    async def get_prefix(self, data: Dict[str, Any]) -> str:
        """
        This method should be overridden

        :param data: all filters kwargs
        :return: function should return prefix from database
        """

        pass
