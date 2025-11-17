# database.py — ФИНАЛЬНАЯ ВЕРСИЯ (2025)
import sqlite3
import logging
from datetime import datetime, timedelta
from config import SUBSCRIPTION_CONFIG

logger = logging.getLogger(__name__)
DB_PATH = SUBSCRIPTION_CONFIG['db_path']

# ====================== МИГРАЦИЯ (безопасная, можно запускать всегда) ======================
def run_migration():
    """Безопасная миграция — создаём таблицы, добавляем колонки"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # === 1. СОЗДАЁМ ТАБЛИЦУ clients (если нет) ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            payment_status TEXT DEFAULT 'trial',
            end_date TEXT,
            server_country TEXT,
            disabled_at TEXT,
            spend TEXT DEFAULT '0',
            referrer_id INTEGER,
            bonus_days INTEGER DEFAULT 0,
            used_bonus_days INTEGER DEFAULT 0,
            trial_given INTEGER DEFAULT 0
        )
    """)
    logger.info("Таблица clients создана или уже существует")

    # === 2. Добавляем недостающие колонки в clients ===
    columns_to_add = [
        ("referrer_id", "INTEGER"),
        ("bonus_days", "INTEGER DEFAULT 0"),
        ("used_bonus_days", "INTEGER DEFAULT 0"),
        ("trial_given", "INTEGER DEFAULT 0"),
    ]
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE clients ADD COLUMN {col_name} {col_type}")
            logger.info(f"Добавлена колонка: {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise

    # === 3. Таблица ключей ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER NOT NULL,
            marzban_username TEXT NOT NULL,
            device_name TEXT DEFAULT 'Мой ключ',
            vless_link TEXT,
            end_date TEXT,
            is_trial INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (tg_id) REFERENCES clients (tg_id)
        )
    """)

    # === 4. Удаляем старый UNIQUE индекс ===
    cursor.execute("DROP INDEX IF EXISTS idx_user_keys_marzban_username")

    # === 5. Таблица рефералов ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_tg_id INTEGER NOT NULL,
            invited_tg_id INTEGER NOT NULL,
            invited_at TEXT DEFAULT (datetime('now')),
            reward_given INTEGER DEFAULT 0,
            UNIQUE(referrer_tg_id, invited_tg_id)
        )
    """)

    # === 6. Индексы ===
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_keys_tg_id ON user_keys (tg_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_keys_end_date ON user_keys (end_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON referrals (referrer_tg_id)")

    conn.commit()
    conn.close()
    logger.info("Миграция базы данных успешно завершена!")


# ====================== ОСНОВНЫЕ ФУНКЦИИ ======================
def init_db():
    """Инициализация + миграция"""
    run_migration()  # Безопасно — можно оставить навсегда


def get_client(tg_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tg_id, username, payment_status, end_date, server_country,
                   disabled_at, spend, referrer_id, bonus_days, used_bonus_days, trial_given
            FROM clients WHERE tg_id = ?
        """, (tg_id,))
        return cursor.fetchone()


def create_client(tg_id: int, username: str = None, referrer_id: int = None) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM clients WHERE tg_id = ?", (tg_id,))
        if cursor.fetchone():
            return False

        trial_days = SUBSCRIPTION_CONFIG.get('trial_days', 3)
        end_date = (datetime.now() + timedelta(days=trial_days)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO clients (
                tg_id, username, payment_status, end_date, spend,
                referrer_id, trial_given, bonus_days, used_bonus_days
            ) VALUES (?, ?, 'trial', ?, 0, ?, 1, 0, 0)
        """, (tg_id, username or f"user_{tg_id}", end_date, referrer_id))
        conn.commit()
    return True


def create_user_key(tg_id: int, device_name: str, months: int, vless_link: str, marzban_username: str, is_trial: bool = False):
    """Создание нового ключа (триал или платный)"""
    end_date = (datetime.now() + timedelta(days=months * 30)).strftime("%Y-%m-%d %H:%M:%S")
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_keys
            (tg_id, marzban_username, device_name, vless_link, end_date, is_trial)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tg_id, marzban_username, device_name, vless_link, end_date, int(is_trial)))
        conn.commit()
    
    logger.info(f"Создан ключ: {device_name} для tg_id={tg_id}, marzban_username={marzban_username}, триал={is_trial}")


def extend_user_key(key_id: int, months: int) -> bool:
    """Продление конкретного ключа"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT end_date FROM user_keys WHERE id = ?", (key_id,))
        row = cursor.fetchone()
        if not row:
            return False
        current_end = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        new_end = current_end + timedelta(days=months * 30)
        cursor.execute("UPDATE user_keys SET end_date = ? WHERE id = ?",
                       (new_end.strftime("%Y-%m-%d %H:%M:%S"), key_id))
        conn.commit()
        logger.info(f"Продлён ключ {key_id} на {months} мес.")
    return True


def get_user_keys(tg_id: int):
    """Все ключи пользователя"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, device_name, vless_link, end_date, is_trial
            FROM user_keys WHERE tg_id = ? ORDER BY created_at DESC
        """, (tg_id,))
        return cursor.fetchall()

def get_user_bonus_days(tg_id: int) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT bonus_days FROM clients WHERE tg_id = ?", (tg_id,))
        row = c.fetchone()
        return row[0] if row else 0

def deduct_bonus_days(tg_id: int, days: int):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("UPDATE clients SET bonus_days = bonus_days - ? WHERE tg_id = ?", (days, tg_id))
        conn.commit()

def delete_user_key(key_id: int):
    """Удаление ключа"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_keys WHERE id = ?", (key_id,))
        conn.commit()


def add_bonus_days(tg_id: int, days: int):
    """Начисление бонусных дней (за рефералку)"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE clients SET bonus_days = bonus_days + ? WHERE tg_id = ?", (days, tg_id))
        conn.commit()


def get_referrals_count(tg_id: int) -> int:
    """Сколько человек пригласил"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM referrals WHERE referrer_tg_id = ?", (tg_id,))
        return cursor.fetchone()[0]


def get_referral_link(tg_id: int) -> str:
    return f"https://t.me/MatrixVpnBot?start=ref{tg_id}"


# ====================== АДМИН-ФУНКЦИИ ======================
def get_expired_clients():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tg_id, username, payment_status, end_date, server_country, disabled_at
                FROM clients WHERE end_date <= ?
            """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Failed to get expired clients: {e}")
        return []


def update_client_status(tg_id, status):
    try:
        with sqlite3.connect(DB_PATH) as conn:
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
    try:
        with sqlite3.connect(DB_PATH) as conn:
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
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT spend FROM clients WHERE tg_id = ?", (tg_id,))
            row = cursor.fetchone()
            previous_spend = float(row[0]) if row and row[0] else 0
            new_spend = previous_spend + amount
            cursor.execute("UPDATE clients SET spend = ? WHERE tg_id = ?", (str(new_spend), tg_id))
            conn.commit()
            logger.info(f"Updated spend for {tg_id}: {previous_spend} → {new_spend}")
    except Exception as e:
        logger.error(f"Failed to update spend for client {tg_id}: {e}")
        raise


def set_client_disabled_at(tg_id, disabled_at):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE clients SET disabled_at = ? WHERE tg_id = ?", (disabled_at, tg_id))
            conn.commit()
        logger.info(f"Set disabled_at for client {tg_id} to {disabled_at}")
    except Exception as e:
        logger.error(f"Failed to set disabled_at for client {tg_id}: {e}")
        raise


def delete_client(tg_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients WHERE tg_id = ?", (tg_id,))
            conn.commit()
        logger.info(f"Deleted client {tg_id} from database")
    except Exception as e:
        logger.error(f"Failed to delete client {tg_id}: {e}")
        raise


def get_users_count():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM clients")
            count = cursor.fetchone()[0]
            logger.info(f"Retrieved users count: {count}")
            return count
    except Exception as e:
        logger.error(f"Failed to get users count: {e}")
        raise


def get_active_users_count():
    try:
        with sqlite3.connect(DB_PATH) as conn:
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
    try:
        with sqlite3.connect(DB_PATH) as conn:
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
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(CAST(spend AS REAL)) FROM clients")
            total = cursor.fetchone()[0]
            income = int(total) if total else 0
            logger.info(f"Доход: {income} руб.")
            return income
    except Exception as e:
        logger.error(f"Failed to get income: {e}")
        raise


def get_all_users():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tg_id FROM clients")
        return [row[0] for row in cursor.fetchall()]


def get_active_users():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tg_id FROM clients
            WHERE payment_status = 'active' AND (disabled_at IS NULL OR disabled_at = '')
        """)
        return [row[0] for row in cursor.fetchall()]


def get_inactive_users():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tg_id FROM clients
            WHERE payment_status != 'active' OR disabled_at IS NOT NULL
        """)
        return [row[0] for row in cursor.fetchall()]


# ====================== ЗАПУСК ======================
if __name__ == "__main__":
    init_db()
    print("База данных обновлена! Теперь всё по-взрослому")