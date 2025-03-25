from fastapi import APIRouter

from custom_logging import config_logging

config_logging()
reports_router = APIRouter()
