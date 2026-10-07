from functools import lru_cache

from pydantic_settings import BaseSettings


class LightClientSettings(BaseSettings):
    light_mac_address: str = ""
    light_service_uuid: str = ""
    trigger_light_uuid: str = ""
    reconnect_interval: int = 100  # seconds


@lru_cache
def get_settings() -> LightClientSettings:
    return LightClientSettings()
