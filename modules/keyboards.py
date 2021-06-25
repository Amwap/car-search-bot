from modules.models import Ticket
from typing import ItemsView
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from modules import calendar_methods as cdm
import modules.ticket_methods as tkm

start_over_button = InlineKeyboardButton('⬅️ Начать заново', callback_data='start_over') # Начало создания заявки
to_start_button = InlineKeyboardButton('⏮ В начало', callback_data='to_start') # к старту
choise_another_day_button = InlineKeyboardButton("📅Выбрать другой день", callback_data=f'select_another_day')
put_own_request_button = InlineKeyboardButton('✏️Рассказать водителям', callback_data='put_own_request')
profile_button = InlineKeyboardButton('👤 Мой профиль', callback_data='show_profile')
back_to_menu_bitton = InlineKeyboardButton('⏮ Назад в меню', callback_data=f'back_to_menu')

start_message = InlineKeyboardMarkup()
start_message.add(InlineKeyboardButton('Пользовательское соглашение', callback_data='terms_of_use'))
start_message.add(InlineKeyboardButton('Правила поездок', callback_data='travel_rules'))
start_message.add(InlineKeyboardButton('Политика персональных данных', callback_data='personal_data_policy'))
start_message.add(InlineKeyboardButton('Контакты', callback_data='contacts'))


entry_message = InlineKeyboardMarkup()
entry_message.add(InlineKeyboardButton("🙋🏻‍♂️ Я пассажир", callback_data='passenger'))
entry_message.add(InlineKeyboardButton("🚗 Я водитель", callback_data='driver'))


send_phone = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True) #Подключаем клавиатуру
send_phone.add(KeyboardButton(text="Отправить телефон", request_contact=True)) #Добавляем эту кнопку


def get_current_months():
    keyboard = InlineKeyboardMarkup()
    for i, year, month in cdm.get_months():
        keyboard.add(InlineKeyboardButton(month, callback_data=f'selected_months {year}-{i}'))
    return keyboard


def get_calendar(month:int, ticket_id) -> list:
    """ Возвращает календарь для данного месяца """
    keyboard = InlineKeyboardMarkup(row_width=4)
    data = cdm.get_calendar_data(month)
    line = []
    kind = tkm.get_ticket_type(ticket_id)
    for i in data['days']:
        count_of_drive = len(tkm.check_this_date(date=i, ticket_id=ticket_id))
        day = i.day
        if count_of_drive != 0 and kind != 'driver':
            day = f"{day}✅"
        
        line.append(InlineKeyboardButton(day, callback_data=f'selected_day {data["year"]}-{data["month"]}-{i.day}'))
    keyboard.add(*line)
    keyboard.add(InlineKeyboardButton("📅Выбрать другой месяц", callback_data=f'select_another_month'))
    return keyboard


hours = InlineKeyboardMarkup()
hours.add(InlineKeyboardButton('01:00', callback_data='01:00'),InlineKeyboardButton('02:00', callback_data='02:00'),InlineKeyboardButton('03:00', callback_data='03:00'))
hours.add(InlineKeyboardButton('04:00', callback_data='04:00'),InlineKeyboardButton('05:00', callback_data='05:00'),InlineKeyboardButton('06:00', callback_data='06:00'))
hours.add(InlineKeyboardButton('07:00', callback_data='07:00'),InlineKeyboardButton('08:00', callback_data='08:00'),InlineKeyboardButton('09:00', callback_data='09:00'))
hours.add(InlineKeyboardButton('10:00', callback_data='10:00'),InlineKeyboardButton('11:00', callback_data='11:00'),InlineKeyboardButton('12:00', callback_data='12:00'))

passenger_menu = InlineKeyboardMarkup()
passenger_menu.add(InlineKeyboardButton('🔍 Найти поездку', callback_data='search_drive'), profile_button)
passenger_menu.add(to_start_button)

driver_menu = InlineKeyboardMarkup()
driver_menu.add(InlineKeyboardButton('🚗 Добавить поездку', callback_data='search_drive'), profile_button)
driver_menu.add(to_start_button)

to_start = InlineKeyboardMarkup()
to_start.add(to_start_button)

start_over = InlineKeyboardMarkup()
start_over.add(start_over_button)

drive_not_found = InlineKeyboardMarkup()
drive_not_found.add(put_own_request_button)
drive_not_found.add(choise_another_day_button)
drive_not_found.add(start_over_button)

drive_is_found = InlineKeyboardMarkup()
drive_is_found.add(InlineKeyboardButton('🆗Я нашёл что искал', callback_data='back_to_menu'))
drive_is_found.add(put_own_request_button)
drive_is_found.add(choise_another_day_button)
drive_is_found.add(start_over_button)


free_places = InlineKeyboardMarkup(row_width=4)
board = []
for i in range(1, 9):
    board.append(InlineKeyboardButton(i, callback_data=f'set_places {i}'))
free_places.add(*board)

setting_comment = InlineKeyboardMarkup()
setting_comment.add(InlineKeyboardButton('Мне нечего добавить.', callback_data=f'skip_comments'))

ending_keyboard = InlineKeyboardMarkup()
ending_keyboard.add(InlineKeyboardButton('✅ Опубликовать', callback_data=f'ticket_to_publish'))
ending_keyboard.add(InlineKeyboardButton('❌ Отменить', callback_data=f'back_to_menu'))


def keyboard_for_publishing(ticket_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('❌ Завершить поиск', callback_data=f'cancel_trip {ticket_id}'))
    return keyboard

go_to_menu = InlineKeyboardMarkup()
go_to_menu.add(back_to_menu_bitton)

def variables_of_cities(cities:list):
    if len(cities) == 0: return None
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True) #Подключаем клавиатуру
    for city in cities:
        keyboard.add(KeyboardButton(text=city)) #Добавляем эту кнопку

    return keyboard

skip_city_from = InlineKeyboardMarkup()
skip_city_from.add(start_over_button)
skip_city_from.add(InlineKeyboardButton('➡️ Оставить свой вариант', callback_data=f'skip_city_from'))

skip_city_to = InlineKeyboardMarkup()
skip_city_to.add(start_over_button)
skip_city_to.add(InlineKeyboardButton('➡️ Оставить свой вариант', callback_data=f'skip_city_to'))

profile = InlineKeyboardMarkup()
profile.add(InlineKeyboardButton('📝 История заявок', callback_data=f'my_history'))
profile.add(InlineKeyboardButton('🔍 Открытые заявки', callback_data=f'my_requests'))
profile.add(back_to_menu_bitton)

def hide_messages():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Скрыть список', callback_data=f'hide_messages'))
    return keyboard