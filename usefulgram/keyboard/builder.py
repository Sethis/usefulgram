
from typing import Optional, Any, Union

from datetime import datetime, date, time

from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup)

from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from usefulgram.parsing.encode import CallbackData
from usefulgram.exceptions import (
    DifferentButtonsInMatrix,
    UnknownButtonType,
    NoOneButtonParamIsFilled)

from usefulgram.utils import autorepr


def check_buttons_type(button_instance: object, button_type: type):
    if not isinstance(button_instance, button_type):
        raise DifferentButtonsInMatrix


class Button:
    text: str
    prefix: Optional[str]
    url: Optional[str]
    additional: tuple[Union[str, int, bool, None, datetime,
                            date, time, object], ...]
    other: dict[str, Any]
    separator: str

    def __init__(
            self, text: Union[str, int],
            *args: Union[str, int, bool, None, datetime, date, time, object],
            prefix: Optional[str] = None,
            url: Optional[str] = None, separator: str = "/",
            **kwargs: dict[str, Any]
            ):

        prefix = self._get_prefix(prefix, args)

        if isinstance(text, int):
            text = str(text)

        if not any((prefix, url, kwargs)):
            raise NoOneButtonParamIsFilled

        self.text = text
        self.prefix = prefix
        self.url = url
        self.additional = args
        self.other = kwargs
        self.separator = separator

    def __repr__(self):
        return autorepr(self)

    @staticmethod
    def _get_prefix(
            prefix: Optional[str],
            args: tuple[Union[str, int, bool, None, datetime, date, time, object], ...]
    ) -> Optional[str]:

        if prefix is not None:
            return prefix

        for obj in args:
            result = obj.__getattribute__("prefix")

            if result is not None:
                return result

        return None

    def get_buttons(self) -> InlineKeyboardButton:
        if self.prefix is not None:
            callback_data = CallbackData(
                self.prefix, *self.additional,
                separator=self.separator)

        else:
            callback_data = None

        return InlineKeyboardButton(text=self.text, url=self.url,
                                    callback_data=callback_data,
                                    **self.other)


class ReplyButton:
    text: str
    other: dict[str, Any]

    def __init__(self, text: str, **kwargs):
        self.text = text
        self.other = kwargs

    def __repr__(self):
        return autorepr(self)

    def get_buttons(self) -> KeyboardButton:
        return KeyboardButton(text=self.text, **self.other)


class Row:
    buttons: Union[list[InlineKeyboardButton], list[KeyboardButton]]
    first_button_instance: Union[Button, ReplyButton]

    def __init__(self, *args: Union[ReplyButton, Button]):
        self.buttons = []

        first_button = args[0]

        self.first_button_instance = first_button

        for button in args:
            check_buttons_type(button, type(first_button))

            self.buttons.append(button.get_buttons())

    def __repr__(self):
        return autorepr(self)

    def get_rows(self) -> list[InlineKeyboardButton]:
        return self.buttons


class _Builder:
    @staticmethod
    def _get_builder(
            first_row_button_ins: Optional[Union[Button, ReplyButton]] = None,
            is_callback: Optional[bool] = None
    ) -> Union[InlineKeyboardBuilder, ReplyKeyboardBuilder]:

        if isinstance(first_row_button_ins, Button) or is_callback is True:
            return InlineKeyboardBuilder()

        if (isinstance(first_row_button_ins, ReplyButton)
                or is_callback is False):

            return ReplyKeyboardBuilder()

        raise UnknownButtonType

    def __call__(self, *rows: Row, adjust: Optional[int] = None,
                 is_callback: bool = True,
                 **kwargs) -> Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]:

        if len(rows) == 0:
            return self._get_builder(is_callback=is_callback).as_markup()

        first_row_button_instance = rows[0].first_button_instance

        builder = self._get_builder(first_row_button_instance)

        for row in rows:
            check_buttons_type(row.first_button_instance,
                               type(first_row_button_instance))

            builder.row(*row.get_rows())

        if adjust is not None:
            builder.adjust(adjust)

        return builder.as_markup(**kwargs)


Builder = _Builder()
