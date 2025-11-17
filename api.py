# fastapi_app.py — ФИНАЛЬНАЯ ВЕРСИЯ 2025
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional
import sqlite3
import logging
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
import time


from controlers import add_client, delete_inbound
from controlers.extend_subscription import update_client_expiry
from utils import generate_marzban_username
from core.cloudtips_client import CloudTipsClient
from config import SUBSCRIPTION_CONFIG, PAYMENT_URL, CLOUDTIPS_CLIENT_ID, TOKEN_FILE
from database import (
    get_client, create_client, create_user_key, get_user_keys,
    extend_user_key, delete_user_key, get_referrals_count,
    update_client_spend, update_client_status, add_bonus_days,
    get_user_bonus_days, deduct_bonus_days
)
from core.referrals import apply_referral

logger = logging.getLogger(__name__)
app = FastAPI()
cloudtips = CloudTipsClient(CLOUDTIPS_CLIENT_ID, TOKEN_FILE)
DB_PATH = SUBSCRIPTION_CONFIG['db_path']

# === РАЗРЕШАЕМ ВСЕ ИСТОЧНИКИ (для WebApp в Telegram) ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене можно ограничить: ["https://web.telegram.org", "https://твой-домен.lhr.life"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================== МОДЕЛИ ======================
class CreateUserRequest(BaseModel):
    tg_id: int
    username: str | None = None
    ref_code: str | None = None   # например: "ref123456789"

class CreateKeyRequest(BaseModel):
    user_id: int
    device_name: str
    months: int = Field(..., ge=1, le=36)
    payment_method: Optional[str] = None  # "bonuses" или None (по умолчанию — рубли)

class ExtendKeyRequest(BaseModel):
    user_id: int
    key_id: int
    months: int
    payment_method: Literal['sbp', 'bonuses']
    amount_rub: Optional[float] = None  # Только для СБП


class DeleteKeyRequest(BaseModel):
    user_id: int
    key_id: int

# ====================== РОУТЫ ======================

@app.post("/api/create_user")
async def create_user(data: CreateUserRequest):
    try:
        # Проверяем, есть ли уже пользователь
        client = get_client(data.tg_id)
        if client:
            keys = get_user_keys(data.tg_id)
            formatted = [
                {"id": k[0], "name": k[1], "key": k[2], "expires": k[3], "is_trial": bool(k[4])}
                for k in keys
            ]
            return {"success": True, "already_exists": True, "keys": formatted}

        # === Рефералка ===
        referrer_id = None
        if data.ref_code and data.ref_code.startswith("ref"):
            try:
                referrer_id = int(data.ref_code[3:])
            except:
                pass

        # === Базовое имя ===
        base_name = data.username.strip() if data.username else f"id{data.tg_id}"

        # === Создаём клиента в своей базе ===
        create_client(data.tg_id, base_name, referrer_id)

        # === Триал-ключ ===
        trial_days = SUBSCRIPTION_CONFIG.get("trial_days", 3)
        marzban_username = generate_marzban_username(base_name, "trial", is_trial=True)

        try:
            link, _ = add_client.add_client(
                tg_id=data.tg_id,
                marzban_username=marzban_username,   # ← ИСПРАВЛЕНО: было trial_username
                expiry_days=trial_days,
                is_trial=True                        # ← on_hold + 3 дня
            )
            link = str(link).replace(".org", ".org:8000")
        except Exception as e:
            logger.error(f"Marzban trial error: {e}")
            raise HTTPException(500, "Не удалось создать триал-ключ")

        end_date = (datetime.now() + timedelta(days=trial_days)).strftime("%Y-%m-%d %H:%M:%S")

        create_user_key(
            tg_id=data.tg_id,
            marzban_username=marzban_username,
            device_name="Триал-ключ",
            vless_link=link,
            months=0,                    # триал — не считаем как месяц
            is_trial=True
        )

        logger.info(f"Создан триал для {data.tg_id} → {marzban_username}")
        return {"success": True, "trial_key": link, "end_date": end_date}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"create_user error: {e}")
        raise HTTPException(500, "Ошибка сервера")

@app.get("/api/my-data")
async def my_data(user_id: int):
    client = get_client(user_id)
    print(client)
    if not client:
        raise HTTPException(404, "User not found")

    keys = get_user_keys(user_id)
    print(keys)
    formatted_keys = [
        {
            "id": k[0],
            "name": k[1],
            "key": k[2],
            "expires": k[3],
            "is_trial": bool(k[4])
        } for k in keys
    ]

    return {
        "keys": formatted_keys,
        "bonus_days": client["bonus_days"] or 0,           # теперь по имени и с дефолтом
        "used_bonus_days": client["used_bonus_days"] or 0,
        "referrals_count": get_referrals_count(user_id),
        "ref_link": f"https://t.me/MatrixVpnBot?start=ref{user_id}"
    }



@app.post("/api/create-key")
async def create_key(data: CreateKeyRequest):
    try:
        user = get_client(data.user_id)
        if not user:
            raise HTTPException(404, "Пользователь не найден")

        # === Проверка бонусов / оплата ===
        if getattr(data, "payment_method", None) == "bonuses":
            needed = data.months * 30
            current = get_user_bonus_days(data.user_id)
            if current < needed:
                raise HTTPException(400, "Недостаточно бонусных дней")
            deduct_bonus_days(data.user_id, needed)
        else:
            price = get_price(data.months)
            update_client_spend(data.user_id, price)

        base_name = user["username"] if user["username"] and "@" not in user["username"] else f"id{data.user_id}"
        marzban_username = generate_marzban_username(base_name, data.device_name, is_trial=False)

        # ВАЖНО: is_trial=False → сразу active + нужные дни
        link, _ = add_client.add_client(
            tg_id=data.user_id,
            marzban_username=marzban_username,
            expiry_days=data.months * 30,
            is_trial=False        # ← ЭТО ГЛАВНОЕ
        )
        link = str(link).replace(".org", ".org:8000")

        end_date = (datetime.now() + timedelta(days=data.months * 30)).strftime("%Y-%m-%d %H:%M:%S")

        create_user_key(
            tg_id=data.user_id,
            marzban_username=marzban_username,
            device_name=data.device_name,
            vless_link=link,
            months=data.months,
            is_trial=False
        )

        return {"success": True, "link": link, "end_date": end_date}

    except Exception as e:
        logger.error(f"create-key error: {e}")
        raise HTTPException(500, "Ошибка сервера")


@app.post("/api/extend-key")
async def extend_key(data: ExtendKeyRequest):
    try:
        # 1. Проверяем существование пользователя
        user = get_client(data.user_id)
        if not user:
            raise HTTPException(404, "Пользователь не найден")

        # 2. Находим ключ
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT marzban_username, device_name, end_date 
                FROM user_keys 
                WHERE id = ? AND tg_id = ?
            """, (data.key_id, data.user_id))
            row = c.fetchone()
            if not row:
                raise HTTPException(404, "Ключ не найден или не ваш")

            marzban_username, device_name, current_end_date = row

        # 3. ОПЛАТА
        if data.payment_method == "bonuses":
            needed_days = data.months * 30
            current_bonus = get_user_bonus_days(data.user_id)
            if current_bonus < needed_days:
                raise HTTPException(400, "Недостаточно бонусных дней")
            deduct_bonus_days(data.user_id, needed_days)
            logger.info(f"Списано {needed_days} бонусных дней у {data.user_id}")

        elif data.payment_method == "sbp":
            if data.amount_rub is None:
                raise HTTPException(400, "amount_rub обязателен для СБП")
            price = get_price(data.months)
            if abs(data.amount_rub - price) > 0.01:
                raise HTTPException(400, "Неверная сумма оплаты")
            update_client_spend(data.user_id, price)
            logger.info(f"Оплата СБП: {data.amount_rub}₽ за {data.months} мес.")

        # 4. Продлеваем в Marzban
        try:
            new_end_date = update_client_expiry(
                key_id=data.key_id,           # ← НОВЫЙ ПАРАМЕТР
                tg_id=data.user_id,
                username=marzban_username,
                months=data.months
            )
        except Exception as e:
            logger.error(f"Ошибка Marzban при продлении: {e}")
            raise HTTPException(500, "Не удалось продлить в Marzban")

        # 5. Обновляем в своей базе
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE user_keys 
                SET end_date = ? 
                WHERE id = ?
            """, (new_end_date, data.key_id))
            conn.commit()

        return {
            "success": True,
            "message": f"Ключ «{device_name}» продлён на {data.months} мес.",
            "new_end_date": new_end_date,
            "payment_method": data.payment_method
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"extend-key error: {e}")
        raise HTTPException(500, "Ошибка сервера")


@app.post("/api/delete-key")
async def delete_key(data: DeleteKeyRequest):
    """
    Удаление одного конкретного ключа по его ID
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()

            # 1. Находим ключ и проверяем владельца
            c.execute("""
                SELECT marzban_username, tg_id 
                FROM user_keys 
                WHERE id = ?
            """, (data.key_id,))
            row = c.fetchone()

            if not row:
                raise HTTPException(404, "Ключ не найден")

            marzban_username, owner_tg_id = row

            if owner_tg_id != data.user_id:
                logger.warning(f"Попытка удалить чужой ключ: user {data.user_id} → key {data.key_id}")
                raise HTTPException(403, "Это не ваш ключ")

            # 2. Удаляем из Marzban
            try:
                delete_inbound.delete_inbound(data.user_id, marzban_username)
                logger.info(f"Удалён из Marzban: {marzban_username} (tg_id={data.user_id})")
            except Exception as e:
                logger.error(f"Ошибка при удалении из Marzban ({marzban_username}): {e}")
                # Не падаем — ключ всё равно удалим из своей базы

            # 3. Удаляем ТОЛЬКО этот ключ из своей базы (НЕ трогаем таблицу clients!)
            c.execute("DELETE FROM user_keys WHERE id = ?", (data.key_id,))
            conn.commit()

            logger.info(f"Ключ id={data.key_id} успешно удалён из базы (tg_id={data.user_id})")

        return {
            "success": True,
            "message": "Ключ удалён"
        }

    except HTTPException:
        raise  # Пробрасываем 404/403 как есть
    except Exception as e:
        logger.error(f"delete-key error: {e}")
        raise HTTPException(500, "Ошибка сервера")


# api.py
import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException

# Хранилище ожидающих платежей (в памяти или Redis)
pending_payments = {}

@app.post("/api/init-sbp")
async def init_sbp(data: dict):
    user_id = data["user_id"]
    months = data["months"]
    device_name = data.get("device_name")
    key_id = data.get("key_id")

    # Генерируем уникальный код (8 цифр)
    code = str(uuid.uuid4().int)[:8]
    price = get_price(months)

    # Сохраняем ожидающий платёж
    pending_payments[code] = {
        "user_id": user_id,
        "months": months,
        "price": price,
        "device_name": device_name,
        "key_id": key_id,
        "created_at": datetime.now()
    }

    return {"code": code, "price": price}


@app.post("/api/confirm-sbp")
async def confirm_sbp(data: dict):
    code = data.get("code", "").strip()
    if not code:
        raise HTTPException(400, "Код обязателен")

    payment = pending_payments.get(code)
    if not payment:
        raise HTTPException(400, "Код не найден или истёк")

    # ← ПРЕОБРАЗУЕМ sqlite3.Row → dict
    payment_dict = dict(payment)
    price = float(payment_dict.get("price", 0))
    months = int(payment_dict.get("months", 1))
    user_id = payment_dict.get("user_id")
    device_name = payment_dict.get("device_name")
    key_id = payment_dict.get("key_id")



    logger.info(f"Ожидаем: {price}₽, код: {code}, user_id: {user_id}, key: {key_id}")

    # === ПОЛУЧАЕМ ПОЛЬЗОВАТЕЛЯ ИЗ БД ===
    user = get_client(user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    # 2. Находим ключ
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT marzban_username, device_name, end_date 
            FROM user_keys 
            WHERE id = ? AND tg_id = ?
        """, (key_id, user_id))
        row = c.fetchone()
        if not row:
            raise HTTPException(404, "Ключ не найден или не ваш")
        marzban_username, device_name, current_end_date = row

    del pending_payments[code]

    # === ИЩЕМ ЗА ПОСЛЕДНИЙ ЧАС (как просил) ===
    now = datetime.now()
    date_from = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S+03:00")
    date_to = (now + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S+03:00")

    logger.info(f"Ищем с {date_from} по {date_to}")

    try:
        timeline = await cloudtips.get_timeline(
            page=1,
            limit=100,
            date_from=date_from,
            date_to=date_to
        )
    except Exception as e:
        logger.error(f"CloudTips error: {e}")
        raise HTTPException(500, "Ошибка CloudTips")

    if not timeline.get("succeed"):
        raise HTTPException(500, "CloudTips API error")

    items = timeline.get("data", {}).get("items", [])
    logger.info(f"Найдено {len(items)} транзакций за час")

    for item in items:
        comment = (item.get("comment") or "").strip()
        amount = float(item.get("paymentAmount", 0))

        if comment == code and abs(amount - price) < 0.01:
            logger.info(f"ПЛАТЁЖ НАЙДЕН: {amount}₽ == {price}₽")

            try:
                if key_id:
                    # 4. Продлеваем в Marzban
                    try:
                        new_end_date = update_client_expiry(
                            key_id=key_id,           # ← НОВЫЙ ПАРАМЕТР
                            tg_id=user_id,
                            username=marzban_username,
                            months=months
                        )
                    except Exception as e:
                        logger.error(f"Ошибка Marzban при продлении: {e}")
                        raise HTTPException(500, "Не удалось продлить в Marzban")

                    # 5. Обновляем в своей базе
                    with sqlite3.connect(DB_PATH) as conn:
                        c = conn.cursor()
                        c.execute("""
                            UPDATE user_keys 
                            SET end_date = ? 
                            WHERE id = ?
                        """, (new_end_date, key_id))
                        conn.commit()

                    return {
                        "success": True,
                        "message": f"Ключ «{device_name}» продлён на {months} мес.",
                        "id": key_id,
                        "end_date": new_end_date.strftime("%Y-%m-%d") if isinstance(new_end_date, datetime) else new_end_date
                    }
                else:
                    # НОВЫЙ КЛЮЧ
                    # === НОВЫЙ КЛЮЧ — ПО ТОЙ ЖЕ ЛОГИКЕ, ЧТО В INIT_SBP ===
                    base_name = user["username"] if user["username"] and "@" not in user["username"] else f"id{user_id}"
                    marzban_username = generate_marzban_username(base_name, device_name, is_trial=False)

                    link, _ = add_client.add_client(
                        tg_id=user_id,
                        marzban_username=marzban_username,
                        expiry_days=months * 30,
                        is_trial=False  # ← ВАЖНО: сразу активный
                    )
                    link = str(link).replace(".org", ".org:8000")

                    end_date = (datetime.now() + timedelta(days=months * 30)).strftime("%Y-%m-%d")

                    db.create_user_key(
                        tg_id=user_id,
                        marzban_username=marzban_username,
                        device_name=device_name,
                        vless_link=link,
                        months=months,
                        is_trial=False
                    )

                    return {
                        "success": True,
                        "message": f"Ключ создан на {months} мес.",
                        "link": link,
                        "end_date": end_date
                    }
            except Exception as e:
                logger.error(f"Ошибка ключа: {e}")
                raise HTTPException(500, "Платёж прошёл, но ключ не создан")

    raise HTTPException(400, f"Платёж не найден. Код: {code}")

# Вспомогательная функция цены
def get_price(months: int) -> int:
    prices = {1: 100, 3: 250, 6: 450, 12: 800}
    return prices.get(months, months * 100)


# Запуск (если запускаешь напрямую)
if __name__ == "__main__":
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8000, reload=True)