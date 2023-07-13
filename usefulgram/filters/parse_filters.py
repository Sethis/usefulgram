

from typing import Optional, Union, Dict, Any, Tuple

from pydantic import BaseModel

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery

from usefulgram.parsing.decode import DecodeCallbackData


class BasePydanticFilter(BaseFilter, BaseModel):
    prefix: Optional[str]

    async def __call__(
            self, _callback: CallbackQuery,
            decoder: DecodeCallbackData,
            united: Optional[bool] = False) -> Union[bool, Dict[str, Any]]:

        try:
            callback_data = decoder.to_format(type(self), add_prefix=True)

        except (AttributeError, ValueError, IndexError):
            return False

        for item_name in self.__fields__.keys():
            result = self.__getattribute__(item_name)

            if result is None:
                continue

            if callback_data.__getattribute__(item_name) != result:
                return False

        if united:
            return decoder.class_to_dict(callback_data)

        if len(callback_data.__annotations__) == len(decoder.additional):
            return decoder.class_to_dict(callback_data)

        return False


class CallbackPrefixFilter(BaseFilter):
    def __init__(self, prefix: str):
        """

        :param prefix: first argument in callback data
        """
        self.prefix = prefix

    async def __call__(self, message: CallbackQuery,
                       decoder: DecodeCallbackData) -> bool:

        if self.prefix == decoder.prefix:
            return True

        return False


class ItarationFilter(BaseFilter):
    def __init__(self, item_number: int = 0):
        self._item_number: int = item_number
        self._operation: Optional[Tuple[str, Any]] = None
        self._error_result: bool = False

    def __getitem__(self, item: int):
        self._item_number = item

    @staticmethod
    def _convert(other: str) -> Optional[int]:
        try:
            return int(other)

        except ValueError:
            return None

    def __eq__(self, other: Any):
        self._operation = ("eq", other)

    def __ne__(self, other: Any):
        self._operation = ("ne", other)

    def __lt__(self, other: Any):
        int_other = self._convert(other)

        if int_other is None:
            self._error_result = True

            return

        self._operation = ("lt", int_other)

    def __gt__(self, other: Any):
        int_other = self._convert(other)

        if int_other is None:
            self._error_result = True

            return

        self._operation = ("gt", int_other)

    def __le__(self, other: Any):
        int_other = self._convert(other)

        if int_other is None:
            self._error_result = True

            return

        self._operation = ("le", int_other)

    def __ge__(self, other: Any):
        int_other = self._convert(other)

        if int_other is None:
            self._error_result = True

            return

        self._operation = ("ge", int_other)

    @staticmethod
    def _do_operation(operation: str, first_item: Any, second_item: Any):
        if operation == "eq":
            return first_item == second_item

        if operation == "ne":
            return first_item != second_item

        if operation == "lt":
            return first_item < second_item

        if operation == "gt":
            return first_item > second_item

        if operation == "le":
            return first_item <= second_item

        if operation == "ge":
            return first_item >= second_item

    async def __call__(self, _callback: CallbackQuery,
                       decoder: DecodeCallbackData):

        if self._error_result:
            return False

        first_item = (decoder.prefix, decoder.additional)[self._item_number]

        operation, second_item = self._operation

        return self._do_operation(operation, first_item, second_item)
