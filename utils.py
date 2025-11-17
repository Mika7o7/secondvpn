import re
import secrets
import string

def generate_marzban_username(base_name: str, device_name: str, is_trial: bool = False) -> str:
    """
    Генерирует имя для Marzban:
    никнейм_устройство_abc  или  id123456789_устройство_abc
    """
    # 1. Базовое имя — username или tg_id
    if base_name and not base_name.startswith("user_") and "@" not in base_name:
        clean_base = re.sub(r'[^a-zA-Z0-9_]', '', base_name.lower())
        if not clean_base:
            clean_base = f"id{secrets.token_hex(4)}"
    else:
        clean_base = f"id{secrets.token_hex(8)}"  # fallback

    # 2. Устройство (очищаем и обрезаем)
    clean_device = re.sub(r'[^a-zA-Z0-9]', '', device_name.lower())[:16]
    if not clean_device:
        clean_device = "key"

    # 3. Префикс: trial или устройство
    prefix = "trial" if is_trial else clean_device

    # 4. 3 случайных символа
    random_part = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(3))

    # Без user_ — чисто и красиво
    return f"{clean_base}_{prefix}_{random_part}"