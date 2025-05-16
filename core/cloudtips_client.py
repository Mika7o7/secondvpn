
import aiohttp
import json
import os
import time
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudTipsClient:
    def __init__(self, client_id: str, token_file: str):
        self.client_id = client_id
        self.token_file = token_file
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = 0
        self.load_tokens()

    def save_tokens(self):
        """Сохранение токенов в файл."""
        data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_expiry": self.token_expiry
        }
        try:
            with open(self.token_file, "w") as f:
                json.dump(data, f)
            logger.info(f"Токены сохранены в {self.token_file}")
        except Exception as e:
            logger.error(f"Ошибка сохранения токенов: {str(e)}")

    def load_tokens(self):
        """Загрузка токенов из файла."""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file) as f:
                    data = json.load(f)
                    self.access_token = data.get("access_token")
                    self.refresh_token = data.get("refresh_token")
                    self.token_expiry = data.get("token_expiry", 0)
                logger.info(f"Токены загружены из {self.token_file}: access_token={self.access_token[:10]}..., expiry={self.token_expiry}")
            except Exception as e:
                logger.error(f"Ошибка загрузки токенов из {self.token_file}: {str(e)}")
                raise
        else:
            logger.error(f"Файл {self.token_file} не найден")
            raise Exception(f"Файл {self.token_file} не найден")

    async def refresh_tokens(self):
        """Обновление токенов."""
        logger.info("Обновляем токены...")
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post("https://identity.cloudtips.ru/connect/token", data=data, headers=headers) as response:
                    logger.info(f"Ответ от /connect/token: status={response.status}")
                    response.raise_for_status()
                    tokens = await response.json()
                    logger.info(f"Получены новые токены: expires_in={tokens.get('expires_in')}")
                    self.access_token = tokens["access_token"]
                    self.refresh_token = tokens["refresh_token"]
                    self.token_expiry = int(time.time()) + tokens.get("expires_in", 3600) - 60
                    self.save_tokens()
                    logger.info("Токены успешно обновлены и сохранены")
            except Exception as e:
                logger.error(f"Ошибка обновления токенов: {str(e)}")
                raise

    async def ensure_token_valid(self):
        """Проверка валидности токена."""
        current_time = int(time.time())
        logger.info(f"Проверка токена: current_time={current_time}, token_expiry={self.token_expiry}")
        if self.access_token is None or current_time >= self.token_expiry:
            if self.refresh_token is None:
                logger.error("Нет refresh_token, нужно предоставить новый")
                raise Exception("Нет refresh_token, нужно предоставить новый")
            logger.info(f"Токен истёк или отсутствует, обновляем")
            await self.refresh_tokens()

    async def get_timeline(self, date_from: Optional[str] = None, date_to: Optional[str] = None, page: int = 1, limit: int = 50):
        """Получение транзакций через /api/timeline с фильтрацией по дате."""
        logger.info(f"Выполняем запрос /api/timeline: page={page}, limit={limit}, dateFrom={date_from}, dateTo={date_to}")
        await self.ensure_token_valid()
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {"page": page, "limit": limit}
        if date_from:
            params["dateFrom"] = date_from
        if date_to:
            params["dateTo"] = date_to
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://api.cloudtips.ru/api/timeline", headers=headers, params=params) as response:
                    logger.info(f"Ответ от /api/timeline: status={response.status}")
                    response.raise_for_status()
                    data = await response.json()
                    logger.info(f"Данные от /api/timeline: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    return data
            except Exception as e:
                logger.error(f"Ошибка получения timeline: {str(e)}")
                raise