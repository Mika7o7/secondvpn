from core.api_client import APIClient
from database import get_client, set_client_disabled_at
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def disable_inbound(tg_id):
    """Отключение inbound клиента"""
    try:
        client = get_client(tg_id)
        if not client or not client[1]:
            raise Exception("Client or inbound_id not found")

        inbound_id = client[1]
        client_id = client[2]
        email = f"user_{tg_id}_{client_id}@example.com"
        expiry_time = int(datetime.strptime(client[4], "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
        port = client[5]
        private_key = client[6]
        public_key = client[7]


        # Записываем время отключения
        disabled_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        set_client_disabled_at(tg_id, disabled_at)

        logger.info(f"Disabled inbound {inbound_id} for user {tg_id}, disabled_at={disabled_at}")
        return disabled_at
    except Exception as e:
        logger.error(f"Failed to disable inbound for user {tg_id}: {str(e)}")
        raise