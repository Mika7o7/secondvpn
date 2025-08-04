from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import (
    get_users_count, get_active_users_count, get_inactive_users_count,
    get_income, get_all_users, get_active_users, get_inactive_users
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

admin_router = Router()

# ID администратора
ADMIN_ID = 1628997906

def is_admin(user_id):
    """Проверка, является ли пользователь администратором"""
    return user_id == ADMIN_ID


# --- FSM для рассылки ---
class BroadcastState(StatesGroup):
    waiting_for_message = State()
    waiting_for_target_group = State()

# --- Команда для запуска рассылки ---
@admin_router.message(Command("broadcast"))
async def start_broadcast(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return await message.answer("У вас нет доступа к этой команде.")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Всем", callback_data="broadcast_all")],
        [InlineKeyboardButton(text="✅ Только активным", callback_data="broadcast_active")],
        [InlineKeyboardButton(text="🚫 Только неактивным", callback_data="broadcast_inactive")]
    ])
    await message.answer("Кому отправить сообщение?", reply_markup=keyboard)
    await state.set_state(BroadcastState.waiting_for_target_group)

# --- Обработка выбора целевой группы ---
@admin_router.callback_query(lambda c: c.data.startswith("broadcast_"))
async def choose_group(callback: types.CallbackQuery, state: FSMContext):
    group = callback.data.replace("broadcast_", "")
    await state.update_data(target_group=group)
    await callback.message.edit_text("✍️ Введи сообщение для рассылки (можно с фото):")
    await state.set_state(BroadcastState.waiting_for_message)

# --- Обработка текста и/или фото ---
@admin_router.message(BroadcastState.waiting_for_message)
async def send_broadcast(message: types.Message, state: FSMContext, bot):
    data = await state.get_data()
    group = data.get("target_group")

    text = message.text
    photo = message.photo[-1].file_id if message.photo else None

    if not text and not photo:
        return await message.answer("❌ Вы не отправили ни текста, ни изображения. Повторите попытку.")

    if group == "all":
        users = get_all_users()
    elif group == "active":
        users = get_active_users()
    elif group == "inactive":
        users = get_inactive_users()
    else:
        users = []

    success = 0
    fail = 0
    for user_id in users:
        try:
            if photo:
                await bot.send_photo(chat_id=user_id, photo=photo, caption=text or "")
            else:
                await bot.send_message(chat_id=user_id, text=text)
            success += 1
        except Exception as e:
            fail += 1
            logger.warning(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

    await message.answer(f"📤 Рассылка завершена.\n✅ Отправлено: {success}\n❌ Ошибок: {fail}")
    await state.clear()

# --- Команда /users_count ---
@admin_router.message(Command("users_count"))
async def users_count(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("У вас нет доступа к этой команде.")
        return

    try:
        count = get_users_count()
        await message.answer(f"Общее количество пользователей: {count}")
    except Exception as e:
        await message.answer(f"Ошибка при получении данных: {str(e)}")

# --- Команда /active_users ---
@admin_router.message(Command("active_users"))
async def active_users(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("У вас нет доступа к этой команде.")
        return

    try:
        count = get_active_users_count()
        await message.answer(f"Количество активных пользователей: {count}")
    except Exception as e:
        await message.answer(f"Ошибка при получении данных: {str(e)}")

# --- Команда /inactive_users ---
@admin_router.message(Command("inactive_users"))
async def inactive_users(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("У вас нет доступа к этой команде.")
        return

    try:
        count = get_inactive_users_count()
        await message.answer(f"Количество неактивных пользователей: {count}")
    except Exception as e:
        await message.answer(f"Ошибка при получении данных: {str(e)}")

# --- Команда /income ---
@admin_router.message(Command("income"))
async def income(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("У вас нет доступа к этой команде.")
        return

    try:
        total_income = get_income()
        await message.answer(f"Общий доход: {total_income} руб.")
    except Exception as e:
        await message.answer(f"Ошибка при получении данных: {str(e)}")

