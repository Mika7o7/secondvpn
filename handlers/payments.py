import json
import random
import string
import logging
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
    """Генерация 8-значного цифрового токена."""
    return ''.join(random.choices(string.digits, k=8))

@payments_router.message(Command("extend"))
@payments_router.callback_query(lambda call: call.data == "extend_subscription")
async def extend_subscription(event: types.Message | types.CallbackQuery, state: FSMContext):
    """Обработчик команды /extend или callback extend_subscription."""
    user_id = event.from_user.id
    client = get_client(user_id)
    if not client:
        if isinstance(event, types.Message):
            await event.answer("Сначала подключись к Zion с помощью /start.")
        else:
            await event.message.answer("Сначала подключись к Zion с помощью /start.")
            await event.answer()
        return

    await state.clear()
    text = (
        "💾 Продление доступа к Zion: 100 руб./мес.\n"
        "Введите количество месяцев для продления (1-12):"
    )
    if isinstance(event, types.Message):
        await event.answer(text)
    else:
        await event.message.answer(text)
        await event.answer()

    await state.set_state(ExtendSubscription.months)
    logger.info(f"Агент {user_id} начал продление доступа, ждём ввода месяцев")

@payments_router.message(ExtendSubscription.months)
async def process_months(message: types.Message, state: FSMContext):
    """Обработка количества месяцев."""
    user_id = message.from_user.id
    text = message.text.strip()
    logger.info(f"Агент {user_id} ввёл: {text}")

    try:
        months = int(text)
        if months < 1 or months > 12:
            await message.answer("Пожалуйста, введите число от 1 до 12.")
            logger.warning(f"Агент {user_id} ввёл неверное количество месяцев: {text}")
            return

        client = get_client(user_id)
        if not client or not client[1]:
            await message.answer("Ошибка: идентификатор агента не найден. Свяжитесь с Оракулом.")
            logger.error(f"Отсутствует идентификатор для агента {user_id}")
            await state.clear()
            return

        # Генерируем токен и сохраняем данные в состоянии
        payment_token = generate_payment_token()
        amount = 100 * months
        token_created = datetime.now().isoformat() + "+03:00"  # Формат ISO 8601
        await state.update_data(
            token=payment_token,
            months=months,
            amount=amount,
            username=client[1],
            token_created=token_created
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💾 Оплатить", url=PAYMENT_URL)],
            [InlineKeyboardButton(text="✅ Я оплатил", callback_data="confirm_payment")]
        ])
        await message.answer(
            f"⚠️ <b>Внимание!</b>\n"
            f"Укажи код <code>{payment_token}</code> в комментарии к платежу!\n\n"
            f"💰 {amount} руб. за {months} мес. доступа к Zion.\n"
            f"После оплаты нажми <b>«Я оплатил»</b>.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        logger.info(f"Агент {user_id} получил код матрицы {payment_token} и ссылку на оплату")

        await state.set_state(ExtendSubscription.awaiting_payment)
    except ValueError:
        await message.answer("Пожалуйста, введите целое число.")
        logger.warning(f"Агент {user_id} ввёл не число: {text}")
    except Exception as e:
        await message.answer(f"Ошибка в матрице: {str(e)}. Попробуй снова.")
        logger.error(f"Ошибка обработки для агента {user_id}: {str(e)}")
        await state.clear()

@payments_router.message(ExtendSubscription.months, lambda message: message.text.startswith('/'))
async def ignore_commands(message: types.Message):
    """Игнорируем команды во время ожидания ввода месяцев."""
    await message.answer("Пожалуйста, введите число от 1 до 12.")

@payments_router.callback_query(lambda call: call.data == "confirm_payment")
async def confirm_payment(call: types.CallbackQuery, state: FSMContext):
    """Обработка кнопки 'Я оплатил'."""
    user_id = call.from_user.id

    state_data = await state.get_data()
    # Это для теста
    payment_token = "ggwp"  # Оставляем ggwp для тестов
    expected_amount = state_data.get("amount")
    months = state_data.get("months")
    username = state_data.get("username")
    token_created = state_data.get("token_created")

    logger.info(f"Начало проверки транзакции для агента {user_id}: token={payment_token}, amount={expected_amount}, months={months}, username={username}, token_created={token_created}")

    if not all([payment_token, expected_amount, months, username, token_created]):
        await call.message.answer("Ошибка: данные транзакции не найдены. Попробуй снова с /extend.")
        logger.error(f"Данные транзакции не найдены для агента {user_id}")
        await call.answer()
        await state.clear()
        return

    try:
        # Устанавливаем временной диапазон для фильтрации
        created_time = datetime.fromisoformat(token_created)
        date_from = (created_time - timedelta(hours=1)).isoformat()  # 1 час назад
        date_to = (created_time + timedelta(days=1)).isoformat()  # 1 день вперёд

        # Проверяем транзакции через /api/timeline с фильтрацией
        logger.info(f"Запрос timeline для агента {user_id} с кодом {payment_token}, dateFrom={date_from}, dateTo={date_to}")
        timeline = await cloudtips.get_timeline(date_from=date_from, date_to=date_to)
        logger.info(f"Получен ответ timeline для агента {user_id}: {json.dumps(timeline, indent=2, ensure_ascii=False)}")
        if not timeline.get("succeed"):
            await call.message.answer("Ошибка проверки транзакции. Попробуй снова.")
            logger.error(f"Ошибка timeline для агента {user_id}: {timeline.get('errors')}")
            await call.answer()
            await state.clear()
            return

        # Ищем транзакцию с кодом матрицы
        for item in timeline.get("data", {}).get("items", []):
            logger.info(f"Проверка элемента timeline: comment={item.get('comment')}")
            if item.get("comment") == payment_token:
                amount = item.get("paymentAmount", 0)
                logger.info(f"Найдена транзакция для агента {user_id}: код {payment_token}, сумма {amount}, ожидаемая сумма {expected_amount}")
                # Рассчитываем пропорциональное количество месяцев
                proportion = amount / 100  # 100 RUB = 1 месяц
                effective_months = proportion * months
                # Транзакция подтверждена
                try:
                    new_end_date = update_client_expiry(tg_id=user_id, username=username, months=effective_months)
                    update_client_spend(tg_id=user_id, amount=amount)
                    update_client_status(user_id, "paid")
                    # Сообщение в зависимости от суммы
                    if abs(amount - expected_amount) < 0.01:
                        message = f"✅ Транзакция на {amount} RUB прошла! Доступ к Zion продлён на {months} мес. до {new_end_date}."
                    else:
                        effective_days = int(proportion * 30)  # 1 месяц = 30 дней
                        message = f"✅ Оплата на {amount} RUB получена (ожидалось {expected_amount} RUB). Доступ к Zion продлён на {effective_days} дней до {new_end_date}."
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="Вернуться", callback_data="back_to_start")]
                    ])
                    await call.message.answer(message, reply_markup=keyboard)
                    logger.info(f"Транзакция для агента {user_id} подтверждена (код {payment_token}, сумма {amount}, продлено на {effective_months} мес.)")
                    await state.clear()
                    await call.answer()
                    return
                except Exception as e:
                    await call.message.answer(
                        "✅ Транзакция прошла, но не удалось продлить доступ. Свяжитесь с Оракулом."
                    )
                    logger.error(f"Ошибка продления доступа для {user_id}: {str(e)}")
                    await call.answer()
                    await state.clear()
                    return

        # Транзакция не найдена
        await call.message.answer(
            "⏳ Транзакция не найдена или ещё не подтверждена. Попробуй снова через минуту."
        )
        logger.info(f"Транзакция с кодом {payment_token} не найдена для агента {user_id}")
        await call.answer()
    except Exception as e:
        await call.message.answer(f"Ошибка проверки транзакции: {str(e)}. Попробуй снова.")
        logger.error(f"Ошибка проверки для агента {user_id}: {str(e)}")
        await call.answer()
        await state.clear()

@payments_router.callback_query(lambda call: call.data == "back_to_start")
async def back_to_start(call: types.CallbackQuery):
    """Обработчик возврата к началу."""
    await call.message.answer("Используй /start для подключения к Zion.")
    await call.message.delete()
    await call.answer()
