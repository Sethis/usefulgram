

import asyncio

from typing import Optional, Union
from datetime import datetime, timedelta
import pytz

from aiogram.types import (
    CallbackQuery,
    Message,
    FSInputFile,
    InlineKeyboardMarkup,
    UNSET_PARSE_MODE,
)

from aiogram import Bot
from aiogram.enums.chat_type import ChatType

from usefulgram.enums import Const
from usefulgram.exceptions import MessageTooOld
from usefulgram.lazy.editor import MessageEditor
from usefulgram.lazy.sender import MessageSender


class LazyEditing:
    callback: CallbackQuery
    bot: Bot
    stable: bool

    def __init__(self, callback: CallbackQuery, bot: Bot, stable: bool = False):
        self.callback = callback
        self.bot = bot
        self.stable = stable

    @staticmethod
    def _get_text_by_caption(
            text: Optional[str],
            caption: Optional[str]
    ) -> Optional[str]:

        if text is None or caption is not None:
            return caption

        return text

    @staticmethod
    def _get_message_text(text: Optional[str], message: Message) -> Optional[str]:
        if text is None:
            return message.text

        return text

    @staticmethod
    def _get_data_changes_status(
            message: Message,
            text: Optional[str],
            reply_markup: Optional[InlineKeyboardMarkup],
            video: Optional[FSInputFile],
            photo: Optional[FSInputFile]) -> bool:

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
    def _get_time_between_current_and_message(
            message_date: datetime
    ) -> timedelta:

        current = datetime.now(tz=pytz.UTC)

        return current - message_date

    @staticmethod
    def _get_time_allowed_edit_status(message: Message) -> bool:
        const_delta = timedelta(hours=Const.ALLOW_EDITING_DELTA)

        delta = LazyEditing._get_time_between_current_and_message(
            message.date
        )

        return delta < const_delta

    @staticmethod
    def _get_message_in_chat_status(message: Message) -> bool:
        if message.chat.type == ChatType.CHANNEL:
            return True

        return False

    @staticmethod
    def _get_message_media_is_correct_status(
            message: Message,
            photo: Optional[FSInputFile],
            video: Optional[FSInputFile]
    ) -> bool:

        message_has_photo_or_video = message.photo or message.video

        if photo and not message_has_photo_or_video:
            return False

        elif video and not message_has_photo_or_video:
            return False

        return True

    def _get_bot_allow_edit_status(
            self,
            message: Message,
            photo: Optional[FSInputFile],
            video: Optional[FSInputFile],
    ) -> bool:

        if self._get_message_in_chat_status(message):
            return True

        if not self._get_time_allowed_edit_status(message):
            return False

        if not self._get_message_media_is_correct_status(
            message=message, photo=photo, video=video
        ):
            return False

        return True

    @staticmethod
    async def _auto_callback_answer(
            bot: Bot,
            callback_id: str,
            autoanswer: bool = True,
            answer_text: Optional[str] = None,
            answer_show_alert: bool = False
    ) -> Optional[bool]:

        if not autoanswer:
            return None

        return await bot.answer_callback_query(
            callback_query_id=callback_id,
            text=answer_text,
            show_alert=answer_show_alert
        )

    @staticmethod
    async def _send_or_edit(
            bot: Bot,
            can_edit: bool,
            message: Message,
            text: Optional[str],
            photo: Optional[FSInputFile],
            video: Optional[FSInputFile],
            reply_markup: Optional[InlineKeyboardMarkup],
            parse_mode: Union[str],
            disable_web_page_preview: bool,
    ) -> Union[Message, bool]:

        if not can_edit:
            text = LazyEditing._get_message_text(text, message=message)

            return await MessageSender.send(
                bot=bot,
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                text=text,
                photo=photo,
                video=video,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview
            )

        return await MessageEditor.edit(
            bot=bot,
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=text,
            photo=photo,
            video=video,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview
        )

    def _get_can_edit_status(
            self,
            message: Message,
            photo: Optional[FSInputFile],
            video: Optional[FSInputFile],
    ) -> bool:

        if message is None:
            return False

        if not self._get_bot_allow_edit_status(
                message=message,
                photo=photo,
                video=video
        ):
            return False

        return True

    @staticmethod
    def _get_stable_wait_time(message: Message) -> float:
        if message.edit_date:
            dt = datetime.fromtimestamp(message.edit_date, tz=pytz.UTC)

            delta = LazyEditing._get_time_between_current_and_message(
                message_date=dt
            )
        else:
            delta = LazyEditing._get_time_between_current_and_message(
                message_date=message.date
            )

        total_seconds = delta.total_seconds()

        wait_time = Const.STABLE_WAIT_TIME_SECONDS - total_seconds
        return round(wait_time, 3)

    async def edit(
            self,
            text: Optional[str] = None,
            photo: Optional[FSInputFile] = None,
            video: Optional[FSInputFile] = None,
            reply_markup: Optional[InlineKeyboardMarkup] = None,
            parse_mode: Union[str] = UNSET_PARSE_MODE,
            disable_web_page_preview: bool = False,
            answer_text: Optional[str] = None,
            answer_show_alert: bool = False,
            autoanswer: bool = True
    ) -> Union[Message, bool]:

        callback = self.callback
        message = callback.message

        if message is None:
            await callback.answer("Message too old")

            raise MessageTooOld

        if self.stable:
            await asyncio.sleep(self._get_stable_wait_time(message))

        if not self._get_data_changes_status(
                message=message,
                text=text,
                reply_markup=reply_markup,
                video=video,
                photo=photo
        ):
            return message

        can_edit = self._get_can_edit_status(
            message=message,
            photo=photo,
            video=video,
        )

        result = await self._send_or_edit(
            bot=self.bot,
            can_edit=can_edit,
            message=message,
            text=text,
            photo=photo,
            video=video,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
        )

        await asyncio.sleep(Const.SECONDS_BETWEEN_OPERATION)

        await self._auto_callback_answer(
            bot=self.bot,
            callback_id=callback.id,
            autoanswer=autoanswer,
            answer_text=answer_text,
            answer_show_alert=answer_show_alert
        )

        return result
