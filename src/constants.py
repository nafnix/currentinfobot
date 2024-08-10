from enum import StrEnum, auto


class _NameEnum(StrEnum):
    @staticmethod
    def _generate_next_value_(name, *_args, **_kwargs) -> str:
        return name


class LogLevel(_NameEnum):
    TRACE = auto()
    DEBUG = auto()
    INFO = auto()
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


class Environment(_NameEnum):
    LOCAL = auto()
    PRODUCTION = auto()

    @property
    def is_local(self):
        return self == self.LOCAL

    @property
    def is_production(self):
        return self == self.PRODUCTION
