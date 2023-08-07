

from typing import Callable, Union, Optional

from datetime import datetime, date, time

from enum import Enum
from decimal import Decimal

import unittest

from usefulgram.parsing.encode import CallbackData
from usefulgram.parsing.decode import DecodeCallbackData

from pydantic import BaseModel


class OneTextTestClass(BaseModel):
    text: str


class DatetimeValuesClass(BaseModel):
    datetime_value: datetime
    date_value: date
    time_value: time


class DifferentTypeValuesTestClass(BaseModel):
    text: str
    number: int
    bool_value: bool
    none_value: None
    time_value: time


class DifferentTypeValuesWithPrefixTestClass(BaseModel):
    prefix: str
    text: str
    number: int
    bool_value: bool
    none_value: None
    time_value: time


class InvestedClass(BaseModel):
    value1: int = 123
    value2: str = "another_text"


class NestedPadanticClass(BaseModel):
    value1: str = "some_text"
    class_: InvestedClass = InvestedClass()
    value2: int = 100


class EnumValueClass(Enum):
    FIRST: int = 1
    SECOND: int = 2
    THIRD: int = 3


class EnumTestClass(BaseModel):
    value: EnumValueClass


class DecimalTestClass(BaseModel):
    value: Decimal


class UnionValueTestClass(BaseModel):
    value: Union[int, str]


class OptionalTestClass(BaseModel):
    value: Optional[int]


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

different_type_values_with_prefix_test_class = \
    DifferentTypeValuesWithPrefixTestClass(
        prefix="other_prefix",
        text="smt", number=15, bool_value=False,
        none_value=None, time_value=test_date.time()
    )


class DecodeTestCase(unittest.TestCase):
    @staticmethod
    def _is_raise_value_exception(fun: Callable, *args, **kwargs) -> bool:
        try:
            fun(*args, **kwargs)
            return False

        except ValueError:
            return True

    def test_enum_decode(self):
        callback = CallbackData("prefix", EnumValueClass.SECOND)

        decode = DecodeCallbackData(callback).to_format(EnumTestClass)

        self.assertTrue(decode.value.value == 2)

    def test_decimal_decode(self):
        decimal_value = Decimal('1') / Decimal('7')

        callback = CallbackData("prefix", decimal_value)

        decode = DecodeCallbackData(callback).to_format(DecimalTestClass)

        self.assertTrue(decode.value == decimal_value)

    def test_first_union_value_decode(self):
        int_value = 1

        callback = CallbackData("prefix", int_value)

        decode = DecodeCallbackData(callback).to_format(UnionValueTestClass)

        self.assertTrue(decode.value == int_value)

    def test_second_union_value_decode(self):
        str_value = "text"

        callback = CallbackData("prefix", str_value)

        decode = DecodeCallbackData(callback).to_format(UnionValueTestClass)

        self.assertTrue(decode.value == str_value)

    def test_optional_value_decode(self):
        int_value = 1

        callback = CallbackData("prefix", int_value)

        decode = DecodeCallbackData(callback).to_format(OptionalTestClass)

        self.assertTrue(decode.value == int_value)

    def test_none_optional_value_decode(self):
        none_value = None

        callback = CallbackData("prefix", none_value)

        decode = DecodeCallbackData(callback).to_format(OptionalTestClass)

        self.assertTrue(decode.value == none_value)

    def test_unknown_optional_value_decode(self):
        unknown_value = "str"

        callback = CallbackData("prefix", unknown_value)

        result = self._is_raise_value_exception(
            DecodeCallbackData(callback).to_format, OptionalTestClass
        )

        self.assertTrue(result)

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

    def test_nested_decode(self):
        callback = CallbackData("prefix", NestedPadanticClass())

        decode = DecodeCallbackData(callback).to_format(NestedPadanticClass)

        self.assertTrue(decode == NestedPadanticClass())

    def test_different_type_with_prefix_decode(self):
        callback = CallbackData(
            "other_prefix",
            different_type_values_with_prefix_test_class
        )

        decode = DecodeCallbackData(callback).to_format(
            DifferentTypeValuesWithPrefixTestClass
        )

        self.assertTrue(
            decode == different_type_values_with_prefix_test_class
        )

    def test_datetime_type_values_decode(self):
        callback = CallbackData("prefix", datetime_values_test_class)

        decode = DecodeCallbackData(callback).to_format(DatetimeValuesClass)

        self.assertTrue(decode == datetime_values_test_class)

    def test_another_separator_decode(self):
        callback = CallbackData(
            "other_prefix", different_type_values_with_prefix_test_class,
            separator="$"
        )

        decode = DecodeCallbackData(
            callback,
            separator="$"
        ).to_format(DifferentTypeValuesWithPrefixTestClass)

        self.assertTrue(
            decode == different_type_values_with_prefix_test_class
        )


if __name__ == '__main__':
    unittest.main()
