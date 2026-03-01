import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Базовая директория проекта
BASE_DIR = Path(__file__).parent.parent

# Настройки бота
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TELEGRAM_TOKEN:
    raise ValueError("Нет TELEGRAM_TOKEN в .env файле!")

# Настройки o!rdr
ORDR_API_KEY = os.getenv('ORDR_API_KEY')
ORDR_API_URL = "https://ordr.issou.best/api/render"
ORDR_STATUS_URL = "https://ordr.issou.best/api/render/{}"

# Пути к папкам
TEMP_DIR = BASE_DIR / "temp"
LOGS_DIR = BASE_DIR / "logs"

# Создаем нужные папки
TEMP_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Настройки
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 10))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Сообщения для пользователя
MESSAGES = {
    'start': """
👋 Привет! Я бот для рендера osu! реплеев.

Просто отправь мне файл .osr, и я отправлю его на рендеринг в o!rdr!

Команды:
/help - показать помощь
/status - проверить статус бота
    """,

    'help': """
📚 Как пользоваться ботом:

1. Сохрани свой реплей в osu! (файл .osr)
2. Отправь этот файл мне
3. Я отправлю его на сервер o!rdr для рендеринга
4. Когда видео будет готово, ты получишь ссылку

⚠️ Файл должен иметь расширение .osr
Максимальный размер файла: {} MB
    """,

    'wrong_file': "❌ Пожалуйста, отправь файл с расширением .osr",

    'file_too_big': "❌ Файл слишком большой! Максимальный размер: {} MB",

    'processing': "📥 Получил файл! Начинаю обработку...",

    'saved': "✅ Файл {filename} сохранен\n🔄 Отправляю на рендеринг в o!rdr...",

    'sent': """
✅ Файл отправлен на рендеринг!
🆔 ID задачи: {render_id}

⏳ Обычно это занимает 1-5 минут.
Я пришлю ссылку, когда видео будет готово!
    """,

    'ordr_error': "❌ Ошибка при отправке на o!rdr. Попробуй позже.",

    'error': "❌ Произошла ошибка: {error}",

    'still_processing': "⏳ Рендер все еще в процессе... Подожди еще немного.",

    'status_ok': "✅ Бот работает и готов принимать файлы!"
}