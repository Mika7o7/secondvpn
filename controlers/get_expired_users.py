from datetime import datetime
import logging

from core.api_client import APIClient
from config import MARZBAN_CONFIG

logger = logging.getLogger(__name__)

import re

def get_expired_clients():
    """Получает список клиентов с истекшей подпиской и временем, прошедшим с момента окончания"""
    try:
        api_client = APIClient(MARZBAN_CONFIG)
        data = api_client.get_expired_users(limit=100)
        users = data.get("users", [])

        results = []
        for user in users:
            username = user.get("username")
            note = user.get("note", "")
            tg_id = int(re.search(r"\d+", note).group()) if re.search(r"\d+", note) else 0
            expire_unix = user.get("expire")

            if not tg_id or not expire_unix:
                continue

            if expire_unix > 1e12:
                expire_unix = expire_unix / 1000

            expire_dt = datetime.fromtimestamp(expire_unix)

            results.append([
                tg_id,
                username,
                "expired",
                expire_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "-",
                None
            ])

        return results

    except Exception as e:
        logger.error(f"Error getting expired clients: {e}")
        return []
