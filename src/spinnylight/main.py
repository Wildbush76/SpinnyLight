import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .client.light_client import get_light_client
from .router import router


def _setup_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    log_format = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    _console_handler = logging.StreamHandler(sys.stdout)
    _console_handler.setFormatter(log_format)
    root_logger.addHandler(_console_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _setup_logger()
    client = get_light_client()
    client.start()
    yield
    client.stop()


app = FastAPI(lifespan=lifespan)
app.include_router(router=router.router)
