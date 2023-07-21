

from typing import Union, Any, Optional
from datetime import datetime, date, time

from usefulgram.enums import Const
from usefulgram.exceptions import WrongObjectType

from enum import Enum

from pydantic import BaseModel

from contextlib import suppress


class DecodeCallbackData:
    prefix: str
    additional: list[str]

    @staticmethod
    def _get_prefix_and_additional(
            callback_data: str,
            separator: str
    ) -> tuple[str, list[str]]:

        split_data = callback_data.split(separator)

        additional = split_data[1].split("&")

        return split_data[0], additional

    @staticmethod
    def _get_empty_prefix_and_additional() -> tuple[str, list[str]]:
        return "", []

    def __init__(self, callback_data: Optional[str], separator: str = "/"):
        if callback_data is not None:
            self.prefix, self.additional = self._get_prefix_and_additional(
                callback_data, separator
            )

            return

        self.prefix, self.additional = self._get_empty_prefix_and_additional()

    def _convert_typing_object_to_type(
            self, obj_value: str, *args: type
    ) -> Any:

        for obj_type in args:
            with suppress(ValueError, TypeError):
                return self._convert_str_to_type(
                    obj_value=obj_value,
                    obj_type=obj_type
                )

        raise WrongObjectType

    def _convert_str_to_type(
            self,
            obj_value: str,
            obj_type: Any
    ) -> Any:

        if obj_value == "":
            return None

        if not isinstance(obj_type, type):  # Optional[smt] checker
            optional_types = obj_type.__getattribute__("__args__")

            return self._convert_typing_object_to_type(obj_value, *optional_types)

        if issubclass(obj_type, bool):
            return bool(int(obj_value))

        if issubclass(obj_type, datetime):
            return datetime.strptime(obj_value, Const.DATETIME_FORMAT)

        if issubclass(obj_type, date):
            return datetime.strptime(obj_value, Const.DATETIME_FORMAT).date()

        if issubclass(obj_type, time):
            return datetime.strptime(obj_value, Const.DATETIME_FORMAT).time()

        if issubclass(obj_type, Enum):
            return obj_type[obj_value]

        try:
            return obj_type(obj_value)  # type: ignore

        except (ValueError, AttributeError):
            raise WrongObjectType

    def _iter_key_and_type(
            self, keys: list[str], objects_type: list[type],
            add_prefix: bool
    ) -> dict[str, Any]:

        return_param = {}

        if add_prefix:
            return_param["prefix"] = self.prefix

        additional_value = 0

        for key, obj_type in zip(keys, objects_type):
            if key == "prefix":
                return_param[key] = self._convert_str_to_type(self.prefix, obj_type)

                continue

            return_param[key] = self._convert_str_to_type(
                self.additional[additional_value], obj_type
            )

            additional_value += 1

        return return_param

    def to_format(self, format_objects: type, add_prefix: bool = False) -> Union[BaseModel, object]:
        annotations = format_objects.__annotations__

        keys = list(annotations.keys())
        values = list(annotations.values())

        obj_params = self._iter_key_and_type(keys, values, add_prefix)

        return format_objects(**obj_params)

    @staticmethod
    def class_to_dict(class_: Union[BaseModel, object]) -> dict[str, Any]:
        result_dict = {"prefix": class_.__getattribute__("prefix")}

        for key in class_.__annotations__.keys():
            result_dict[key] = class_.__getattribute__(key)

        return result_dict
