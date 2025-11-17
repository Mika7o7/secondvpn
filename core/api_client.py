import requests
import logging
import os
import json
from datetime import datetime, timedelta
import uuid
import time
from requests.exceptions import RequestException, HTTPError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/tmp/vpn_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, config):
        self.host = config["host"]
        self.username = config["username"]
        self.password = config["password"]
        self.token_file = config["token_file"]
        self.token = self.load_token()
        self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else None
        self.max_retries = 3
        self.retry_delay = 5

    def load_token(self):
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, "r") as f:
                    token = f.read().strip()
                    logger.info(f"Loaded token from {self.token_file}")
                    return token
            return None
        except Exception as e:
            logger.error(f"Failed to load token from {self.token_file}: {e}")
            return None

    def save_token(self, token):
        try:
            with open(self.token_file, "w") as f:
                f.write(token)
            logger.info(f"Saved token to {self.token_file}")
        except Exception as e:
            logger.error(f"Failed to save token to {self.token_file}: {e}")

    def login(self):
        hosts = [self.host]
        
        for host in hosts:
            url = f"{host}/api/admin/token"
            data = {
                "username": self.username,
                "password": self.password,
                "grant_type": "password"
            }
            headers = {"Content-Type": "application/json"}
            logger.info(f"Attempting to login to Marzban at {url}")
            for attempt in range(self.max_retries):
                try:
                    resp = requests.post(url, json=data, headers=headers, timeout=10)
                    if resp.status_code != 200:
                        headers = {"Content-Type": "application/x-www-form-urlencoded"}
                        resp = requests.post(url, data=data, headers=headers, timeout=10)
                    resp.raise_for_status()
                    data = resp.json()
                    self.token = data.get("access_token")
                    if not self.token:
                        raise Exception(f"No access token received. Response: {resp.text}")
                    self.save_token(self.token)
                    self.headers = {"Authorization": f"Bearer {self.token}"}
                    logger.info(f"Login successful using {host}")
                    return
                except (RequestException, HTTPError) as e:
                    logger.warning(f"Login attempt {attempt + 1} failed on {host}: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
            logger.error(f"Login failed on {host} after {self.max_retries} attempts")
        raise Exception(f"Login failed on all hosts: {hosts}")

    def check_token(self):
        if not self.token or not self.headers:
            logger.info("No token available")
            return False
        hosts = [self.host]
        
        for host in hosts:
            url = f"{host}/api/admin"
            try:
                resp = requests.get(url, headers=self.headers, timeout=5)
                if resp.status_code == 200:
                    logger.info(f"Token is valid on {host}")
                    return True
                logger.warning(f"Token is invalid on {host}, status code: {resp.status_code}")
            except RequestException as e:
                logger.error(f"Token check failed on {host}: {e}")
        return False

    def post(self, endpoint, data=None):
        if not self.check_token():
            self.login()
        hosts = [self.host]
        
        
        for host in hosts:
            url = f"{host}{endpoint}"
            logger.info(f"POST request to {url} with data: {data}")
            for attempt in range(self.max_retries):
                try:
                    resp = requests.post(url, json=data or {}, headers=self.headers, timeout=10)
                    resp.raise_for_status()
                    if not resp.text.strip():
                        logger.error("Empty response received")
                        raise Exception("Empty response received from server")
                    response_data = resp.json()
                    logger.info(f"POST response from {host}: {response_data}")
                    return response_data
                except (RequestException, HTTPError) as e:
                    logger.warning(f"POST attempt {attempt + 1} failed on {host}: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
            logger.error(f"POST request failed on {host} after {self.max_retries} attempts")
        raise Exception(f"POST request failed on all hosts: {hosts}")

    def put(self, endpoint, data=None):
        if not self.check_token():
            self.login()
        hosts = [self.host]
        
        
        for host in hosts:
            url = f"{host}{endpoint}"
            logger.info(f"PUT request to {url} with data: {data}")
            for attempt in range(self.max_retries):
                try:
                    resp = requests.put(url, json=data or {}, headers=self.headers, timeout=10)
                    resp.raise_for_status()
                    response_data = resp.json()
                    logger.info(f"PUT response from {host}: {response_data}")
                    return response_data
                except (RequestException, HTTPError) as e:
                    logger.warning(f"PUT attempt {attempt + 1} failed on {host}: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
            logger.error(f"PUT request failed on {host} after {self.max_retries} attempts")
        raise Exception(f"PUT request failed on all hosts: {hosts}")

    def get(self, endpoint):
        if not self.check_token():
            self.login()
        hosts = [self.host]
        
        
        for host in hosts:
            url = f"{host}{endpoint}"
            logger.info(f"GET request to {url}")
            for attempt in range(self.max_retries):
                try:
                    resp = requests.get(url, headers=self.headers, timeout=10)
                    resp.raise_for_status()
                    return resp.json()
                except (RequestException, HTTPError) as e:
                    logger.warning(f"GET attempt {attempt + 1} failed on {host}: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
            logger.error(f"GET request failed on {host} after {self.max_retries} attempts")
        raise Exception(f"GET request failed on all hosts: {hosts}")

    def delete(self, endpoint):
        if not self.check_token():
            self.login()
        hosts = [self.host]
        
        
        for host in hosts:
            url = f"{host}{endpoint}"
            logger.info(f"DELETE request to {url}")
            for attempt in range(self.max_retries):
                try:
                    resp = requests.delete(url, headers=self.headers, timeout=10)
                    resp.raise_for_status()
                    logger.info(f"Response status from {host}: {resp.status_code}")
                    return {"success": True}
                except (RequestException, HTTPError) as e:
                    logger.warning(f"DELETE attempt {attempt + 1} failed on {host}: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
            logger.error(f"DELETE request failed on {host} after {self.max_retries} attempts")
        raise Exception(f"DELETE request failed on all hosts: {hosts}")

    def create_user(self, tg_id: int, username: str = '', expiry_days: int = 3, is_trial: bool = False):
        vless_id = str(uuid.uuid4())
    
        if is_trial or expiry_days <= 3:
            payload = {
                "username": username,
                "proxies": {"vless": {"id": vless_id, "flow": "xtls-rprx-vision"}},
                "inbounds": {"vless": ["VLESS TCP REALITY"]},
                "expire": 0,
                "status": "on_hold",
                "on_hold_expire_duration": 259200,
                "note": f"Trial for tg_id {tg_id}"
            }
        else:
            expire_ts = int((datetime.now() + timedelta(days=expiry_days)).timestamp())
            payload = {
                "username": username,
                "proxies": {"vless": {"id": vless_id, "flow": "xtls-rprx-vision"}},
                "inbounds": {"vless": ["VLESS TCP REALITY"]},
                "expire": expire_ts,
                "status": "active",
                "note": f"Paid key for tg_id {tg_id} ({expiry_days} days)"
            }
    
        # Твой self.post() возвращает dict
        response = self.post("/api/user", data=payload)
    
        # === ПРОВЕРКА ОШИБОК ===
        if not isinstance(response, dict):
            raise Exception(f"Marzban вернул не JSON: {response}")
    
        if "detail" in response or "username" not in response:
            error_msg = response.get("detail", str(response))
            logger.error(f"Marzban create failed: {error_msg}")
            raise Exception(f"Marzban error: {error_msg}")
    
        user_data = response
    
        # ВАЖНО: берём subscription_url напрямую — без self.base_url!
        sub_url = user_data["subscription_url"]
        if not sub_url.startswith("http"):
            # Если Marzban отдал только путь — добавляем домен из конфига
            sub_url = f"https://ggwpvpn.duckdns.org:8000{sub_url}"
    
        logger.info(f"Создан пользователь {username} → {'триал' if is_trial else f'{expiry_days} дней'}")
        return sub_url, user_data["username"]

    def update_user(self, username, data):
        """Обновляем пользователя в Marzban"""
        response = self.put(f"/api/user/{username}", data)
        if not response.get("username"):
            raise Exception(f"Failed to update user {username}: Invalid response {response}")
        logger.info(f"Updated user {username} with data: {data}")
        return response

    def get_expired_users(self, limit=30, sort="-created_at"):
        """Получает пользователей со статусом 'expired'"""
        endpoint = f"/api/users?limit={limit}&sort={sort}&status=expired"
        return self.get(endpoint)
