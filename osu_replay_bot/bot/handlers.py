import asyncio

from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from .config import MESSAGES, TEMP_DIR, MAX_FILE_SIZE_MB
from .ordr_api import ordr_api
from .utils import safe_delete_file, format_size


async def start_command(update: Update):
    """Обработчик /start"""
    await update.message.reply_text(MESSAGES['start'])


async def help_command(update: Update):
    """Обработчик /help"""
    await update.message.reply_text(
        MESSAGES['help'].format(MAX_FILE_SIZE_MB)
    )


async def status_command(update: Update):
    """Обработчик /status"""
    await update.message.reply_text(MESSAGES['status_ok'])


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик полученных файлов"""
    document = update.message.document
    file_name = document.file_name

    # Проверяем расширение файла
    if not file_name.endswith('.osr'):
        await update.message.reply_text(MESSAGES['wrong_file'])
        return

    # Проверяем размер файла
    file_size_mb = document.file_size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        await update.message.reply_text(
            MESSAGES['file_too_big'].format(MAX_FILE_SIZE_MB)
        )
        return

    # Отправляем сообщение о начале обработки
    status_msg = await update.message.reply_text(MESSAGES['processing'])

    file_path = None
    try:
        # Скачиваем файл
        file = await context.bot.get_file(document.file_id)
        file_path = TEMP_DIR / file_name
        await file.download_to_drive(file_path)

        logger.info(f"Файл сохранен: {file_name}, размер: {format_size(document.file_size)}")

        await status_msg.edit_text(
            MESSAGES['saved'].format(filename=file_name)
        )

        # Отправляем в o!rdr
        render_result = await ordr_api.send_replay(file_path)

        if render_result and 'renderId' in render_result:
            render_id = render_result['renderId']

            # Сохраняем ID в контексте пользователя
            if 'renders' not in context.user_data:
                context.user_data['renders'] = []
            context.user_data['renders'].append({
                'render_id': render_id,
                'file_name': file_name,
                'status': 'pending'
            })

            await status_msg.edit_text(
                MESSAGES['sent'].format(render_id=render_id)
            )

            # Запускаем проверку статуса
            asyncio.create_task(
                monitor_render(render_id, update.effective_chat.id, context)
            )

        else:
            await status_msg.edit_text(MESSAGES['ordr_error'])

    except Exception as e:
        logger.error(f"Ошибка при обработке файла: {e}")
        await status_msg.edit_text(
            MESSAGES['error'].format(error=str(e)[:100])
        )

    finally:
        # Удаляем временный файл
        if file_path and file_path.exists():
            safe_delete_file(file_path)


async def monitor_render(render_id: str, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """
    Мониторинг статуса рендера

    Проверяет статус каждые 10 секунд в течение 5 минут
    """
    max_attempts = 30  # 30 * 10 секунд = 5 минут
    attempt = 0

    while attempt < max_attempts:
        try:
            # Ждем перед проверкой
            await asyncio.sleep(10)

            # Проверяем статус
            status = await ordr_api.check_status(render_id)

            if status:
                logger.info(f"Статус рендера {render_id}: {status.get('status')}")

                # Если видео готово
                if status.get('status') == 'completed':
                    video_url = status.get('videoUrl')
                    if video_url:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=f"✅ Видео готово!\n🎥 Скачать: {video_url}"
                        )
                    else:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text="✅ Видео готово, но ссылка временно недоступна. Проверь позже."
                        )
                    break

                # Если ошибка
                elif status.get('status') == 'failed':
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text="❌ К сожалению, рендер не удался. Попробуй другой файл."
                    )
                    break

            attempt += 1

            # На половине пути отправляем напоминание
            if attempt == max_attempts // 2:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=MESSAGES['still_processing']
                )

        except Exception as e:
            logger.error(f"Ошибка при мониторинге рендера {render_id}: {e}")
            break

    # Если время вышло
    if attempt >= max_attempts:
        await context.bot.send_message(
            chat_id=chat_id,
            text="⏰ Время ожидания истекло. Проверь статус позже вручную на сайте o!rdr."
        )