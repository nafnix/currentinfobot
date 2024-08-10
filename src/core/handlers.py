from telegram import Update
from telegram.ext import (
    BaseHandler,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    TypeHandler,
)
from telegram.ext.filters import BaseFilter

from src.core.requests import TelegramCallbackRequest, TelegramRequest
from src.logger import logger


class Handlers(list[BaseHandler]):
    def handler_register(self, handler: BaseHandler):
        def callback_arg_transform(fn):
            # TODO: 可能需要允许 context 是可选参数。
            def wrapper(update: Update, context):
                if update.callback_query:
                    req_class = TelegramCallbackRequest
                else:
                    req_class = TelegramRequest

                return fn(req_class(update, context))

            return wrapper

        handler.callback = callback_arg_transform(handler.callback)
        self.append(handler)

    def on_command(self, command: str):
        def decorate(fn):
            h = CommandHandler(command, fn)
            logger.debug(f"注册命令: {command}\t{fn}")
            self.handler_register(h)

            return fn

        return decorate

    def on_callback(self, *ps):
        def decorate(fn):
            pattern = "^" + "&".join(rf"({p})\=?([^&=]*)" for p in ps)
            h = CallbackQueryHandler(fn, pattern)
            logger.debug(f"注册回调: {pattern}\t{fn}")
            self.handler_register(h)

            return fn

        return decorate

    def on_message(self, filters: BaseFilter | None):
        def decorate(fn):
            h = MessageHandler(filters, fn)
            logger.debug(f"注册消息处理: {filters!r}\t{fn}")
            self.handler_register(h)
            return fn

        return decorate

    def on_type(self, type_: type):
        def decorate(fn):
            h = TypeHandler(type_, fn)
            logger.debug(f"注册类型: {type_}\t{fn}")
            self.handler_register(h)

            return fn

        return decorate


class StateHandlers(Handlers):
    def __init__(self, name: str | int) -> None:
        """状态注册

        :param name: 状态名
        """

        self.name = name
        super().__init__()
