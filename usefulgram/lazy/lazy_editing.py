

from typing import Optional
from datetime import datetime, timedelta

import asyncio

from contextlib import suppress

from aiogram.types import (
    CallbackQuery,
    Message,
    InputMediaPhoto,
    InputMediaVideo,
    FSInputFile,
    InlineKeyboardMarkup,
    UNSET
)
from aiogram.enums.chat_type import ChatType

from aiogram.exceptions import TelegramBadRequest

from usefulgram.enums import Const


class LazyEditing:
    callback: CallbackQuery

    def __init__(self, callback: CallbackQuery):
        self.callback = callback

    @staticmethod
    def _get_text_by_caption(
            text: Optional[str] = None,
            caption: Optional[str] = None
    ) -> Optional[str]:
        if text is None or caption is not None:
            return caption

        return text

    @staticmethod
    def _check_data_changes(
            message: Message,
            text: Optional[str] = None,
            reply_markup: Optional[InlineKeyboardMarkup] = None,
            video: Optional[FSInputFile] = None,
            photo: Optional[FSInputFile] = None) -> bool:

        if message.text != text:
            return True

        if message.reply_markup != reply_markup:
            return True

        if message.video != video:
            return True

        if message.photo != photo:
            return True

        return False

    @staticmethod
    def _check_can_edit(callback: CallbackQuery) -> bool:
        if callback.message.chat.type == ChatType.CHANNEL:
            return True

        message_date = callback.message.date

        current = datetime.now(tz=message_date.tzinfo)
        const_delta = timedelta(hours=Const.send_message_delta)

        return current - message_date < const_delta

    @staticmethod
    async def _send_message(
            callback: CallbackQuery, text: Optional[str] = None,
            photo: Optional[FSInputFile] = None,
            video: Optional[FSInputFile] = None,
            reply_markup: Optional[InlineKeyboardMarkup] = None,
            parse_mode: Optional[str] = UNSET,
            disable_web_page_preview: bool = False):

        if photo is not None:
            return await callback.message.answer_photo(
                photo, caption=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview
            )

        if video is not None:
            return await callback.message.answer_video(
                video, caption=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview
            )

        text = LazyEditing._get_message_text(text, callback)

        return await callback.message.answer(
            text=text, reply_markup=reply_markup,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview
        )

    async def _check_message_media(
            self,
            callback: CallbackQuery, text: Optional[str] = None,
            photo: Optional[InputMediaPhoto] = None,
            video: Optional[InputMediaVideo] = None,
            reply_markup: Optional[InlineKeyboardMarkup] = None,
            parse_mode: Optional[str] = UNSET,
            disable_web_page_preview: bool = False) -> bool:

        message_has_photo_or_video = callback.message.photo \
                                     or callback.message.video

        if photo and not message_has_photo_or_video:
            await self._send_message(
                callback, text, photo, reply_markup=reply_markup,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview
            )

            return False

        elif video and not message_has_photo_or_video:
            await self._send_message(
                callback, text, video=video, reply_markup=reply_markup,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview
            )

            return False

        return True

    @staticmethod
    async def _edit_message(
            callback: CallbackQuery, text: Optional[str] = None,
            photo: Optional[FSInputFile] = None,
            video: Optional[FSInputFile] = None,
            reply_markup: Optional[InlineKeyboardMarkup] = None,
            parse_mode: Optional[str] = UNSET,
            disable_web_page_preview: bool = False):

        if photo or video:
            if photo:
                media = InputMediaPhoto(media=photo, caption=text)

            else:
                media = InputMediaVideo(media=video, caption=text)

            return await callback.message.edit_media(
                media=media, reply_markup=reply_markup,
                parse_mode=parse_mode
            )

        if text is None:
            return await callback.message.edit_reply_markup(
                text=text, reply_markup=reply_markup,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview
            )

        return await callback.message.edit_text(
            text=text, reply_markup=reply_markup,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview
        )

    @staticmethod
    async def _auto_callback_answer(
            callback: CallbackQuery,
            autoanswer: bool = True,
            answer_text: Optional[str] = None,
            answer_show_alert: bool = False
    ):
        if autoanswer:
            return await callback.answer(
                text=answer_text,
                show_alert=answer_show_alert
            )

    async def _edit_message_check(
            self,
            callback: CallbackQuery, text: Optional[str] = None,
            photo: Optional[FSInputFile] = None,
            video: Optional[FSInputFile] = None,
            reply_markup: Optional[InlineKeyboardMarkup] = None,
            parse_mode: Optional[str] = UNSET,
            disable_web_page_preview: bool = False
    ) -> bool:

        if not self._check_data_changes(callback.message, text,
                                        reply_markup, video, photo):
            return False

        check_result = await self._check_message_media(
            callback=callback, text=text,
            photo=photo, video=video,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview
        )

        if check_result is False:
            return False

        return True

    @staticmethod
    def _get_message_text(text: Optional[str], callback: CallbackQuery):
        if text is None:
            return callback.message.text

        return text

    async def edit(self,
                   text: Optional[str] = None,
                   photo: Optional[FSInputFile] = None,
                   video: Optional[FSInputFile] = None,
                   reply_markup: Optional[InlineKeyboardMarkup] = None,
                   parse_mode: Optional[str] = UNSET,
                   disable_web_page_preview: bool = False,
                   answer_text: Optional[str] = None,
                   answer_show_alert: bool = False,
                   autoanswer: bool = True
                   ):

        if self._check_can_edit(self.callback):
            edit_check_result = await self._edit_message_check(
                    callback=self.callback,
                    text=text,
                    photo=photo,
                    video=video,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                    disable_web_page_preview=disable_web_page_preview
                )

            if not edit_check_result:
                return await self._auto_callback_answer(
                    callback=self.callback, autoanswer=autoanswer,
                    answer_text=answer_text,
                    answer_show_alert=answer_show_alert)

            with suppress(TelegramBadRequest):
                await self._edit_message(
                    callback=self.callback,
                    text=text,
                    photo=photo,
                    video=video,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                    disable_web_page_preview=disable_web_page_preview,
                )

                await asyncio.sleep(Const.seconds_between_operation)

                return await self._auto_callback_answer(
                    callback=self.callback, autoanswer=autoanswer,
                    answer_text=answer_text,
                    answer_show_alert=answer_show_alert)

            await asyncio.sleep(Const.SECONDS_WAIT_AFTER_ERROR_EDIT)

        await self._send_message(
            callback=self.callback,
            text=text,
            photo=photo,
            video=video,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
        )

        await self._auto_callback_answer(
            callback=self.callback, autoanswer=autoanswer,
            answer_text=answer_text,
            answer_show_alert=answer_show_alert)
