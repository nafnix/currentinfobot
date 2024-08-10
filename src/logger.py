import datetime
import inspect
import logging
import sys
from collections.abc import Callable
from functools import partial, wraps
from typing import ParamSpec, TypeVar, overload

from loguru import logger

from src.config import settings
from src.constants import LogLevel


logger.remove()


# ref: https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
class InterceptHandler(logging.Handler):
    @logger.catch(default=True, onerror=lambda _: sys.exit(1))
    def emit(self, record: logging.LogRecord) -> None:
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = logging.currentframe(), 0
        while frame and (
            depth == 0 or frame.f_code.co_filename == logging.__file__
        ):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# 替换根日志记录器的所有日志级别的 Handler
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)


# https://github.com/encode/uvicorn/issues/562
# 下面者几个因为不是使用根日志记录器的日志, 所以需要手动拦截
for log_name in ["uvicorn", "uvicorn.access", "fastapi"]:
    _logger = logging.getLogger(log_name)
    _logger.handlers = [InterceptHandler()]


LOG_FORMAT = (
    "<level>{level: <8}</level> | "
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<cyan>{name}</cyan>:"
    "<cyan>{function}</cyan>:"
    "<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

logger.add(sys.stdout, level=settings.LOG_LEVEL, format=LOG_FORMAT)


if settings.LOG_DIR:

    class _Rotator:
        """指定大小和时间更新日志文件"""

        def __init__(self, *, size):
            now = datetime.datetime.now()

            self._size_limit = size
            # 每晚 0 点更新
            self._time_limit = now.replace(hour=0, minute=0, second=0)
            if now >= self._time_limit:
                # The current time is already past the target time
                # so it would rotate already.
                # Add one day to prevent an immediate rotation.
                self._time_limit += datetime.timedelta(days=1)

        def should_rotate(self, message, file):
            file.seek(0, 2)
            if file.tell() + len(message) > self._size_limit:
                return True

            excess = (
                message.record["time"].timestamp()
                - self._time_limit.timestamp()
            )
            if excess >= 0:
                elapsed_days = datetime.timedelta(seconds=excess).days
                self._time_limit += datetime.timedelta(days=elapsed_days + 1)
                return True
            return False

    rotator = _Rotator(
        size=2e7  # 20MB
    )
    logger.add(
        settings.LOG_DIR,
        level=settings.LOG_LEVEL,
        format=LOG_FORMAT,
        rotation=rotator.should_rotate,
    )

_P = ParamSpec("_P")
_T = TypeVar("_T")


@overload
def log_fn(fn: Callable[_P, _T], *, level: LogLevel = settings.LOG_LEVEL): ...


@overload
def log_fn(
    fn: Callable[_P, _T] | None = None, *, level: LogLevel = settings.LOG_LEVEL
): ...


def log_fn(
    fn: Callable[_P, _T] | None = None, *, level: LogLevel = settings.LOG_LEVEL
):
    if fn is None:
        return partial(log_fn, level=level)

    @wraps(fn)
    async def wrapper(*args, **kwargs):
        def get_arguments_signature(sign: inspect.Signature) -> list[str]:
            # 绑定参数
            bound_args = sign.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # 获取参数和参数注释, 并转换为字符串
            result = []
            for key, value in bound_args.arguments.items():
                param_annotation = sign.parameters[key].annotation
                if param_annotation != inspect.Signature.empty:
                    key += f": {param_annotation}"

                value = f"'{value}'" if isinstance(value, str) else value
                result.append(f"{key} = {value}")

            return result

        # 获取函数签名
        signature = inspect.signature(fn)

        arguments = get_arguments_signature(signature)
        arguments_annotation = ", ".join(arguments)

        # 获取返回值注释, 并转换为字符串
        return_annotation = ""
        if signature.return_annotation != inspect.Signature.empty:
            return_annotation = f" -> {signature.return_annotation}"

        fn_name = fn.__name__
        fn_info = f"{fn_name}({arguments_annotation}){return_annotation}"

        logger.log(level, f"调用: {fn_info}")

        result = fn(*args, **kwargs)
        if inspect.iscoroutine(result):
            result = await result

        # 如果返回值是字符串, 就给返回值左右添加单引号
        result_value = f"'{result}'" if isinstance(result, str) else result

        logger.log(level, f"{fn_name} 结果: {result_value}")

        return result

    return wrapper
