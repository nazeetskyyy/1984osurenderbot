#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram бот для рендера osu! реплеев через o!rdr
Версия: 1.0.0
"""

import sys
from pathlib import Path

# Добавляем путь к проекту в sys.path
sys.path.append(str(Path(__file__).parent.parent))

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters
)
from loguru import logger

from bot.config import TELEGRAM_TOKEN, DEBUG, MESSAGES
from bot.handlers import (
    start_command,
    help_command,
    status_command,
    handle_document
)
from bot.utils import setup_logger, clean_temp_files
from bot.ordr_api import ordr_api


def main():
    """Главная функция запуска бота"""

    # Настраиваем логирование
    setup_logger()
    logger.info("=" * 50)
    logger.info("Запуск бота для рендера osu! реплеев")
    logger.info("=" * 50)

    # Проверяем наличие API ключа
    if not ordr_api.api_key:
        logger.error("API ключ o!rdr не найден!")
        sys.exit(1)

    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))

    # Добавляем обработчик документов
    application.add_handler(
        MessageHandler(filters.Document.ALL, handle_document)
    )

    # Очищаем старые временные файлы при запуске
    clean_temp_files()

    # Запускаем бота
    logger.info("Бот запущен и готов к работе!")

    if DEBUG:
        logger.warning("Бот работает в режиме DEBUG")

    try:
        # Запускаем polling
        application.run_polling(
            allowed_updates=['message', 'callback_query'],
            drop_pending_updates=True
        )
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        logger.info("Завершение работы бота")
        # Финальная очистка
        clean_temp_files()


if __name__ == '__main__':
    main()