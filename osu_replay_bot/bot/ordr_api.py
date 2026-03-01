from pathlib import Path
from typing import Optional, Dict, Any

import aiohttp
from loguru import logger

from .config import ORDR_API_KEY


class ORDRAPI:
    """Класс для работы с o!rdr API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://ordr.issou.best/api"

    async def send_replay(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Отправка реплея на рендеринг

        Args:
            file_path: путь к .osr файлу

        Returns:
            dict: ответ от API или None при ошибке
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Подготавливаем данные
                data = aiohttp.FormData()
                data.add_field('apiKey', self.api_key)
                data.add_field(
                    'file',
                    open(file_path, 'rb'),
                    filename=file_path.name,
                    content_type='application/octet-stream'
                )

                # Отправляем запрос
                async with session.post(
                        f"{self.base_url}/render",
                        data=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Рендер создан: {result.get('renderId')}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка API: {response.status} - {error_text}")
                        return None

        except Exception as e:
            logger.error(f"Ошибка при отправке в o!rdr: {e}")
            return None

    async def check_status(self, render_id: str) -> Optional[Dict[str, Any]]:
        """
        Проверка статуса рендера

        Args:
            render_id: ID рендера

        Returns:
            dict: статус рендера или None при ошибке
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        f"{self.base_url}/render/{render_id}",
                        params={'apiKey': self.api_key}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Ошибка проверки статуса: {response.status}")
                        return None

        except Exception as e:
            logger.error(f"Ошибка при проверке статуса: {e}")
            return None


# Создаем экземпляр API
ordr_api = ORDRAPI(ORDR_API_KEY)