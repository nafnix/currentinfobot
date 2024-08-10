import asyncio
from typing import Any, Callable, Coroutine

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, Defaults

from src.config import settings

from .handlers import Handlers


class App:
    def __init__(
        self,
        *,
        backgrounds: list[Callable[[Application], Coroutine[Any, Any, Any]]]
        | None = None,
    ) -> None:
        self.base = (
            Application.builder()
            .token(settings.TOKEN)
            .defaults(Defaults(ParseMode.HTML))
            .build()
        )
        self._backgrounds: list[asyncio.Task] = []

        async def post_init(app: Application):
            if backgrounds:
                self._backgrounds.extend(
                    asyncio.create_task(i(app)) for i in backgrounds
                )

        async def post_shutdown(_: Application):
            for task in self._backgrounds:
                task.cancel()

        self.base.post_init = post_init
        self.base.post_shutdown = post_shutdown

        self.bot = self.base.bot

    def include_handlers(self, handlers: Handlers, group: int = 0):
        self.base.add_handlers(handlers, group)

    def run(self):
        self.base.run_polling(
            allowed_updates=[Update.CALLBACK_QUERY, Update.MESSAGE]
        )
