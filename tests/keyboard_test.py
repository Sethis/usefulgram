

import unittest

from typing import Callable, Optional

from aiogram.types import (
    InlineKeyboardButton,
    KeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup)

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from usefulgram.keyboard import (
    Button,
    ReplyButton,
    Row,
    ReplyRow,
    Builder,
    ReplyBuilder
)

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

    def test_inline_button_prefix(self):
        button = Button("text", prefix="prefix")

        self.assertTrue(button)

    def test_prefix_from_class(self):
        first_button = Button("text", PrefixTestData())
        second_button = Button("text", prefix="some_prefix")

        self.assertTrue(second_button == first_button)

    def test_prefix_changing(self):
        first_button = Button("text", PrefixTestData(), prefix="another_prefix")
        second_button = Button("text", prefix="another_prefix")

        self.assertTrue(second_button == first_button)

    def test_inline_button_get_button(self):
        button = Button("text", "other", "something", prefix="prefix")

        callback_data = CallbackData("prefix", "other", "something")
        aiogram_button = InlineKeyboardButton(text="text",
                                              callback_data=callback_data)

        self.assertTrue(button.__dict__ == aiogram_button.__dict__)

    def test_inline_url_button(self):
        button = Button("text", url=self.sample_url)

        aiogram_button = InlineKeyboardButton(
            text="text", url=self.sample_url
        )

        self.assertTrue(button.__dict__ == aiogram_button.__dict__)

    def test_inline_button_too_lenght(self):
        try:
            Button("text", prefix="prefix"*100)

            self.assertFalse(True)

        except ValueError:
            self.assertTrue(True)

    def test_reply_button(self):
        button = ReplyButton("text")

        aiogram_button = KeyboardButton(text="text")

        self.assertTrue(button.__dict__ == aiogram_button.__dict__)

    def test_inline_row(self):
        row = Row(
            Button("text", url="url"),
            Button("text", prefix="prefix"),
            Button("text", True, True, False, prefix="prefix")
        )

        self.assertTrue(row)

    def test_reply_row(self):
        row = ReplyRow(
            ReplyButton("text"),
            ReplyButton("text"),
            ReplyButton("text")
        )

        self.assertTrue(row)

    @staticmethod
    def _get_aiogram_reply_matrix() -> ReplyKeyboardMarkup:
        aiogram_builder = ReplyKeyboardBuilder()
        aiogram_builder.row(KeyboardButton(text="text1"),
                            KeyboardButton(text="text1"))

        aiogram_builder.row(KeyboardButton(text="text2"))

        return aiogram_builder.as_markup()

    def test_reply_matrix(self):
        builder = ReplyBuilder(
            ReplyRow(
                ReplyButton("text1"),
                ReplyButton("text1")
            ),
            ReplyRow(
                ReplyButton("text2")
            )
        )

        aiogram_builder = ReplyKeyboardBuilder()
        aiogram_builder.row(KeyboardButton(text="text1"),
                            KeyboardButton(text="text1"))

        aiogram_builder.row(KeyboardButton(text="text2"))

        aiogram_matrix = aiogram_builder.as_markup()

        for row_index, row in enumerate(builder.keyboard):
            for btn_index, button in enumerate(row):
                aiogram_button = aiogram_matrix.keyboard[row_index][btn_index]

                self.assertTrue(button.__dict__ == aiogram_button.__dict__)

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

        for row_index, row in enumerate(builder.inline_keyboard):
            for btn_index, button in enumerate(row):
                aiogram_button = \
                   aiogram_matrix.inline_keyboard[row_index][btn_index]

                self.assertTrue(button.__dict__ == aiogram_button.__dict__)

    def test_empty_inline_matrix(self):
        builder = Builder()
        aiogram_builder = InlineKeyboardBuilder().as_markup()

        self.assertTrue(builder.inline_keyboard == aiogram_builder.inline_keyboard)

    def test_empty_reply_matrix(self):
        builder = ReplyBuilder()
        aiogram_builder = ReplyKeyboardBuilder().as_markup()

        self.assertTrue(builder.__dict__ == aiogram_builder.__dict__)

    def test_adjust(self):
        builder1 = ReplyBuilder(
            ReplyRow(ReplyButton("text"), ReplyButton("text")),
            ReplyRow(ReplyButton("text"), ReplyButton("text")),
            adjust=2
        )

        builder2 = ReplyBuilder(
            ReplyRow(ReplyButton("text"), ReplyButton("text")),
            ReplyRow(ReplyButton("text"), ReplyButton("text")),
        )

        print(builder1.keyboard)
        print(builder2.keyboard)

        return self.assertTrue(builder1 == builder2)

    def test_adjust_in_one_row(self):
        builder1 = ReplyBuilder(
            ReplyRow(ReplyButton("text"), ReplyButton("text"),
                     ReplyButton("text"), ReplyButton("text")),
            adjust=2
        )

        builder2 = ReplyBuilder(
            ReplyRow(ReplyButton("text"), ReplyButton("text")),
            ReplyRow(ReplyButton("text"), ReplyButton("text")),
        )

        print(builder1.keyboard)
        print(builder2.keyboard)

        return self.assertTrue(builder1 == builder2)




if __name__ == '__main__':
    unittest.main()
