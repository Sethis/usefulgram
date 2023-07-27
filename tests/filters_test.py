

import unittest

from typing import Optional

import asyncio

from aiogram.types import CallbackQuery
from aiogram import F

from usefulgram.keyboard import Button
from usefulgram.parsing.decode import DecodeCallbackData
from usefulgram.filters import (
    BasePydanticFilter,
    CallbackPrefixFilter,
    ItarationFilter
)


class SimpleData(BasePydanticFilter):
    value: Optional[str] = None
    number: Optional[int] = None


class StandartValueData(BasePydanticFilter):
    value: str = "some_value"


class StandartPrefixData(BasePydanticFilter):
    prefix: str = "information"


class ClickerData(BasePydanticFilter):
    prefix: str = "inforamation"
    value: Optional[int] = None


class FilterTestCase(unittest.TestCase):
    _test_callback: Optional[CallbackQuery] = None

    @staticmethod
    def _get_decoder(button: Button) -> DecodeCallbackData:
        callback_data = button.callback_data

        return DecodeCallbackData(callback_data)

    @staticmethod
    def _get_simple_test_decoder() -> DecodeCallbackData:
        button = Button(
            "text",
            SimpleData(
                prefix="some_prefix",
                value="some_value",
                number=1)
        )

        return FilterTestCase._get_decoder(button)

    @staticmethod
    def _get_params_test_decoder(**kwargs) -> DecodeCallbackData:
        button = Button("text", SimpleData(**kwargs))

        return FilterTestCase._get_decoder(button)

    def test_nothing_in_pydantic_filter(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = SimpleData()

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_only_prefix_in_pydantic_filter(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = SimpleData(prefix="some_prefix")

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_different_prefixes_in_pydantic_filter(self):
        first_btn = Button("text", SimpleData(prefix="some_prefix"))

        decoder = self._get_decoder(first_btn)

        filter_obj = SimpleData(prefix="another_prefix")

        result = filter_obj(self._test_callback, decoder)

        self.assertFalse(asyncio.run(result))

    def test_correct_different_prefixes_in_pydantic_filter(self):
        first_btn = Button("text", SimpleData(prefix="some_prefix"))

        decoder = self._get_decoder(first_btn)

        filter_obj = SimpleData(prefix="some_prefix", value=None)

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_standart_prefix_in_pydantic_filter(self):
        first_btn = Button("text", StandartPrefixData())

        decoder = self._get_decoder(first_btn)

        filter_obj = StandartPrefixData(prefix="information")

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_changing_standart_prefix_in_pydantic_filter(self):
        first_btn = Button("text", StandartPrefixData(prefix="another_prefix"))

        decoder = self._get_decoder(first_btn)

        filter_obj = StandartPrefixData(prefix="another_prefix")

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_standart_value_in_pydantic_filter(self):
        first_btn = Button("text", StandartValueData(prefix="some_prefix"))

        decoder = self._get_decoder(first_btn)

        filter_obj = StandartValueData(value="some_value")

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_changing_standart_value_in_pydantic_filter(self):
        first_btn = Button("text", StandartValueData(prefix="some_prefix",
                                                     value="another_prefix"))

        decoder = self._get_decoder(first_btn)

        filter_obj = StandartValueData(value="another_prefix")

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_only_value_in_pydantic_filter(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = SimpleData(value="some_value")

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_only_number_in_pydantic_filter(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = SimpleData(number=1)

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_all_values_in_pydantic_filter(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = SimpleData(prefix="some_prefix", value="some_value", number=1)

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_false_pydantic_filter(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = SimpleData(prefix="some_prefix", value="some_value", number=2)

        result = filter_obj(self._test_callback, decoder)

        self.assertFalse(asyncio.run(result))

    def test_pydantic_filter_returning_value(self):
        decoder = self._get_simple_test_decoder()

        values = {"prefix": "some_prefix", "value": "some_value", "number": 1}

        filter_obj = SimpleData(prefix="some_prefix")

        result = filter_obj(self._test_callback, decoder)

        result = asyncio.run(result)

        self.assertTrue(values == result)

    def test_pydantic_filter_example(self):
        first_btn = Button("-1", ClickerData(prefix="information"))

        decoder = self._get_decoder(first_btn)

        filter_obj = ClickerData(prefix="information")

        result = filter_obj(self._test_callback, decoder)

        result = asyncio.run(result)

        self.assertTrue(result)

    def test_one_params_magic_filter_in_pydantic(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = SimpleData().filter(F.prefix == "some_prefix")

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_many_params_magic_filter_in_pydantic(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = SimpleData().filter(F.prefix == "some_prefix", F.number > 0)

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_error_params_magic_filter_in_pydantic(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = SimpleData().filter(F.prefix == "some_prefix", F.number > 5)

        result = filter_obj(self._test_callback, decoder)

        self.assertFalse(asyncio.run(result))

    def test_prefix_filter(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = CallbackPrefixFilter(prefix="some_prefix")

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_false_prefix_filter(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = CallbackPrefixFilter(prefix="another_prefix")

        result = filter_obj(self._test_callback, decoder)

        self.assertFalse(asyncio.run(result))

    def test_prefix_iteration_filter(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = ItarationFilter()[0] == "some_prefix"

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_false_iteration_filter(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = ItarationFilter()[0] == "another_prefix"

        result = filter_obj(self._test_callback, decoder)

        self.assertFalse(asyncio.run(result))

    def test_nq_iteration_filter(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = ItarationFilter()[0] != "another_prefix"

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_value_iteration_filter(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = ItarationFilter()[1] == "some_value"

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_number_iteration_filter(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = ItarationFilter()[2] == "1"

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_lt_iteration_filter(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = ItarationFilter()[2] < 10

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_false_lt_iteration_filter(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = ItarationFilter()[2] < 0

        result = filter_obj(self._test_callback, decoder)

        self.assertFalse(asyncio.run(result))

    def test_gt_iteration_filter(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = ItarationFilter()[2] > 0

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_le_iteration_filter(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = ItarationFilter()[2] <= 1

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_ge_iteration_filter(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = ItarationFilter()[2] >= 0

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_one_params_magic_filter_in_iterable(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = ItarationFilter().filter(F[0] == "some_prefix")

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_many_params_magic_filter_in_iterable(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = ItarationFilter().filter(F[0] == "some_prefix", F[2] == "1")

        result = filter_obj(self._test_callback, decoder)

        self.assertTrue(asyncio.run(result))

    def test_error_params_magic_filter_in_iterable(self):
        decoder = self._get_simple_test_decoder()

        filter_obj = ItarationFilter().filter(F[0] == "some_prefix", F[2] == "2")

        result = filter_obj(self._test_callback, decoder)

        self.assertFalse(asyncio.run(result))
