from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_users_count, get_active_users_count, get_inactive_users_count, get_income, get_all_users, get_active_users, get_inactive_users
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
    await callback.message.edit_text("✍️ Введи сообщение для рассылки:")
    await state.set_state(BroadcastState.waiting_for_message)

# --- Обработка текста сообщения ---
@admin_router.message(BroadcastState.waiting_for_message)
async def send_broadcast(message: types.Message, state: FSMContext, bot):
    data = await state.get_data()
    group = data.get("target_group")
    text = message.text
    
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
            await bot.send_message(user_id, text)
            success += 1
        except Exception as e:
            fail += 1
            logger.warning(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
    
    await message.answer(f"✅ Отправлено: {success}\n❌ Ошибок: {fail}")
    await state.clear()

@admin_router.message(Command("users_count"))
async def users_count(message: types.Message):
    """Обработчик команды /users_count"""
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("У вас нет доступа к этой команде.")
        logger.warning(f"User {user_id} attempted to access /users_count without permission")
        return

    try:
        count = get_users_count()
        await message.answer(f"Общее количество пользователей: {count}")
        logger.info(f"User {user_id} requested users count: {count}")
    except Exception as e:
        await message.answer(f"Ошибка при получении данных: {str(e)}. Попробуйте позже.")
        logger.error(f"Failed to get users count for user {user_id}: {e}")

@admin_router.message(Command("active_users"))
async def active_users(message: types.Message):
    """Обработчик команды /active_users"""
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("У вас нет доступа к этой команде.")
        logger.warning(f"User {user_id} attempted to access /active_users without permission")
        return

    try:
        count = get_active_users_count()
        await message.answer(f"Количество активных пользователей: {count}")
        logger.info(f"User {user_id} requested active users count: {count}")
    except Exception as e:
        await message.answer(f"Ошибка при получении данных: {str(e)}. Попробуйте позже.")
        logger.error(f"Failed to get active users count for user {user_id}: {e}")

@admin_router.message(Command("inactive_users"))
async def inactive_users(message: types.Message):
    """Обработчик команды /inactive_users"""
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("У вас нет доступа к этой команде.")
        logger.warning(f"User {user_id} attempted to access /inactive_users without permission")
        return

    try:
        count = get_inactive_users_count()
        await message.answer(f"Количество неактивных пользователей: {count}")
        logger.info(f"User {user_id} requested inactive users count: {count}")
    except Exception as e:
        await message.answer(f"Ошибка при получении данных: {str(e)}. Попробуйте позже.")
        logger.error(f"Failed to get inactive users count for user {user_id}: {e}")

@admin_router.message(Command("income"))
async def income(message: types.Message):
    """Обработчик команды /income"""
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("У вас нет доступа к этой команде.")
        logger.warning(f"User {user_id} attempted to access /income without permission")
        return

    try:
        total_income = get_income()
        await message.answer(f"Общий доход: {total_income} руб.")
        logger.info(f"User {user_id} requested income: {total_income} руб.")
    except Exception as e:
        await message.answer(f"Ошибка при получении данных: {str(e)}. Попробуйте позже.")
        logger.error(f"Failed to get income for user {user_id}: {e}")