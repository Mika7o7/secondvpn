from core.api_client import APIClient
from config import MARZBAN_CONFIG
import logging

logger = logging.getLogger(__name__)

def add_client(tg_id: int, marzban_username: str, expiry_days: int = 3, is_trial: bool = False):
    """is_trial=True только для триала при регистрации"""
    api_client = APIClient(MARZBAN_CONFIG)
    return api_client.create_user(
        tg_id=tg_id,
        username=marzban_username,
        expiry_days=expiry_days,
        is_trial=is_trial
    )