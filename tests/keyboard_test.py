

import unittest

from typing import Callable, Optional

from aiogram.types import (
    InlineKeyboardButton,
    KeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup)

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from usefulgram.keyboard.builder import (
    Button,
    ReplyButton,
    Row,
    Builder)

from usefulgram.parsing.encode import CallbackData
from usefulgram.filters import BasePydanticFilter


class PrefixTestData(BasePydanticFilter):
    prefix: Optional[str] = "some_prefix"


class KeyboardTestCase(unittest.TestCase):
    sample_url = "https://web.telegram.org/a/"

    @staticmethod
    def is_raise_value_exception(fun: Callable, *args, **kwargs) -> bool:
        try:
            fun(*args, **kwargs)
            return False

        except ValueError:
            return True

    def test_inline_button_without_arguments(self):
        result = self.is_raise_value_exception(Button, text="text")

        self.assertTrue(result)

    def test_inline_button_prefix(self):
        button = Button("text", prefix="prefix")

        self.assertTrue(button)

    def test_prefix_from_class(self):
        first_button = Button("text", PrefixTestData())
        second_button = Button("text", prefix="some_prefix")

        self.assertTrue(second_button.get_buttons() == first_button.get_buttons())

    def test_prefix_changing(self):
        first_button = Button("text", PrefixTestData(), prefix="another_prefix")
        second_button = Button("text", prefix="another_prefix")

        self.assertTrue(second_button.get_buttons() == first_button.get_buttons())

    def test_inline_button_get_button(self):
        button = Button("text", "other", "something", prefix="prefix")

        callback_data = CallbackData("prefix", "other", "something")
        aiogram_button = InlineKeyboardButton(text="text",
                                              callback_data=callback_data)

        self.assertTrue(button.get_buttons() == aiogram_button)

    def test_inline_url_button(self):
        button = Button("text", url=self.sample_url)

        aiogram_button = InlineKeyboardButton(
            text="text", url=self.sample_url
        )

        self.assertTrue(button.get_buttons() == aiogram_button)

    def test_inline_button_too_lenght(self):
        button = Button("text", prefix="prefix"*100)

        result = self.is_raise_value_exception(Row, button)

        self.assertTrue(result)

    def test_reply_button(self):
        button = ReplyButton("text")

        aiogram_button = KeyboardButton(text="text")

        self.assertTrue(button.get_buttons() == aiogram_button)

    def test_both_button_type_in_row(self):
        inline_button = Button("text", True, 1, prefix="prefix")
        reply_button = ReplyButton("text")

        result = self.is_raise_value_exception(Row, inline_button,
                                               reply_button)

        self.assertTrue(result)

    def test_inline_row(self):
        row = Row(
            Button("text", url="url"),
            Button("text", prefix="prefix"),
            Button("text", True, True, False, prefix="prefix")
        )

        self.assertTrue(row.get_rows())

    def test_reply_row(self):
        row = Row(
            ReplyButton("text"),
            ReplyButton("text"),
            ReplyButton("text")
        )

        self.assertTrue(row.get_rows())

    @staticmethod
    def _get_aiogram_reply_matrix() -> ReplyKeyboardMarkup:
        aiogram_builder = ReplyKeyboardBuilder()
        aiogram_builder.row(KeyboardButton(text="text1"),
                            KeyboardButton(text="text1"))

        aiogram_builder.row(KeyboardButton(text="text2"))

        return aiogram_builder.as_markup()

    def test_reply_matrix(self):
        builder = Builder(
            Row(
                ReplyButton("text1"),
                ReplyButton("text1")
            ),
            Row(
                ReplyButton("text2")
            )
        )

        aiogram_builder = ReplyKeyboardBuilder()
        aiogram_builder.row(KeyboardButton(text="text1"),
                            KeyboardButton(text="text1"))

        aiogram_builder.row(KeyboardButton(text="text2"))

        aiogram_matrix = aiogram_builder.as_markup()

        self.assertTrue(builder == aiogram_matrix)

    @staticmethod
    def _get_aiogram_inline_matrix() -> InlineKeyboardMarkup:
        aiogram_builder = InlineKeyboardBuilder()
        aiogram_builder.row(InlineKeyboardButton(
            text="text", callback_data=CallbackData("prefix", "other"))
        )

        aiogram_builder.row(
            InlineKeyboardButton(
                text="text2",
                callback_data=CallbackData("other_prefix", True)),

            InlineKeyboardButton(
                text="text3",
                callback_data=CallbackData("rest_prefix", 1)
            )

        )

        return aiogram_builder.as_markup()

    def test_inline_matrix(self):
        builder = Builder(
            Row(
                Button("text", "other", prefix="prefix")
            ),
            Row(
                Button("text2", True, prefix="other_prefix"),
                Button("text3", 1, prefix="rest_prefix")
            )
        )

        aiogram_matrix = self._get_aiogram_inline_matrix()

        self.assertTrue(builder == aiogram_matrix)

    def test_empty_inline_matrix(self):
        builder = Builder()
        aiogram_builder = InlineKeyboardBuilder().as_markup()

        self.assertTrue(builder == aiogram_builder)

    def test_empty_reply_matrix(self):
        builder = Builder(is_callback=False)
        aiogram_builder = ReplyKeyboardBuilder().as_markup()

        self.assertTrue(builder == aiogram_builder)


if __name__ == '__main__':
    unittest.main()
