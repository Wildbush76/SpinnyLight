import asyncio
from functools import lru_cache
from logging import DEBUG, getLogger

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakCharacteristicNotFoundError

from .light_client_settings import get_settings


class LightClient:
    def __init__(self):
        self._settings = get_settings()
        self._task: None | asyncio.Task = None
        self._logger = getLogger(LightClient.__name__)
        self._logger.setLevel(DEBUG)
        self._trigger = asyncio.Event()

    def start(self) -> None:
        self._task = asyncio.create_task(self._run_client())

    def stop(self) -> None:
        self._task.cancel()

    def trigger(self) -> None:
        self._logger.debug("Triggering Light!")
        self._trigger.set()

    async def _send_light_trigger(self, client: BleakClient) -> None:
        try:
            await client.write_gatt_char(
                self._settings.trigger_light_uuid, bytes([True]), True
            )
            self._logger.debug("Successfully sent trigger")
        except BleakCharacteristicNotFoundError:
            self._logger.critical(
                "Failed to find characteristic uuid! -> ", exc_info=True
            )

    async def _connect_client(self) -> None:
        device = None

        while device is None:
            self._logger.debug(
                f"Attempting to connect to server @ {self._settings.light_mac_address}"
            )
            device = await BleakScanner.find_device_by_address(
                self._settings.light_mac_address
            )

        self._logger.debug("Connected to the server!")

        async with BleakClient(device) as client:
            while await self._trigger.wait():
                await self._send_light_trigger(client)
                self._trigger.clear()

    async def _run_client(self) -> None:
        self._logger.debug("Starting BLE light client")
        try:
            while True:
                await self._connect_client()

        except asyncio.CancelledError:
            self._logger.debug("Stopping BLE Light Client")


@lru_cache
def get_light_client() -> LightClient:
    return LightClient()
