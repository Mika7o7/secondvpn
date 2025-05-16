import sqlite3
import logging
from datetime import datetime, timedelta
from config import SUBSCRIPTION_CONFIG

logger = logging.getLogger(__name__)

def init_db():
    """Инициализация базы данных"""
    try:
        with sqlite3.connect(SUBSCRIPTION_CONFIG['db_path']) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    tg_id INTEGER PRIMARY KEY,
                    username TEXT,
                    payment_status TEXT,
                    end_date TEXT,
                    server_country TEXT,
                    disabled_at TEXT,
                    spend TEXT
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_end_date ON clients (end_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_disabled_at ON clients (disabled_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_status ON clients (payment_status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_spend ON clients (spend)")
            conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def get_client(tg_id):
    """Получение клиента по tg_id"""
    try:
        with sqlite3.connect(SUBSCRIPTION_CONFIG['db_path']) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tg_id, username, payment_status, end_date, server_country, disabled_at
                FROM clients WHERE tg_id = ?
            """, (tg_id,))
            return cursor.fetchone()
    except Exception as e:
        logger.error(f"Failed to get client {tg_id}: {e}")
        return None

def get_expired_clients():
    """Получение клиентов с истёкшей подпиской"""
    try:
        with sqlite3.connect(SUBSCRIPTION_CONFIG['db_path']) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tg_id, username, payment_status, end_date, server_country, disabled_at
                FROM clients WHERE end_date <= ?
            """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Failed to get expired clients: {e}")
        return []

def create_client(tg_id, username, server_country):
    """Создание нового клиента"""
    end_date = (datetime.now() + timedelta(days=SUBSCRIPTION_CONFIG['trial_days'])).strftime("%Y-%m-%d %H:%M:%S")
    try:
        with sqlite3.connect(SUBSCRIPTION_CONFIG['db_path']) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tg_id FROM clients WHERE tg_id = ?", (tg_id,))
            if cursor.fetchone():
                logger.warning(f"Client with tg_id {tg_id} already exists, skipping creation")
                return
            cursor.execute("""
                INSERT INTO clients (tg_id, username, payment_status, end_date, server_country, disabled_at, spend)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tg_id, username, "trial", end_date, server_country, None, "0"))
            conn.commit()
        logger.info(f"Created client {tg_id} with username {username} in country {server_country}")
    except Exception as e:
        logger.error(f"Failed to create client {tg_id}: {e}")
        raise

def update_client_status(tg_id, status):
    """Обновление статуса оплаты"""
    try:
        with sqlite3.connect(SUBSCRIPTION_CONFIG['db_path']) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE clients
                SET payment_status = ?, disabled_at = NULL
                WHERE tg_id = ?
            """, (status, tg_id))
            conn.commit()
        logger.info(f"Updated payment_status for client {tg_id} to {status}")
    except Exception as e:
        logger.error(f"Failed to update payment_status for client {tg_id}: {e}")
        raise

def update_client_end_date(tg_id, end_date):
    """Обновление даты окончания подписки"""
    try:
        with sqlite3.connect(SUBSCRIPTION_CONFIG['db_path']) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE clients
                SET end_date = ?, disabled_at = NULL
                WHERE tg_id = ?
            """, (end_date, tg_id))
            conn.commit()
        logger.info(f"Updated end_date for client {tg_id} to {end_date}")
    except Exception as e:
        logger.error(f"Failed to update end_date for client {tg_id}: {e}")
        raise

def update_client_spend(tg_id: int, amount: int):
    """Обновление суммы, которую потратил клиент"""
    try:
        with sqlite3.connect(SUBSCRIPTION_CONFIG['db_path']) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT spend FROM clients WHERE tg_id = ?", (tg_id,))
            row = cursor.fetchone()
            previous_spend = int(row[0]) if row and row[0] else 0
            new_spend = previous_spend + amount
            cursor.execute("UPDATE clients SET spend = ? WHERE tg_id = ?", (str(new_spend), tg_id))
            conn.commit()
            logger.info(f"Updated spend for {tg_id}: {previous_spend} -> {new_spend}")
    except Exception as e:
        logger.error(f"Failed to update spend for client {tg_id}: {e}")
        raise

def set_client_disabled_at(tg_id, disabled_at):
    """Установка времени отключения клиента"""
    try:
        with sqlite3.connect(SUBSCRIPTION_CONFIG['db_path']) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE clients SET disabled_at = ? WHERE tg_id = ?", (disabled_at, tg_id))
            conn.commit()
        logger.info(f"Set disabled_at for client {tg_id} to {disabled_at}")
    except Exception as e:
        logger.error(f"Failed to set disabled_at for client {tg_id}: {e}")
        raise

def delete_client(tg_id):
    """Удаление клиента из базы"""
    try:
        with sqlite3.connect(SUBSCRIPTION_CONFIG['db_path']) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients WHERE tg_id = ?", (tg_id,))
            conn.commit()
        logger.info(f"Deleted client {tg_id} from database")
    except Exception as e:
        logger.error(f"Failed to delete client {tg_id}: {e}")
        raise

def get_users_count():
    """Получение общего количества пользователей"""
    try:
        with sqlite3.connect(SUBSCRIPTION_CONFIG['db_path']) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM clients")
            count = cursor.fetchone()[0]
            logger.info(f"Retrieved users count: {count}")
            return count
    except Exception as e:
        logger.error(f"Failed to get users count: {e}")
        raise

def get_active_users_count():
    """Получение количества активных пользователей (end_date > текущей даты)"""
    try:
        with sqlite3.connect(SUBSCRIPTION_CONFIG['db_path']) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM clients
                WHERE end_date > ?
            """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
            count = cursor.fetchone()[0]
            logger.info(f"Retrieved active users count: {count}")
            return count
    except Exception as e:
        logger.error(f"Failed to get active users count: {e}")
        raise

def get_inactive_users_count():
    """Получение количества неактивных пользователей (end_date <= текущей даты)"""
    try:
        with sqlite3.connect(SUBSCRIPTION_CONFIG['db_path']) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM clients
                WHERE end_date <= ?
            """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
            count = cursor.fetchone()[0]
            logger.info(f"Retrieved inactive users count: {count}")
            return count
    except Exception as e:
        logger.error(f"Failed to get inactive users count: {e}")
        raise

def get_income():
    """Подсчёт дохода (сумма всех значений spend)"""
    try:
        with sqlite3.connect(SUBSCRIPTION_CONFIG['db_path']) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(CAST(spend AS INTEGER)) FROM clients")
            total_spend = cursor.fetchone()[0]
            income = int(total_spend) if total_spend else 0
            logger.info(f"Retrieved income: {income} руб. (total_spend={total_spend})")
            cursor.execute("SELECT tg_id, spend FROM clients")
            all_spends = cursor.fetchall()
            logger.debug(f"All clients spend: {all_spends}")
            return income
    except Exception as e:
        logger.error(f"Failed to get income: {e}")
        raise

def get_all_users():
    with sqlite3.connect(SUBSCRIPTION_CONFIG['db_path']) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tg_id FROM clients")
        return [row[0] for row in cursor.fetchall()]

def get_active_users():
    with sqlite3.connect(SUBSCRIPTION_CONFIG['db_path']) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tg_id FROM clients
            WHERE payment_status = 'active' AND (disabled_at IS NULL OR disabled_at = '')
        """)
        return [row[0] for row in cursor.fetchall()]

def get_inactive_users():
    with sqlite3.connect(SUBSCRIPTION_CONFIG['db_path']) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tg_id FROM clients
            WHERE payment_status != 'active' OR disabled_at IS NOT NULL
        """)
        return [row[0] for row in cursor.fetchall()]