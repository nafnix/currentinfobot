from src.core.handlers import Handlers
from src.core.requests import TelegramRequest
from src.utils.telegram.text import inline_code


handlers = Handlers()


@handlers.on_command("start")
async def start(request: TelegramRequest):
    """获取当前对话的信息"""

    result = (
        f"chat id: {inline_code(request.chat_id)}\n"
        f"chat username: {inline_code(request.chat.username or '')}\n"
        f"chat title: {inline_code(request.chat.title or '')}\n"
        f"\n"
        f"user id: {inline_code(request.user_id)}\n"
        f"user username: {inline_code(request.user.username or '')}\n"
        f"user fullname: {inline_code(request.user.full_name)}\n"
        f"user system language: {inline_code(request.user.language_code)}\n"
    )

    await request.chat.send_message(result)
