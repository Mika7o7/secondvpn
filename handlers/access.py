# from aiogram import Router, types, F
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from datetime import datetime, timedelta
# import random
# import string
# import asyncio
# from database import save_key, get_access_keys, get_client
# from controlers.add_client import add_client
# from handlers.payments import payment_verification_decorator, DISCOUNTED_PRICES, generate_payment_token, PAYMENT_URL, cloudtips, create_new_key_action

# access_router = Router()

# # Класс для FSM
# class AddAccess(StatesGroup):
#     awaiting_months = State()
#     awaiting_payment = State()

# # Обработчик для кнопки "Добавить точку" (с оплатой)
# @access_router.callback_query(F.data == "add_access")
# async def add_access(callback: types.CallbackQuery, state: FSMContext):
#     await state.clear()
#     price_list = "\n".join([f"{m} мес. — {p} руб." for m, p in DISCOUNTED_PRICES.items()])
#     await callback.message.answer(
#         f"💾 Добавление нового ключа для Zion:\n{price_list}\n\nВыберите срок действия нового ключа (в месяцах):",
#         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
#             [InlineKeyboardButton(text=str(months), callback_data=f"add_months:{months}") for months in [1, 3, 6, 12]]
#         ])
#     )
#     await state.set_state(AddAccess.awaiting_months)
#     await callback.answer()

# # Обработчик выбора количества месяцев
# @access_router.callback_query(AddAccess.awaiting_months, F.data.startswith("add_months:"))
# async def process_add_months(callback: types.CallbackQuery, state: FSMContext):
#     user_id = callback.from_user.id
#     months = int(callback.data.split(":")[1])

#     if months not in DISCOUNTED_PRICES:
#         await callback.message.answer("Пожалуйста, выберите 1, 3, 6 или 12 месяцев.")
#         await callback.answer()
#         return

#     payment_token = generate_payment_token()
#     amount = DISCOUNTED_PRICES[months]
#     token_created = datetime.now().isoformat() + "+03:00"
#     name = f"user_{user_id}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"

#     await state.update_data(
#         token=payment_token,
#         months=months,
#         amount=amount,
#         name=name,
#         token_created=token_created
#     )

#     warning_text = (
#         f"⚠️ <b>Внимание!</b>\n"
#         f"Чтобы <b>оплата прошла автоматически</b>, обязательно укажи в комментарии к платежу этот код:\n\n"
#         f"<code>{payment_token}</code>"
#     )
#     await callback.message.answer(warning_text, parse_mode="HTML")

#     await asyncio.sleep(4)

#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="💾 Оплатить", url=PAYMENT_URL)],
#         [InlineKeyboardButton(text="✅ Я оплатил", callback_data="confirm_add_payment")]
#     ])

#     await callback.message.answer(
#         f"💰 {amount} руб. за {months} мес. для нового ключа.\n"
#         f"После оплаты не забудь нажать <b>«Я оплатил»</b>.",
#         reply_markup=keyboard,
#         parse_mode="HTML"
#     )

#     await state.set_state(AddAccess.awaiting_payment)
#     await callback.answer()

# # Обработчик подтверждения оплаты для создания ключа
# @access_router.callback_query(F.data == "confirm_add_payment")
# @payment_verification_decorator
# async def confirm_add_payment(call: types.CallbackQuery, state: FSMContext, user_id: int, username: str, amount: float, expected_amount: float, months: int, effective_months: float):
#     try:
#         message, keyboard = await create_new_key_action(
#             user_id=user_id,
#             username=username,
#             amount=amount,
#             expected_amount=expected_amount,
#             months=months,
#             effective_months=effective_months
#         )
#         await call.message.answer(message, reply_markup=keyboard, parse_mode="HTML")
#         await state.clear()
#     except Exception as e:
#         await call.message.answer(f"✅ Ключ не удалось создать. Свяжитесь с Оракулом: {str(e)}.")
#         await state.clear()

# # Обработчик для тестового ключа (без оплаты)
# @access_router.callback_query(F.data == "add_test_access")
# async def add_test_access(callback: types.CallbackQuery, state: FSMContext):
#     tg_id = callback.from_user.id
#     telegram_username = callback.from_user.username or "unknown"

#     subscription_url, username = add_client(tg_id, telegram_username, xpiry_days=3)

#     existing_keys = get_access_keys(tg_id)
#     name = f"Ключ_{len(existing_keys) + 1}"

#     expires_at = (datetime.now() + timedelta(days=3)).isoformat()
#     save_key(tg_id, subscription_url, username, name, expires_at)

#     keys = get_access_keys(tg_id)

#     if not keys:
#         await callback.message.answer("Ключей пока нет.")
#     else:
#         text = "🔐 Твои ключи:\n\n"
#         for idx, (key_id, key_val, expires_at, key_name) in enumerate(keys, start=1):
#             short_key = f"{key_val[:4]}...{key_val[-4:]}"
#             expire_str = datetime.fromisoformat(expires_at).strftime("%d.%m.%Y") if expires_at else "∞"
#             text += f"{key_name}: <code>{short_key}</code> — до {expire_str}\n"

#         await callback.message.answer(text, parse_mode="HTML")

#     await callback.answer()