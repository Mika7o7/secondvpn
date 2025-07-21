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


    def create_user(self, tg_id, name='', xpiry_days=3):
        """Создаём нового пользователя в Marzban"""
        try:
            # Генерируем базовое имя пользователя
            base_username = f"user_{tg_id}_{uuid.uuid4().hex[:8]}"
            username = base_username
            attempt = 0
            max_attempts = 5

            # Проверяем уникальность имени, добавляя номер при необходимости
            while attempt < max_attempts:
                try:
                    response = self.get(f"/api/user/{username}")
                    if response.status_code == 404:
                        break  # Имя свободно
                    logger.info(f"Username {username} already exists, trying with suffix")
                    attempt += 1
                    username = f"{base_username}_{attempt}"
                except Exception as e:
                    logger.error(f"Error checking username {username}: {str(e)}")
                    if response.status_code != 404:
                        raise
            if attempt >= max_attempts:
                raise Exception(f"Could not generate a unique username after {max_attempts} attempts")

            vless_id = str(uuid.uuid4())
            expire_timestamp = int((datetime.now() + timedelta(days=xpiry_days)).timestamp())

            data = {
                "username": username,
                "proxies": {
                    "vless": {
                        "id": vless_id,
                        "flow": "xtls-rprx-vision"
                    }
                },
                "inbounds": {
                    "vless": ["VLESS TCP REALITY"]
                },
                "expire": expire_timestamp,
                "data_limit": 0,
                "data_limit_reset_strategy": "no_reset",
                "status": "active",
                "note": f"VPN for tg_id {tg_id}"
            }

            response = self.post("/api/user", data, max_retries=0)  # Без повторов
            response_data = response.json()
            if response.status_code != 200 or not response_data.get("username"):
                logger.error(f"Failed to create user {username}: {response.status_code} - {response.text}")
                raise Exception(f"Failed to create user: {response.status_code} - {response.text}")

            subscription_url = response_data.get("subscription_url", "")
            if not subscription_url:
                logger.error(f"No subscription_url in response: {response_data}")
                raise Exception("No subscription_url found in response")

            logger.info(f"Created user {username} with subscription_url: {subscription_url}")
            return subscription_url, username

        except Exception as e:
            logger.error(f"Failed to create user for tg_id {tg_id}: {str(e)}")
            raise

    def update_user(self, username, data):
        """Обновляем пользователя в Marzban"""
        response = self.put(f"/api/user/{username}", data)
        if not response.get("username"):
            raise Exception(f"Failed to update user {username}: Invalid response {response}")
        logger.info(f"Updated user {username} with data: {data}")
        return response
