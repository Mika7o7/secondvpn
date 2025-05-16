from core.api_client import APIClient
from database import delete_client
import logging

logger = logging.getLogger(__name__)

def delete_inbound(tg_id, username):
    """Удаление пользователя из Marzban и базы"""
    try:
        api_client = APIClient()  # Предполагается, что конфигурация загружается автоматически
        api_client.delete(f"/api/user/{username}")
        delete_client(tg_id)
        logger.info(f"Deleted user {username} for tg_id {tg_id}")
    except Exception as e:
        logger.error(f"Failed to delete user {username} for tg_id {tg_id}: {str(e)}")
        raise