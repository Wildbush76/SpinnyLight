import asyncio
import logging
from logging import getLogger

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakCharacteristicNotFoundError

from .light_client_settings import get_settings


class LightClient:
    def __init__(self):
        self._settings = get_settings()
        self._task: None | asyncio.Task = None
        self._logger = getLogger(LightClient.__name__)
        self._logger.setLevel(logging.INFO)
        self._trigger = asyncio.Event()

    def start(self) -> None:
        self._logger.info("Starting BLE Light Client")
        self._task = asyncio.ensure_future(self._run_client())

    def stop(self) -> None:
        self._task.cancel()

    def trigger(self) -> None:
        self._trigger.set()

    async def _send_light_trigger(self, client: BleakClient) -> None:

        try:
            await client.write_gatt_char(self._settings.trigger_light_uuid, True, False)
        except BleakCharacteristicNotFoundError:
            self._logger.critical(
                "Failed to find characteristic uuid! -> ", exc_info=True
            )

    async def _connect_client(self) -> None:
        device = None

        while device is None:
            self._logger.info(
                f"Attempting to connect to server @ {self._settings.light_mac_address}"
            )
            device = await BleakScanner.find_device_by_address(
                self._settings.light_mac_address
            )

        self._logger.info("Connected to the server!")

        async with BleakClient(device) as client:
            while await self._trigger.wait():
                await self._send_light_trigger(client)
                self._trigger.clear()

    async def _run_client(self) -> None:
        try:
            while True:
                await self._connect_client()

        except asyncio.CancelledError:
            self._logger.info("Stopping BLE Light Client")
