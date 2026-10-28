import asyncio
from functools import lru_cache
from logging import DEBUG, getLogger

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from bleak.exc import BleakCharacteristicNotFoundError

from .light_client_settings import get_settings


class LightClient:
    def __init__(self):
        self._settings = get_settings()
        self._logger = getLogger(LightClient.__name__)
        self._logger.setLevel(DEBUG)
        self._trigger = asyncio.Event()
        self._scanner = BleakScanner(self._bleak_detection)
        self._connection: asyncio.Task | None = None

    async def _bleak_detection(
        self, device: BLEDevice, advertisement: AdvertisementData
    ):
        if device.address != self._settings.light_mac_address:
            return
        self._scanner.stop()
        self._logger.debug("Device found, connecting")
        self._connection = asyncio.create_task(self._connect(device))

    def start(self) -> None:
        asyncio.create_task(self._scanner.start())

    def stop(self) -> None:
        self._logger.debug("stopping light client")
        asyncio.create_task(self._scanner.stop())

        if self._connection is not None:
            self._connection.cancel()

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

    def _disconnect(self, client: BleakClient):
        self._logger.warning("Client Disconnected!")
        self.start()

    async def _connect(self, device: BLEDevice):
        async with BleakClient(
            device, disconnected_callback=self._disconnect
        ) as client:
            while await self._trigger.wait():
                await self._send_light_trigger(client)
                self._trigger.clear()


@lru_cache
def get_light_client() -> LightClient:
    return LightClient()
