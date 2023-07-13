

from typing import Union
from datetime import datetime, date, time

from usefulgram.enums import Const

from pydantic import BaseModel
from dataclasses import dataclass


class DecodeCallbackData:
    prefix: str
    additional: list[str]

    @staticmethod
    def _parse(callback_data: str, separator: str) -> tuple[str, list[str]]:
        split_data = callback_data.split(separator)

        additional = split_data[1].split("&")

        return split_data[0], additional

    def __init__(self, callback_data: str, separator: str = "/"):
        self.prefix, self.additional = self._parse(callback_data, separator)

    def _convert_str_to_type(self, obj_value: str, obj_type: Union[type, object]):
        if obj_value == "None":
            return None

        if not isinstance(obj_type, type):
            optional_type = obj_type.__getattribute__("__args__")[0]

            return self._convert_str_to_type(obj_value, optional_type)

        if issubclass(obj_type, datetime):
            return datetime.strptime(obj_value, Const.DATETIME_FORMAT)

        if issubclass(obj_type, date):
            return datetime.strptime(obj_value, Const.DATETIME_FORMAT).date()

        if issubclass(obj_type, time):
            return datetime.strptime(obj_value, Const.DATETIME_FORMAT).time()

        if issubclass(obj_type, bool):
            if obj_value == "False":
                return False

        return obj_type(obj_value)

    def _iter_key_and_type(
            self, keys: list[str], objects_type: list[type],
            add_prefix: bool
    ) -> dict[str, type]:

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

    def to_format(self, format_objects: type, add_prefix: bool = False) -> Union[BaseModel, dataclass]:
        annotations = format_objects.__annotations__

        keys = list(annotations.keys())
        values = list(annotations.values())

        obj_params = self._iter_key_and_type(keys, values, add_prefix)

        return format_objects(**obj_params)

    @staticmethod
    def class_to_dict(class_: Union[BaseModel, dataclass]):
        result_dict = {}

        for key in class_.__fields__.keys():
            result_dict[key] = class_.__getattribute__(key)

        return result_dict
