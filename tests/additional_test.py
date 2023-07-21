

from typing import Callable

from datetime import datetime, date, time

import unittest

from usefulgram.parsing.encode import AdditionalInstance
from usefulgram.enums import Const

from dataclasses import dataclass


@dataclass()
class OneTextTestClass:
    text: str


@dataclass()
class DifferentTypeValuesTestClass:
    text: str
    number: int
    bool_value: bool
    none_value: None
    datetime_value: datetime
    date_value: date
    time_value: time


@dataclass()
class RecursionTestClass:
    reqursion_class: OneTextTestClass


test_date = datetime(year=1999, month=1, day=10, hour=3,
                     minute=30, second=59)

one_text_test_class = OneTextTestClass(text="text")
different_type_values_test_class = DifferentTypeValuesTestClass(
    text="text", number=1000, bool_value=True,
    none_value=None, datetime_value=test_date,
    date_value=test_date.date(),
    time_value=test_date.time()
)

str_current_datetime = test_date.strftime(Const.DATETIME_FORMAT)
str_current_date = test_date.date().strftime(Const.DATETIME_FORMAT)
str_current_time = test_date.time().strftime(Const.DATETIME_FORMAT)

different_type_values_test_class_output = (
    f"text&1000&1&&{str_current_datetime}&"
    f"{str_current_date}&{str_current_time}"
)


# The Bytes lenght checker is located in the CallbackData class
# so some functions there is may not working outside Additional test


class AdditionalTestCase(unittest.TestCase):
    @staticmethod
    def is_raise_value_exception(fun: Callable, *args, **kwargs) -> bool:
        try:
            fun(*args, **kwargs)
            return False

        except ValueError:
            return True

    def test_empty_additional(self):
        result = AdditionalInstance()

        self.assertTrue(result == "")

    def test_none_additional(self):
        result = AdditionalInstance(None)

        self.assertTrue(result == "")

    def test_one_text_additional(self):
        result = AdditionalInstance("text")

        self.assertTrue(result == "text")

    def test_some_text_additional(self):
        result = AdditionalInstance("text", "text", "text")

        self.assertTrue(result == "text&text&text")

    def test_different_type_additional(self):
        result = AdditionalInstance("text", 123, True, None)

        self.assertTrue(result == "text&123&1&")

    def test_one_text_class_based_additional(self):
        result = AdditionalInstance(one_text_test_class)

        self.assertTrue(result == "text")

    def test_different_type_class_based_additional(self):
        result = AdditionalInstance(different_type_values_test_class)

        self.assertTrue(result == different_type_values_test_class_output)

    def test_some_different_type_class_based_additional(self):
        result = AdditionalInstance(different_type_values_test_class, different_type_values_test_class,
                                    different_type_values_test_class, different_type_values_test_class)

        output = [f"{different_type_values_test_class_output}&" for _ in range(4)]
        str_output = "".join(output)[:-1]

        self.assertTrue(result == str_output)

    def test_recursion_class_error(self):
        example_class = RecursionTestClass(reqursion_class=one_text_test_class)

        result = self.is_raise_value_exception(AdditionalInstance, example_class)

        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
