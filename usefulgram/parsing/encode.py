

import sys

from typing import Union

from datetime import date, time, datetime

from usefulgram.exceptions import TooMoreCharacters, RecursionObjectParse
from usefulgram.enums import Const


class _Additional:
    def _object_to_str(self, item: object) -> str:
        annotations_keys = list(item.__annotations__.keys())

        result = ""

        for i in annotations_keys:
            if i == "prefix":
                continue

            values = item.__getattribute__(f"{i}")

            result += self._to_str(values, is_recursion=True)

        return result

    def _to_str(
            self,
            item: Union[str, int, bool, None, datetime, date, time, object],
            is_recursion: bool = False
    ) -> str:

        if isinstance(item, (str, int, bool)) or item is None:
            return f"{item}&"

        if isinstance(item, (datetime, date, time)):
            return item.strftime(Const.DATETIME_FORMAT) + "&"

        if is_recursion:
            raise RecursionObjectParse

        try:
            return self._object_to_str(item)

        except AttributeError:
            return f"{item}"

    def __call__(
            self, *args: Union[str, int, bool, None,
                               datetime, date, time, object]
                 ) -> str:

        if args == ():
            return ""

        result = ""

        for i in args:
            result += self._to_str(i)

        result = result[:-1]

        return result


class _CallbackData:
    @staticmethod
    def _get_str_callback_data(
            prefix: str, additional: str, separator: str
    ) -> str:

        return f"{prefix}{separator}{additional}"

    @staticmethod
    def _check_callback_data_bytes(callback_data: str) -> bool:
        size = sys.getsizeof(callback_data)

        true_size = size - 37  # 37 - is a system empty string lenght

        if true_size < 64:
            return True

        raise TooMoreCharacters

    def __call__(
            self, prefix: str,
            *args: Union[str, int, bool, None, datetime, date, time, object],
            separator: str = "/") -> str:

        additional = AdditionalInstance(*args)

        callback_data = self._get_str_callback_data(prefix, additional, separator)

        self._check_callback_data_bytes(callback_data)

        return callback_data


AdditionalInstance = _Additional()
CallbackData = _CallbackData()
