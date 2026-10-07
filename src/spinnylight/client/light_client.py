import asyncio
from logging import getLogger

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakCharacteristicNotFoundError

from .light_client_settings import get_settings


class LightClient:
    def __init__(self):
        self._settings = get_settings()
        self._bleak_client = BleakClient(self._settings.light_mac_address)
        self._task: None | asyncio.Task = None
        self._logger = getLogger(LightClient.__name__)
        self._trigger = asyncio.Event()

    async def start(self) -> None:
        self._logger.info("Starting BLE Light Client")
        self._task = asyncio.create_task(self._run_server())

    async def _send_light_trigger(self, client: BleakClient) -> None:

        try:
            await client.write_gatt_char(self._settings.trigger_light_uuid, True, False)
        except BleakCharacteristicNotFoundError:
            self._logger.critical(
                "Failed to find characteristic uuid! -> ", exc_info=True
            )

    async def _connect_server(self) -> None:

        device = None
        while device is None:
            device = await BleakScanner.find_device_by_address(
                self._settings.light_mac_address
            )

        with BleakClient(device) as client:
            while await self._trigger.wait():
                await self._send_light_trigger(client)
                self._trigger.clear()

    async def _run_server(self) -> None:
        try:
            while True:
                await self._connect_server()

        except asyncio.CancelledError:
            self._logger.info("Stopping BLE Light Client")
            if self._bleak_client.is_connected:
                self._bleak_client.disconnect()
