from config import VLESS_CONFIG

def generate_vless_link(tg_id, client_id, port, public_key, short_id):
    """Генерирует VLESS-ссылку"""
    vless = (
        f"vless://{client_id}@{VLESS_CONFIG['server_address']}:{port}?"
        f"type=tcp&security=reality&pbk={public_key}&fp={VLESS_CONFIG['fingerprint']}"
        f"&sni={VLESS_CONFIG['sni']}&sid={short_id}&spx={VLESS_CONFIG['spider_x']}"
        f"&flow=xtls-rprx-vision#{tg_id}-user_{tg_id}@example.com"
    )
    return vless