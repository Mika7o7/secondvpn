def get_referrer_code(tg_id: int) -> str:
    return f"ref{tg_id}"

def get_tg_id_by_referrer_code(code: str) -> int | None:
    if code.startswith("ref"):
        try:
            return int(code[3:])
        except:
            return None
    return None

def apply_referral(tg_id: int, referrer_code: str):
    """Вызывается при первом платеже нового пользователя"""
    referrer_id = get_tg_id_by_referrer_code(referrer_code)
    if not referrer_id or referrer_id == tg_id:
        return False
        
    # Проверяем, что такого реферала ещё не было
    with sqlite3.connect(SUBSCRIPTION_CONFIG['db_path']) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM referrals WHERE referrer_tg_id = ? AND invited_tg_id = ?", (referrer_id, tg_id))
        if cursor.fetchone():
            return False
            
        # Добавляем рефералку
        cursor.execute("""
            INSERT INTO referrals (referrer_tg_id, invited_tg_id) VALUES (?, ?)
        """, (referrer_id, tg_id))
        
        # Даём рефереру бонус (например +7 дней)
        cursor.execute("""
            UPDATE clients SET bonus_days = bonus_days + 7 WHERE tg_id = ?
        """, (referrer_id,))
        conn.commit()
        
    logger.info(f"Referral bonus +7 days to {referrer_id} from new user {tg_id}")
    return True