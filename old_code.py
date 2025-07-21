import json
import random
import string
import logging
import asyncio
from datetime import datetime, timedelta
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_client, update_client_end_date, update_client_status, update_client_spend
from controlers.extend_subscription import update_client_expiry
from core.cloudtips_client import CloudTipsClient
from config import PAYMENT_URL, CLOUDTIPS_CLIENT_ID, TOKEN_FILE

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация роутера
payments_router = Router()

# Инициализация cloudtips
cloudtips = CloudTipsClient(CLOUDTIPS_CLIENT_ID, TOKEN_FILE)

# Класс для FSM
class ExtendSubscription(StatesGroup):
    months = State()
    awaiting_payment = State()

def generate_payment_token() -> str:
    return ''.join(random.choices(string.digits, k=8))

# Цены по акции
DISCOUNTED_PRICES = {
    1: 100,
    3: 250,
    6: 450,
    12: 800,
}

@payments_router.message(Command("extend"))
@payments_router.callback_query(lambda call: call.data == "extend_subscription")
async def extend_subscription(event: types.Message | types.CallbackQuery, state: FSMContext):
    user_id = event.from_user.id
    client = get_client(user_id)
    if not client:
        text = "Сначала подключись к Zion с помощью /start."
        if isinstance(event, types.Message):
            await event.answer(text)
        else:
            await event.message.answer(text)
            await event.answer()
        return

    await state.clear()
    price_list = "\n".join([f"{m} мес. — {p} руб." for m, p in DISCOUNTED_PRICES.items()])
    text = f"💾 Продление доступа к Zion:\n{price_list}\n\nВведите количество месяцев для продления (1, 3, 6 или 12):"

    if isinstance(event, types.Message):
        await event.answer(text)
    else:
        await event.message.answer(text)
        await event.answer()

    await state.set_state(ExtendSubscription.months)

@payments_router.message(ExtendSubscription.months)
async def process_months(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.strip()

    try:
        months = int(text)
        if months not in DISCOUNTED_PRICES:
            await message.answer("Пожалуйста, выбери 1, 3, 6 или 12 месяцев.")
            return

        client = get_client(user_id)
        if not client or not client[1]:
            await message.answer("Ошибка: идентификатор агента не найден. Свяжитесь с Оракулом.")
            await state.clear()
            return

        payment_token = generate_payment_token()
        amount = DISCOUNTED_PRICES[months]
        token_created = datetime.now().isoformat() + "+03:00"

        # Сохраняем данные в состояние
        await state.update_data(
            token=payment_token,
            months=months,
            amount=amount,
            username=client[1],
            token_created=token_created
        )

        # 1. Отправляем сначала предупреждение с кодом
        warning_text = (
            f"⚠️ <b>Внимание!</b>\n"
            f"Чтобы <b>оплата прошла автоматически</b>, обязательно укажи в комментарии к платежу этот код:\n\n"
            f"<code>{payment_token}</code>"
        )
        await message.answer(warning_text, parse_mode="HTML")

        # 2. Пауза 4 секунды
        await asyncio.sleep(4)

        # 3. Отправляем клавиатуру с кнопками
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💾 Оплатить", url=PAYMENT_URL)],
            [InlineKeyboardButton(text="✅ Я оплатил", callback_data="confirm_payment")]
        ])

        # 4. Основное сообщение после предупреждения
        await message.answer(
            f"💰 {amount} руб. за {months} мес. доступа к Zion.\n"
            f"После оплаты не забудь нажать <b>«Я оплатил»</b>.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

        # Устанавливаем состояние ожидания оплаты
        await state.set_state(ExtendSubscription.awaiting_payment)

    except ValueError:
        await message.answer("Пожалуйста, введите целое число.")
    except Exception as e:
        await message.answer(f"Ошибка в матрице: {str(e)}. Попробуй снова.")
        await state.clear()

@payments_router.message(ExtendSubscription.months, lambda message: message.text.startswith('/'))
async def ignore_commands(message: types.Message):
    await message.answer("Пожалуйста, введите 1, 3, 6 или 12 месяцев.")

@payments_router.callback_query(lambda call: call.data == "confirm_payment")
async def confirm_payment(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    state_data = await state.get_data()

    payment_token = state_data.get("token")
    expected_amount = state_data.get("amount")
    months = state_data.get("months")
    username = state_data.get("username")
    token_created = state_data.get("token_created")

    if not all([payment_token, expected_amount, months, username, token_created]):
        await call.message.answer("Ошибка: данные транзакции не найдены. Попробуй снова с /extend.")
        await call.answer()
        await state.clear()
        return

    try:
        created_time = datetime.fromisoformat(token_created)
        date_from = (created_time - timedelta(hours=2)).isoformat()
        date_to = (created_time + timedelta(days=1)).isoformat()

        timeline = await cloudtips.get_timeline(date_from=date_from, date_to=date_to)
        if not timeline.get("succeed"):
            await call.message.answer("Ошибка проверки транзакции. Попробуй снова.")
            await call.answer()
            await state.clear()
            return

        for item in timeline.get("data", {}).get("items", []):
            if item.get("comment") == payment_token:
                amount = item.get("paymentAmount", 0)
                proportion = amount / 100
                effective_months = proportion

                try:
                    new_end_date = update_client_expiry(tg_id=user_id, username=username, months=effective_months)
                    update_client_spend(tg_id=user_id, amount=amount)
                    update_client_status(user_id, "paid")

                    if abs(amount - expected_amount) < 0.01:
                        message = f"✅ Транзакция на {amount} RUB прошла! Доступ к Zion продлён на {months} мес. до {new_end_date}."
                    else:
                        effective_days = int(proportion * 30)
                        message = f"✅ Оплата на {amount} RUB получена. Доступ к Zion продлён на {effective_days} дней до {new_end_date}."

                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="Вернуться", callback_data="back_to_start")]
                    ])
                    await call.message.answer(message, reply_markup=keyboard)
                    await state.clear()
                    await call.answer()
                    return

                except Exception as e:
                    await call.message.answer("✅ Транзакция прошла, но не удалось продлить доступ. Свяжитесь с Оракулом.")
                    await state.clear()
                    await call.answer()
                    return

        await call.message.answer("⏳ Транзакция не найдена или ещё не подтверждена. Попробуй снова через минуту.")
        await call.answer()
    except Exception as e:
        await call.message.answer(f"Ошибка проверки транзакции: {str(e)}. Попробуй снова.")
        await state.clear()
        await call.answer()

@payments_router.callback_query(lambda call: call.data == "back_to_start")
async def back_to_start(call: types.CallbackQuery):
    await call.message.answer("Используй /start для подключения к Zion.")
    await call.message.delete()
    await call.answer()
