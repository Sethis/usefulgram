

from typing import Callable

from datetime import datetime, date, time

import unittest

from usefulgram.parsing.encode import CallbackData
from usefulgram.parsing.decode import DecodeCallbackData

from dataclasses import dataclass


@dataclass()
class OneTextTestClass:
    text: str


@dataclass()
class DatetimeValuesClass:
    datetime_value: datetime
    date_value: date
    time_value: time


@dataclass()
class DifferentTypeValuesTestClass:
    text: str
    number: int
    bool_value: bool
    none_value: None
    time_value: time


@dataclass()
class DifferentTypeValuesWithPrefixTestClass:
    prefix: str
    text: str
    number: int
    bool_value: bool
    none_value: None
    time_value: time


test_date = datetime(year=1999, month=1, day=10, hour=3,
                     minute=30, second=59)

one_text_test_class = OneTextTestClass(text="text")

datetime_values_test_class = DatetimeValuesClass(
    datetime_value=test_date, date_value=test_date.date(),
    time_value=test_date.time()
)

different_type_values_test_class = DifferentTypeValuesTestClass(
    text="text", number=10, bool_value=True,
    none_value=None, time_value=test_date.time()
)

different_type_values_with_prefix_test_class = DifferentTypeValuesWithPrefixTestClass(
    prefix="other_prefix",
    text="smt", number=15, bool_value=False,
    none_value=None, time_value=test_date.time()
)


class DecodeTestCase(unittest.TestCase):
    @staticmethod
    def is_raise_value_exception(fun: Callable, *args, **kwargs) -> bool:
        try:
            fun(*args, **kwargs)
            return False

        except ValueError:
            return True

    def test_one_text_decode_list(self):
        callback = CallbackData("prefix", one_text_test_class)

        decode = DecodeCallbackData(callback).additional

        self.assertTrue(decode == ["text"])

    def test_one_text_decode(self):
        callback = CallbackData("prefix", one_text_test_class)

        decode = DecodeCallbackData(callback).to_format(OneTextTestClass)

        self.assertTrue(decode == one_text_test_class)

    def test_different_type_decode(self):
        callback = CallbackData("prefix", different_type_values_test_class)

        decode = DecodeCallbackData(callback).to_format(DifferentTypeValuesTestClass)

        self.assertTrue(decode == different_type_values_test_class)

    def test_different_type_with_prefix_decode(self):
        callback = CallbackData("other_prefix", different_type_values_with_prefix_test_class)

        decode = DecodeCallbackData(callback).to_format(DifferentTypeValuesWithPrefixTestClass)

        self.assertTrue(decode == different_type_values_with_prefix_test_class)

    def test_datetime_type_values_decode(self):
        callback = CallbackData("prefix", datetime_values_test_class)

        decode = DecodeCallbackData(callback).to_format(DatetimeValuesClass)

        self.assertTrue(decode == datetime_values_test_class)

    def test_another_separator_decode(self):
        callback = CallbackData("other_prefix", different_type_values_with_prefix_test_class,
                                separator="$")

        decode = DecodeCallbackData(callback, separator="$").to_format(DifferentTypeValuesWithPrefixTestClass)

        self.assertTrue(decode == different_type_values_with_prefix_test_class)


if __name__ == '__main__':
    unittest.main()
