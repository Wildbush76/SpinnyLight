import logging

from fastapi import APIRouter

_logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/subscriptions", status_code=200)
def subscriptions(data: dict):
    pass
