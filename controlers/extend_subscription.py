from core.api_client import APIClient
from database import get_client, update_client_end_date
from datetime import datetime, timedelta
from config import MARZBAN_CONFIG, SUBSCRIPTION_CONFIG
import uuid
import logging
import sqlite3


logger = logging.getLogger(__name__)
DB_PATH = SUBSCRIPTION_CONFIG['db_path']

def update_client_expiry(key_id: int, tg_id: int, username: str, months: int) -> str:
    """
    Продление конкретного ключа по его ID
    Берёт end_date именно из этого ключа, а не из общей таблицы clients
    """
    try:
        today = datetime.now()

        # 1. Берём текущую дату окончания ИЗ КОНКРЕТНОГО КЛЮЧА
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT end_date FROM user_keys 
                WHERE id = ? AND tg_id = ? AND marzban_username = ?
            """, (key_id, tg_id, username))
            row = c.fetchone()
            if not row or not row[0]:
                raise Exception("Не найдена дата окончания ключа")

            current_end_str = row[0]
            current_end_dt = datetime.strptime(current_end_str, "%Y-%m-%d %H:%M:%S")

        # 2. Если срок истёк — начинаем с сегодня, иначе — от текущей даты
        base_date = current_end_dt if current_end_dt > today else today

        # 3. Добавляем месяцы
        new_end_dt = base_date + timedelta(days=30 * months)
        new_end_date = new_end_dt.strftime("%Y-%m-%d %H:%M:%S")
        new_timestamp = int(new_end_dt.timestamp())

        # 4. Обновляем в Marzban
        api_client = APIClient(MARZBAN_CONFIG)
        user_data = {
            "username": username,
            "proxies": {
                "vless": {
                    "id": str(uuid.uuid4()),
                    "flow": "xtls-rprx-vision"
                }
            },
            "inbounds": {"vless": ["VLESS TCP REALITY"]},
            "expire": new_timestamp,
            "data_limit": 0,
            "data_limit_reset_strategy": "no_reset",
            "status": "active",
            "note": f"Extended for tg_id {tg_id}",
            "on_hold_expire_duration": None
        }
        api_client.update_user(username, user_data)

        # 5. Обновляем дату в ЭТОМ КОНКРЕТНОМ КЛЮЧЕ
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE user_keys 
                SET end_date = ? 
                WHERE id = ? AND tg_id = ?
            """, (new_end_date, key_id, tg_id))
            conn.commit()

        logger.info(f"Продлён ключ id={key_id} ({username}): {base_date.strftime('%Y-%m-%d')} → {new_end_date}")
        return new_end_date

    except Exception as e:
        logger.error(f"Ошибка продления ключа {key_id}: {e}")
        raise