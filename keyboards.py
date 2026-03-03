from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

first_btns = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Да", callback_data='Yes1')],
                                                   [InlineKeyboardButton(text="Нет", callback_data="No1")]])
second_btns = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="2–3 часа", callback_data='2-3_hours')],
                                                    [InlineKeyboardButton(text="4–5 часов", callback_data="4–5_hours")],
                                                    [InlineKeyboardButton(text="6+ часов", callback_data="6+_hours")]])

third_btns = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="B2B звонки", callback_data='b2b')],
                                                    [InlineKeyboardButton(text="Колл-центр", callback_data="center")],
                                                    [InlineKeyboardButton(text="Нет опыта", callback_data="no experience")]])

fourth_btns = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Спокойные короткие разговоры по делу", callback_data='relax answer')],
                                                    [InlineKeyboardButton(text="Активные продажи и работа с возражениями", callback_data="sell and work")],
                                                    [InlineKeyboardButton(text="Готов(а) попробовать", callback_data="ready to try")]])

fifth_btns = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Да", callback_data='Yes2')],
                                                    [InlineKeyboardButton(text="Частично", callback_data="partially")],
                                                    [InlineKeyboardButton(text="Нет", callback_data="No2")]])