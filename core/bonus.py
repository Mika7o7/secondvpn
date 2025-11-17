import sqlite3
import logging
from datetime import datetime, timedelta
from config import SUBSCRIPTION_CONFIG


logger = logging.getLogger(__name__)

def apply_bonus_days(tg_id: int):
    """При любой покупке/продлении — применяем накопленные бонусные дни"""
    with sqlite3.connect(SUBSCRIPTION_CONFIG['db_path']) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT bonus_days FROM clients WHERE tg_id = ?", (tg_id,))
        row = cursor.fetchone()
        if not row or row[0] <= 0:
            return 0
            
        bonus = row[0]
        new_end_date = (datetime.now() + timedelta(days=bonus)).strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            UPDATE clients 
            SET end_date = ?, 
                bonus_days = 0, 
                used_bonus_days = used_bonus_days + ?
            WHERE tg_id = ?
        """, (new_end_date, bonus, tg_id))
        conn.commit()
        
    logger.info(f"Applied {bonus} bonus days to user {tg_id}")
    return bonus