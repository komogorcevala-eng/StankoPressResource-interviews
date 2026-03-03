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
