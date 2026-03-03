<<<<<<< HEAD
import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
import keyboards as kb
import re

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

user_data = {}

load_dotenv()
CHANNEL_ID_=os.getenv("CHANNEL_ID_")
CHANNEL_ID=CHANNEL_ID_


def validate_phone(phone: str) -> bool:
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)

    if not cleaned.isdigit():
        return False

    if len(cleaned) < 10 or len(cleaned) > 12:
        return False

    if len(cleaned) == 11 and cleaned[0] in ['7', '8']:
        return True

    elif len(cleaned) == 10 and cleaned[0] in ['9']:
        return True

    elif len(cleaned) == 12 and cleaned[:2] == '79':
        return True

    return False


def format_phone(phone: str) -> str:
    cleaned = re.sub(r'[^\d]', '', phone)

    if len(cleaned) == 11 and cleaned[0] in ['7', '8']:
        return f"+7 ({cleaned[1:4]}) {cleaned[4:7]}-{cleaned[7:9]}-{cleaned[9:11]}"
    elif len(cleaned) == 10:
        return f"+7 ({cleaned[0:3]}) {cleaned[3:6]}-{cleaned[6:8]}-{cleaned[8:10]}"
    elif len(cleaned) == 12 and cleaned[:2] == '79':
        return f"+{cleaned[0:2]} ({cleaned[2:5]}) {cleaned[5:8]}-{cleaned[8:10]}-{cleaned[10:12]}"
    else:
        return phone


@dp.message(Command("start"))
async def start(message: Message):
    user_data[message.from_user.id] = {
        "format": None,
        "script": None,
        "audio": False,
        "name": None,
        "phone": None,
        "hours": None,
        "experience": None,
        "awaiting_contact": True
    }
    await message.answer("Здравствуйте! Представьтесь и напишите ваш контактный номер.")


@dp.message(F.text)
async def handle_text(message: Message):
    user_id = message.from_user.id

    if user_id not in user_data:
        return

    if user_data[user_id].get("awaiting_contact"):
        text = message.text.strip()
        words = text.split()

        phone = ""
        name_parts = []

        for word in words:
            clean_word = re.sub(r'[\s\-\(\)\+]', '', word)
            if clean_word.isdigit() and len(clean_word) >= 10:
                phone = word
            else:
                name_parts.append(word)

        if not phone:
            numbers = re.findall(r'[\+\d\s\-\(\)]{10,}', text)
            if numbers:
                phone = numbers[0]
                name_text = text.replace(phone, '').strip()
                name_parts = [name_text] if name_text else ["Не указано"]

        name = ' '.join(name_parts) if name_parts else "Не указано"
        if not name or name == "Не указано":
            name = "Имя не указано"

        if phone and validate_phone(phone):
            formatted_phone = format_phone(phone)
            user_data[user_id]["name"] = name
            user_data[user_id]["phone"] = formatted_phone
            user_data[user_id]["awaiting_contact"] = False

            await message.answer('''Здравствуйте!

Это первичный отбор в компанию СтанкоПрессРесурс.

Важно:

У нас не колл-центр и не активные продажи.

Работа — спокойные короткие разговоры с предприятиями по готовой структуре.

Процесс займёт 3–5 минут.
Без аудио-записи отклики не рассматриваются.

Готовы продолжить?
''', reply_markup=kb.first_btns)
        else:
            await message.answer(
                "Пожалуйста, укажите корректный номер телефона (10-12 цифр, например: +79991234567 или 89123456789):")

    else:
        if not message.voice and user_data[user_id].get("audio") is False:
            await message.answer("Пожалуйста, отправьте именно голосовое сообщение.")


@dp.callback_query(F.data == "Yes1")
async def yes_1(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Сколько часов в день готовы работать?", reply_markup=kb.second_btns)


@dp.callback_query(F.data == "No1")
async def no_1(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Спасибо, до свидания.")


@dp.callback_query(F.data.in_(["2-3_hours", "4–5_hours", "6+_hours"]))
async def hours(callback: CallbackQuery):
    await callback.answer()
    hours_map = {
        "2-3_hours": "2-3 часа",
        "4–5_hours": "4-5 часов",
        "6+_hours": "6+ часов"
    }
    user_data[callback.from_user.id]["hours"] = hours_map[callback.data]
    await callback.message.answer("Есть ли опыт телефонных разговоров?", reply_markup=kb.third_btns)


@dp.callback_query(F.data.in_(["b2b", "center", "no experience"]))
async def experience(callback: CallbackQuery):
    await callback.answer()
    exp_map = {
        "b2b": "B2B продажи",
        "center": "Колл-центр",
        "no experience": "Без опыта"
    }
    user_data[callback.from_user.id]["experience"] = exp_map[callback.data]
    await callback.message.answer("Какой формат разговоров вам ближе?", reply_markup=kb.fourth_btns)


@dp.callback_query(F.data.in_(["relax answer", "ready to try"]))
async def relax_answer(callback: CallbackQuery):
    await callback.answer()
    user_data[callback.from_user.id]["format"] = "Спокойные разговоры"
    await callback.message.answer("Готовы работать строго по готовому сценарию разговоров?",
                                  reply_markup=kb.fifth_btns)


@dp.callback_query(F.data.in_(["sell and work"]))
async def sell_and_work(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Спасибо за отклик. Сейчас формат работы отличается от классических продаж.")


@dp.callback_query(F.data.in_(["Yes2", "partially"]))
async def ready_for_audio(callback: CallbackQuery):
    await callback.answer()
    user_data[callback.from_user.id]["script"] = "Да" if callback.data == "Yes2" else "Частично"
    await callback.message.answer(
        """Запишите короткое аудио (20–30 секунд).
Важно: это не продажа и не презентация. Просто спокойная деловая речь.
Скажите своими словами: «Представьтесь и коротко объясните, как вы обычно начинаете рабочий разговор с новым человеком по телефону».""")


@dp.callback_query(F.data == "No2")
async def no2(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Спасибо за отклик. Формат работы предполагает строгую структуру разговоров.")


@dp.message(F.voice)
async def voice_handler(message: Message):
    user_id = message.from_user.id

    voice_duration = message.voice.duration

    if voice_duration < 20:
        await message.answer(
            f"Ваше голосовое сообщение слишком короткое ({voice_duration} сек). Пожалуйста, запишите сообщение длительностью 20-30 секунд.")
        return

    user_data[user_id]["audio"] = True
    user_data[user_id]["audio_duration"] = voice_duration
    await check_conditions(user_id, message)


async def check_conditions(user_id, message: Message = None):
    data = user_data.get(user_id, {})
    if data.get("format") == "Спокойные разговоры" and data.get("script") in ["Да", "Частично"] and data.get("audio"):
        await bot.send_message(
            user_id,
            "Спасибо! Мы посмотрим ответы и прослушаем запись. Если формат совпадает — напишем вам лично."
        )

        if message and message.voice:
            channel_text = f"""Новый кандидат 

Имя: {data.get('name', 'Не указано')}
Телефон: {data.get('phone', 'Не указано')}
Часы: {data.get('hours', 'Не указано')}
Опыт: {data.get('experience', 'Не указано')}
Формат: {data.get('format', 'Не указано')}
Длительность аудио: {data.get('audio_duration', 'Не указано')} сек
Аудио:"""

            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=channel_text
            )

            await bot.send_voice(
                chat_id=CHANNEL_ID,
                voice=message.voice.file_id
            )

        user_data[user_id] = {"format": None, "script": None, "audio": False, "name": None, "phone": None,
                              "hours": None,
                              "experience": None, "awaiting_contact": False}


@dp.message()
async def handle_other(message: Message):
    pass


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
=======
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
from env import BOT_TOKEN, ADMIN_CHAT_ID, GOOGLE_DRIVE_ROOT_FOLDER_ID
from google_drive_oauth import drive_service
import speech_recognition as sr
import tempfile
import subprocess


text_blocks = [
    "Привет! Это бот для проведения устного собеседования.\n\nВам будут заданы вопросы. Отвечайте на них голосовыми сообщениями.\n\nВозвращаться к предыдущим вопросам нельзя.\n\nЖелаем удачи!"
]

question_blocks = [
    ["1. Расскажите о себе."],
    ["2. Как вы решаете сложные задачи?"],
    ["3. Почему мы должны выбрать именно вас?"],
    ["4. Какие языки программирования вы знаете?"],
    ["5. Расскажите о своем последнем проекте."],
    ["6. Приходилось ли вам работать в команде?"],
    ["7. Почему вы выбрали эту профессию?"],
    ["8. Как поддерживаете знания в актуальном состоянии?"]
]

user_sessions = {}

async def download_voice_file(file_id, bot):
    try:
        file = await bot.get_file(file_id)
        file_content = await file.download_as_bytearray()
        logging.info(f"Файл загружен, размер: {len(file_content)} байт")
        return bytes(file_content)
    except Exception as e:
        logging.error(f"Error downloading voice file: {e}")
        return None

async def transcribe_audio(file_content):
    ogg_path = None
    wav_path = None

    try:
        logging.info("Конвертация OGG в WAV...")

        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as ogg_file:
            ogg_file.write(file_content)
            ogg_path = ogg_file.name

        wav_path = ogg_path.replace('.ogg', '.wav')

        result = subprocess.run([
            'ffmpeg.exe',
            '-i', ogg_path,
            '-acodec', 'pcm_s16le',
            '-ac', '1',
            '-ar', '16000',
            '-y',
            wav_path
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0 and os.path.exists(wav_path):
            logging.info("Конвертация успешна, распознаем речь...")

            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio, language='ru-RU')

            logging.info(f"Успешная расшифровка: {text}")
            return text
        else:
            logging.error(f"Ошибка конвертации: {result.stderr}")
            return "Ошибка конвертации аудио"

    except sr.UnknownValueError:
        logging.warning("Речь не распознана")
        return "Речь не распознана"
    except sr.RequestError as e:
        logging.error(f"Ошибка Google Speech API: {e}")
        return "Ошибка сервиса распознавания"
    except Exception as e:
        logging.error(f"Ошибка транскрибации: {e}")
        return f"Ошибка обработки: {str(e)}"
    finally:
        try:
            if ogg_path and os.path.exists(ogg_path):
                os.unlink(ogg_path)
            if wav_path and os.path.exists(wav_path):
                os.unlink(wav_path)
        except Exception as e:
            logging.error(f"Ошибка удаления временных файлов: {e}")

async def create_transcription_file(session):
    try:
        if not session['folder_id']:
            return None

        content = f"РАСШИФРОВКА СОБЕСЕДОВАНИЯ\n"
        content += "=" * 50 + "\n"
        content += f"Кандидат: {session['full_name']}\n"
        content += f"Telegram: @{session['username']}\n"
        content += f"Дата проведения: {session['start_time'].strftime('%d.%m.%Y %H:%M:%S')}\n"
        content += f"Общее время ответов: {sum(voice['duration'] for voice in session['voice_files'])} сек\n"
        content += f"Количество ответов: {len(session['voice_files'])}\n"
        content += "=" * 50 + "\n\n"

        current_question = 0
        for voice in sorted(session['voice_files'], key=lambda x: (x['question_number'], x['voice_count'])):
            if voice['question_number'] != current_question:
                current_question = voice['question_number']
                question_text = question_blocks[current_question - 1][0] if current_question - 1 < len(
                    question_blocks) else f"Вопрос {current_question}"
                content += f"\n{'=' * 30}\n"
                content += f"ВОПРОС {current_question}: {question_text}\n"
                content += f"{'=' * 30}\n"

            content += f"\nОТВЕТ {voice['voice_count']}:\n"
            content += f"Время: {voice['timestamp'].strftime('%H:%M:%S')}\n"
            content += f"Длительность: {voice['duration']} сек\n"
            content += f"Файл: {voice['filename']}\n"
            content += f"Расшифровка:\n{voice['transcription']}\n"
            content += "-" * 40 + "\n"

        filename = f"transcription_{session['start_time'].strftime('%Y%m%d_%H%M%S')}.txt"
        file_id = drive_service.upload_text_file(content.encode('utf-8'), filename, session['folder_id'])

        logging.info(f"Файл расшифровки создан: {filename}")
        return file_id
    except Exception as e:
        logging.error(f"Ошибка создания файла расшифровки: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id

    user_sessions[user_id] = {
        'step': 0,
        'voice_count': 0,
        'username': user.username or f"user_{user_id}",
        'first_name': user.first_name or "",
        'last_name': user.last_name or "",
        'full_name': "",
        'voice_files': [],
        'start_time': datetime.now(),
        'folder_created': False,
        'folder_id': None,
        'folder_url': None,
        'waiting_for_name': True
    }

    await update.message.reply_text(text_blocks[0])
    await update.message.reply_text("📝 Пожалуйста, введите ваше ФИО:")

async def handle_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE, session):
    full_name = update.message.text.strip()

    if len(full_name) < 2:
        await update.message.reply_text("❌ Пожалуйста, введите корректное ФИО (минимум 2 символа):")
        return False

    session['full_name'] = full_name
    session['waiting_for_name'] = False

    await update.message.reply_text(f"✅ ФИО сохранено: {full_name}")

    keyboard = [['Начать тестирование']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text('Теперь нажмите кнопку "Начать тестирование":', reply_markup=reply_markup)

    return True

async def show_next_button(update: Update, context: ContextTypes.DEFAULT_TYPE, session):
    total_questions = len(question_blocks)
    current_step = session['step'] - len(text_blocks)

    if current_step >= total_questions - 1:
        button_text = "Завершить тестирование"
    else:
        button_text = "Следующий вопрос"

    keyboard = [[button_text]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text('Дайте ответ голосовым сообщением, продолжительностью не менее 10 секунд',
                                    reply_markup=reply_markup)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    session = user_sessions.get(user_id)

    if not session:
        await update.message.reply_text("Начните с /start")
        return

    if session.get('waiting_for_name', False):
        await handle_name_input(update, context, session)
        return

    if update.message.text == 'Начать тестирование':
        await handle_next_block(update, context, session)
    elif update.message.text == 'Следующий вопрос' or update.message.text == 'Завершить тестирование':
        await handle_next_block(update, context, session)

async def handle_next_block(update: Update, context: ContextTypes.DEFAULT_TYPE, session):
    user_id = update.message.from_user.id

    total_text_blocks = len(text_blocks)
    total_questions = len(question_blocks)

    if session['step'] >= total_text_blocks and session['step'] < total_text_blocks + total_questions:
        if session['voice_count'] == 0:
            await update.message.reply_text("❌ Сначала ответьте на вопрос голосовым сообщением!")
            return

    session['step'] += 1
    session['voice_count'] = 0

    if session['step'] < total_text_blocks:
        await update.message.reply_text(text_blocks[session['step']])
        await show_next_button(update, context, session)

    elif session['step'] < total_text_blocks + total_questions:
        question_index = session['step'] - total_text_blocks
        questions = question_blocks[question_index]
        question_text = "\n".join(questions)
        await update.message.reply_text(f"Вопрос:\n{question_text}")
        await show_next_button(update, context, session)

    else:
        await finish_interview(update, context, session)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    session = user_sessions.get(user_id)

    if not session:
        await update.message.reply_text("Начните с /start")
        return

    if session.get('waiting_for_name', False):
        await update.message.reply_text("❌ Сначала введите ваше ФИО!")
        return

    voice_duration = update.message.voice.duration
    if voice_duration < 10:
        await update.message.reply_text("❌ Необходимо дать более развернутый ответ (не менее 10 секунд).")
        return

    try:
        if not session['folder_created']:
            date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            username_clean = session['username'].replace(' ', '_')
            full_name_clean = session['full_name'].replace(' ', '_')
            folder_name = f"{username_clean}_{full_name_clean}_{date_str}"

            folder_id = drive_service.create_folder(folder_name, GOOGLE_DRIVE_ROOT_FOLDER_ID)

            if folder_id:
                session['folder_id'] = folder_id
                session['folder_url'] = drive_service.get_folder_url(folder_id)
                session['folder_created'] = True
                logging.info(f"Created folder for user: {folder_name}")
            else:
                await update.message.reply_text("❌ Ошибка при создании папки для сохранения ответов.")
                return

        session['voice_count'] += 1

        total_text_blocks = len(text_blocks)
        current_question_number = session['step'] - total_text_blocks + 1

        file_content = await download_voice_file(update.message.voice.file_id, context.bot)

        if file_content:
            file_number = f"{current_question_number}.{session['voice_count']}.ogg"
            file_id = drive_service.upload_voice_message(file_content, file_number, session['folder_id'])

            if file_id:
                logging.info("Начинаем транскрибацию...")
                transcription = await transcribe_audio(file_content)
                logging.info(f"Результат транскрибации: {transcription}")

                voice_data = {
                    'file_id': file_id,
                    'question_number': current_question_number,
                    'voice_count': session['voice_count'],
                    'duration': voice_duration,
                    'file_size': update.message.voice.file_size,
                    'timestamp': datetime.now(),
                    'filename': file_number,
                    'transcription': transcription
                }

                session['voice_files'].append(voice_data)

                logging.info(f"Голосовое сообщение сохранено: {file_number}")

                total_questions = len(question_blocks)
                current_question = session['step'] - len(text_blocks) + 1

                if current_question >= total_questions:
                    await update.message.reply_text(
                        "✅ Ответ принят! Вы можете отправить еще одно сообщение или нажать кнопку 'Завершить тестирование'")
                else:
                    await update.message.reply_text(
                        "✅ Ответ принят! Вы можете отправить еще одно сообщение или перейти к следующему вопросу.")
            else:
                await update.message.reply_text("❌ Ошибка при сохранении ответа. Пожалуйста, попробуйте еще раз.")
        else:
            await update.message.reply_text("❌ Ошибка при загрузке голосового сообщения.")

    except Exception as e:
        logging.error(f"Ошибка обработки голосового сообщения: {e}")
        await update.message.reply_text("❌ Произошла ошибка при сохранении ответа. Пожалуйста, попробуйте еще раз.")

async def finish_interview(update: Update, context: ContextTypes.DEFAULT_TYPE, session):
    final_message = "🎉 Поздравляем! Собеседование завершено. Спасибо за уделенное время и ваши ответы! При положительном решении мы свяжемся с вами в ближайшее время."
    await update.message.reply_text(final_message, reply_markup=ReplyKeyboardRemove())

    await create_transcription_file(session)

    if ADMIN_CHAT_ID:
        await send_admin_notification(context, session)

    if update.message.from_user.id in user_sessions:
        del user_sessions[update.message.from_user.id]

async def send_admin_notification(context: ContextTypes.DEFAULT_TYPE, session):
    try:
        total_duration = sum(voice['duration'] for voice in session['voice_files'])
        total_size = sum(voice['file_size'] for voice in session['voice_files'])

        folder_link = session['folder_url'] if session['folder_created'] else "Папка не создана"

        summary_message = f"""
📋 Завершено новое собеседование

👤 Кандидат: @{session['username']}
📛 ФИО: {session['full_name']}
🎤 Ответов: {len(session['voice_files'])}
⏱️ Общая длительность: {total_duration} сек
📊 Общий размер: {total_size} байт
🕒 Начало: {session['start_time'].strftime('%d.%m.%Y %H:%M:%S')}
⏰ Завершение: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
📁 Ответы сохранены: {folder_link}

Ответы по вопросам:
"""

        for voice in session['voice_files']:
            summary_message += f"• Вопрос {voice['question_number']}.{voice['voice_count']} - {voice['duration']} сек\n"

        await context.bot.send_message(
            chat_id=int(ADMIN_CHAT_ID),
            text=summary_message
        )

    except Exception as e:
        logging.error(f"Ошибка отправки уведомления администратору: {e}")

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ Команда только для администратора")
        return

    if not user_sessions:
        await update.message.reply_text("📊 Нет активных собеседований")
        return

    stats_message = "📊 Активные собеседования:\n\n"
    for user_id, session in user_sessions.items():
        stats_message += f"👤 @{session['username']}\n"
        stats_message += f"   📛 ФИО: {session['full_name']}\n"
        stats_message += f"   📍 Шаг: {session['step']}/{len(text_blocks) + len(question_blocks)}\n"
        stats_message += f"   🎤 Ответов: {len(session['voice_files'])}\n"
        stats_message += f"   📁 Папка создана: {'Да' if session['folder_created'] else 'Нет'}\n"
        stats_message += f"   ⏰ В процессе: {datetime.now() - session['start_time']}\n\n"

    await update.message.reply_text(stats_message)

def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", show_stats))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))

    logging.info("Бот запущен!")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
>>>>>>> 2753e3179e2d108e4e68a68bf23bc38c37aa3249
