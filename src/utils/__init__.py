from src.config import settings
from src.constants import Environment


def assert_local():
    assert settings.ENVIRONMENT == Environment.LOCAL, "仅可在本地环境下调用"  # noqa: S101
