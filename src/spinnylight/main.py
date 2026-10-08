import asyncio
import logging
import sys

from .client.light_client import LightClient


def _setup_logger():
    logging.basicConfig(level=logging.INFO)
    root_logger = logging.getLogger()

    log_format = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    _console_handler = logging.StreamHandler(sys.stdout)
    _console_handler.setFormatter(log_format)

    root_logger.addHandler(_console_handler)


async def _test_BLE():
    _setup_logger()

    client = LightClient()
    client.start()

    while True:
        _input = await asyncio.to_thread(input, "Trigger it? (Just press enter)\n")
        if _input == "exit":
            break

        client.trigger()

    # client.stop()


def test_BLE():
    asyncio.run(_test_BLE())
