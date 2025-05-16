from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile
from database import get_client, create_client, update_client_status
from controlers.add_client import add_client
from datetime import datetime
from config import SUBSCRIPTION_CONFIG
from keyboards.inline_keyboards import extend_keyboard, vless_keyboard
import logging

logger = logging.getLogger(__name__)

start_router = Router()


@start_router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    logger.info(f"Processing /start for user {user_id}")

    client = get_client(user_id)
    logger.info(f"get_client({user_id}) returned: {client}")

    if client:
        try:
            end_date = datetime.strptime(client[3], "%Y-%m-%d %H:%M:%S")
            payment_status = client[2]
            logger.info(f"Client {user_id} found: end_date={end_date}, payment_status={payment_status}")

            text = (
                "☠️ Добро пожаловать обратно, беглец из Матрицы!\n\n"
                f"Твой доступ к Зиону активен до {client[3]}.\n"
                "Продлить доступ к Зиону за 100 руб./мес.?\n\n"
            )
            await message.answer(text, reply_markup=extend_keyboard(), parse_mode="HTML")
            return

        except ValueError as e:
            logger.error(f"Invalid end_date for user {user_id}: {client[3]}, error: {e}")
            await message.answer("Ошибка: неверный формат даты. Свяжитесь с поддержкой.")
            return

    # Новый клиент
    logger.info(f"Creating new client {user_id}")
    try:
        subscription_url, username = add_client(user_id)
        create_client(user_id, username, None)
        await state.update_data(subscription_url=subscription_url)

        text = (
            "🚀 Тебе открыт доступ к Зиону: неограниченная скорость, новейшие технологии и точки входа по всему миру.\n\n"
            "🛰️ Подключение через зашифрованные каналы — ты вне зоны слежки.\n\n"
            "🛡️ Оставайся невидимкой в мире цифрового контроля.\n\n"
            f"🎁 Бесплатный доступ к Зиону на {SUBSCRIPTION_CONFIG['trial_days']} дня!\n\n"
            "🚀 Что делать дальше?\n"
            "1️⃣ СКАЧАЙ приложение для своего устройства 👇\n"
            "2️⃣ НАЖМИ на 💊, чтобы получить ключи к Зиону\n"
            "3️⃣ ОТКРОЙ приложение и нажми ➕\n"
            "4️⃣ ВСТАВЬ ключ из буфера обмена\n"
            "5️⃣ НАЖМИ 'Подключиться' 🔌\n\n"
            "🌐 Добро пожаловать в Зион."
        )

        try:
            with open("images/matrix.jpeg", "rb") as file:
                photo = BufferedInputFile(file.read(), filename="matrix.jpeg")
            await message.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=vless_keyboard(),
                parse_mode="HTML"
            )
        except FileNotFoundError:
            logger.warning("Изображение matrix.jpeg не найдено.")
            await message.answer(text, reply_markup=vless_keyboard(), parse_mode="HTML")

    except Exception as e:
        logger.error(f"Failed to create client {user_id}: {e}")
        await message.answer("Ошибка при получении доступа к Зиону. Попробуйте позже или свяжитесь с поддержкой.")
        return

@start_router.message(Command("support"))
async def support_cmd(message: types.Message):
    await message.answer(
        "📞 [Написать в поддержку](https://t.me/Mikaggwp)",
        disable_web_page_preview=True,
        parse_mode="Markdown"
    )

@start_router.message(Command("channel"))
async def channel_cmd(message: types.Message):
    await message.answer(
        "📢 [Перейти в наш канал](https://t.me/+teMI40exbmk2MGEy)",
        disable_web_page_preview=True,
        parse_mode="Markdown"
    )

@start_router.callback_query(lambda call: call.data == "copy_vless")
async def copy_vless_callback(call: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Таблетка' (💊)"""
    user_id = call.from_user.id
    data = await state.get_data()
    subscription_url = data.get("subscription_url")
    subscription_url = str(subscription_url).replace(".org",".org:8000")
    if subscription_url:
        message_text = f"🔴 Твои ключи к Зиону.\n\n<code>{subscription_url}</code>"
        await call.message.answer(message_text, parse_mode="HTML")
        await call.answer()
    else:
        await call.message.answer("Ошибка: ключи не найдены. Используй /start.")
        await call.answer()
