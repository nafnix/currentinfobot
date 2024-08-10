from functools import partial
from typing import Any, Final

from telegram.constants import ParseMode
from telegram.helpers import escape_markdown

from src.config import settings
from src.logger import logger


IS_HTML: Final = settings.PARSE_MODE == ParseMode.HTML


def delete(text: Any):
    return f"<del>{text}</del>" if IS_HTML else f"~~{text}~~"


def inline_code(text: Any):
    return f"<code>{text}</code>" if IS_HTML else f"`{text}`"


def bold(text: Any):
    return f"<b>{text}</b>" if IS_HTML else f"**{text}**"


def italic(text: Any):
    return f"<i>{text}</i>" if IS_HTML else f"*{text}*"


def underline(text: Any):
    if IS_HTML:
        return f"<u>{text}</u>"

    logger.warning(
        f"尝试将 `{text}` 转为带下划线格式的文本失败。"
        "非 HTML 格式无法发送带下划线的文本。"
    )
    return text


escape_markdown = partial(escape_markdown, version=2)


def escape(text: str) -> str:
    return text if IS_HTML else escape_markdown(text)
