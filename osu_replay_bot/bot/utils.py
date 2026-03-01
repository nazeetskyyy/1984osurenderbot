import os
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime
from loguru import logger

# Настройка логирования
logger.add(
    "logs/bot_{time}.log",
    rotation="500 MB",
    retention="10 days",
    format="{time} {level} {message}"
)


def setup_logger():
    """Настройка логгера"""
    return logger


def clean_temp_files(max_age_hours: int = 24):
    """Очистка старых временных файлов"""
    temp_dir = Path("temp")
    if not temp_dir.exists():
        return

    current_time = datetime.now().timestamp()
    for file in temp_dir.glob("*"):
        if file.is_file():
            file_age = current_time - file.stat().st_mtime
            if file_age > max_age_hours * 3600:
                file.unlink()
                logger.info(f"Удален старый файл: {file}")


def get_file_size_mb(file_path: Path) -> float:
    """Получить размер файла в MB"""
    return file_path.stat().st_size / (1024 * 1024)


def safe_delete_file(file_path: Path):
    """Безопасное удаление файла"""
    try:
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Файл удален: {file_path}")
    except Exception as e:
        logger.error(f"Ошибка при удалении файла {file_path}: {e}")


def format_size(size_bytes: int) -> str:
    """Форматирование размера файла"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"