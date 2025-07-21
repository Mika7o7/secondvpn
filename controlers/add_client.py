from core.api_client import APIClient
from config import MARZBAN_CONFIG
import logging

logger = logging.getLogger(__name__)

def add_client(tg_id, name, xpiry_days=None, server_country=None):
    """Создаём нового клиента в Marzban и возвращаем VLESS-ссылки"""
    try:
        api_client = APIClient(MARZBAN_CONFIG)
        links, username = api_client.create_user(tg_id, name, xpiry_days)
        if not links:
            raise Exception("No VLESS links returned")
        logger.info(f"Created user {username} for tg_id {tg_id} with links: {links}")
        return links, username
    except Exception as e:
        logger.error(f"Failed to add client for user {tg_id}: {str(e)}")
        raise
