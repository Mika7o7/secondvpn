from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def vless_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🪟 Windows", url="https://storage.v2raytun.com/v2RayTun_Setup.exe"),
                InlineKeyboardButton(text="🍏 macOS/IOS", url="https://apps.apple.com/en/app/v2raytun/id6476628951")
            ],
            [   
                InlineKeyboardButton(text="🤖 Android", url="https://play.google.com/store/apps/details?id=com.v2raytun.android"),
                InlineKeyboardButton(text="🐧 Linux", url="https://github.com/hiddify/hiddify-app/releases/latest/download/Hiddify-Linux-x64.AppImage")
            ],
            [
                InlineKeyboardButton(text="💊", callback_data="copy_vless")
            ]
        ]
    )

def extend_keyboard():
    """Клавиатура с кнопкой Продлить"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💳 Продлить", callback_data="extend_subscription")]
            ])
    return keyboard

