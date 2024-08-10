import re
from collections import UserDict
from dataclasses import dataclass

from telegram import Update
from telegram.ext import ContextTypes


@dataclass
class TelegramBaseRequest:
    update: Update
    context: ContextTypes


class TelegramRequest(TelegramBaseRequest):
    @property
    def user(self):
        """telegram user"""

        assert self.update.effective_user, "此 handle 不存在用户"  # noqa: S101
        return self.update.effective_user

    @property
    def user_id(self):
        """telegram user id"""
        return self.user.id

    @property
    def chat(self):
        """telegram chat"""
        assert self.update.effective_chat, "此 handle 不存在 chat"  # noqa: S101
        return self.update.effective_chat

    @property
    def chat_id(self):
        """telegram chat id"""
        return self.chat.id

    @property
    def message(self):
        """telegram message"""
        assert self.update.effective_message, "此 handle 不存在 message"  # noqa: S101
        return self.update.effective_message


class CallbackSearchData(UserDict):
    _p = re.compile(r"[\?&]*((?P<key>[^=]+)=(?P<value>[^&]+))")

    def __init__(self, search_string: str) -> None:
        self.data = {
            i.group("key"): i.group("value")
            for i in self._p.finditer(search_string)
        }

    @property
    def page_or_none(self) -> int | None:
        result = self.data.get("page")
        if result is not None:
            return int(result)

        return None

    @property
    def page(self) -> int:
        result = self.page_or_none
        assert result, "无效的页参数"  # noqa: S101

        return result


class TelegramCallbackRequest(TelegramRequest):
    @property
    def query(self):
        assert self.update.callback_query, "此 handle 不存在 callback_query"  # noqa: S101

        return self.update.callback_query

    @property
    def callback_content(self):
        assert self.query.data, "此 handle 不存在 callback_data"  # noqa: S101

        return self.query.data

    @property
    def callback_data(self):
        return CallbackSearchData(self.callback_content)
