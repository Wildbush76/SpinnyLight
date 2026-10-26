from functools import lru_cache

from pydantic_settings import BaseSettings


class LightClientSettings(BaseSettings):
    light_mac_address: str = "B0:A6:04:00:ED:6E"
    light_service_uuid: str = "2d60fead-9a7c-42b7-8878-41518bfec0a6"
    trigger_light_uuid: str = "63e613d6-3d8e-4d62-8ee8-82fe2baae72a"
    reconnect_interval: int = 100  # seconds


@lru_cache
def get_settings() -> LightClientSettings:
    return LightClientSettings()
