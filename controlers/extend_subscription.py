from core.api_client import APIClient
from database import get_client, update_client_end_date
from datetime import datetime, timedelta
from config import MARZBAN_CONFIG
import uuid
import logging

logger = logging.getLogger(__name__)

def update_client_expiry(tg_id, username, months):
    """Продление подписки клиента через Marzban API"""
    try:
        client = get_client(tg_id)
        if not client or not client[3]:
            raise Exception("Client or end_date not found")

        # Вычисляем новую дату окончания
        current_end_date = datetime.strptime(client[3], "%Y-%m-%d %H:%M:%S")
        new_end_date_dt = current_end_date + timedelta(days=30 * months)
        new_end_date = new_end_date_dt.strftime("%Y-%m-%d %H:%M:%S")
        new_expiry_time = int(new_end_date_dt.timestamp())

        # Обновляем пользователя в Marzban
        api_client = APIClient(MARZBAN_CONFIG)
        user_data = {
            "username": username,
            "proxies": {
                "vless": {
                    "id": str(uuid.uuid4()),  # Новый ID для безопасности
                    "flow": "xtls-rprx-vision"
                }
            },
            "inbounds": {
                "vless": ["VLESS TCP REALITY"]
            },
            "expire": new_expiry_time,
            "data_limit": 0,
            "data_limit_reset_strategy": "no_reset",
            "status": "active",
            "note": f"Extended for tg_id {tg_id}",
            "on_hold_expire_duration": None
        }
        api_client.update_user(username, user_data)

        # Обновляем базу данных
        update_client_end_date(tg_id, new_end_date)

        logger.info(f"Extended subscription for user {tg_id} (username: {username}) for {months} months until {new_end_date}")
        return new_end_date
    except Exception as e:
        logger.error(f"Failed to extend subscription for user {tg_id}: {str(e)}")
        raise