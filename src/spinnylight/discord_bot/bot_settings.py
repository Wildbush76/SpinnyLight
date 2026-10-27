from functools import lru_cache


class BotSettings:
    dev: int = 704773768035172726


@lru_cache
def get_bot_settings() -> BotSettings:
    return BotSettings()
