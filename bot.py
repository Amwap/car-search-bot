from credentials import *
import telebot
from modules.models import *
import modules.user_methods as usm
import modules.state_methods as stm
import modules.keyboards as kb
import modules.ticket_methods as tkm
import modules.wide_texts as wt

from difflib import SequenceMatcher
import re
import json



bot = telebot.TeleBot(TOKEN)

def j_open(name:str):
    """ Извлекает данные из json файла """
    with open(name, mode="r",encoding='utf8') as json_file:
        return json.load(json_file)

def j_save(name:str, var):
    """ Сохраняет данные в json файл """
    with open(name, 'w', encoding='utf8') as json_file:
        json.dump(var, json_file, ensure_ascii=False)

city_list = j_open('cities.json')
finland = j_open('finland_cities.json')

def change_root(tg_id, new_root) -> None:
    """ Удаляет старое рут сообщение и меняет его на новое """
    root_message = stm.get_root_message(tg_id)
    bot.delete_message(tg_id, root_message)
    stm.set_root_message(tg_id, new_root)


def update_demo(ticket_id, tg_id, keyboard=None) -> None:
    """ Обновляет представление редактируемого тикета """
    text = tkm.get_ticket_demo(ticket_id)
    demo_id = tkm.get_demo_message_id(ticket_id=ticket_id)
    try: bot.edit_message_text(text=text, chat_id=tg_id,  message_id=demo_id, parse_mode='Markdown', reply_markup=keyboard)
    except: pass


def scene_manager(tg_id, new_root, ticket_id:None, state:str, keyboard=None) -> None:
    """ Стандартные процедуры смены сцены """
    try: update_demo(tg_id=tg_id, ticket_id=ticket_id, keyboard=keyboard)
    except: print('Update demo was passed cuz its the same')
    change_root(tg_id=tg_id, new_root=new_root)
    stm.set_state(tg_id, state)


def show_profile(tg_user_id, kind:str) -> None:
    """ Открывает профиль после создания тикета или выхода из создания """
    if kind == 'passenger': new_root = bot.send_message(tg_user_id, "Выберите пункт меню:", reply_markup=kb.passenger_menu)    
    elif kind == 'driver':  new_root = bot.send_message(tg_user_id, "Выберите пункт меню:", reply_markup=kb.driver_menu)        
    return new_root


def city_validator(city:str) -> any:
    if city.capitalize() in city_list:
        return True
    else: return False


def searcher(city, city_list) -> list:
    """ Ищет совпадения городов для селектора валидатора """
    variable_of_answers = []
    max_coincidence = 0.0 #максимальное совпадение
    for word in city_list: # перебор массив tuple (№,quest)
        sm = SequenceMatcher(lambda x: x==" ", word.lower(), city.lower()) 
        coincidence = sm.ratio() #коэффициент совпадения
        if coincidence == max_coincidence and coincidence > 0:
            variable_of_answers.append(word)

        elif coincidence > max_coincidence: #находим наибольшее совпадение
            max_coincidence = coincidence
            variable_of_answers.clear()
            variable_of_answers.append(word)

    return variable_of_answers



@bot.message_handler(commands=['myid'])
def welcome_start(message):
    """ Возвращает id пользователя телеграм """
    tg_user_id = message.from_user.id
    bot.send_message(tg_user_id, tg_user_id)


@bot.message_handler(commands=['say'])
def say_function(message):
    tg_user_id = message.from_user.id
    if tg_user_id in admins:
        all_profiles = usm.get_all_tg_id()
        for profile in all_profiles:
            try: bot.send_message(profile.tg_id, message.text.replace('/say', ""))
            except: pass 


@bot.message_handler(commands=['start'])
def welcome_start(message):
    tg_user_id = message.from_user.id
    usm.check_user(tg_user_id)
    stm.drop_state(tg_user_id)
    start_msg = bot.send_message(tg_user_id, wt.start_message[0], reply_markup=kb.start_message)
    root_msg = bot.send_message(tg_user_id, "Я помогу тебе найти попутчиков. Но сначала, cкажи мне к какой категории ты относишься:", reply_markup=kb.entry_message)
    stm.set_root_message(tg_user_id, root_msg)
    stm.set_state(tg_user_id, f"waiting_choice_of_kind {start_msg.id}")


def view_for_wide_texts(var:list, tg_user_id):
    """ Отображение заготовленных текстов """
    for i, text in enumerate(var):
        if i == (len(var)-1):
            msg = bot.send_message(tg_user_id, text, reply_markup=kb.hide_messages())
            stm.update_state_list(tg_user_id, msg.id)
        else:
            msg = bot.send_message(tg_user_id, text)
            stm.update_state_list(tg_user_id, msg.id)


@bot.message_handler(content_types=['text'])
def text(message):
    tg_user_id = message.from_user.id
    state = stm.get_state(tg_user_id)
    ticket_id = state.split(" ")[-1]
    bot.delete_message(chat_id=tg_user_id, message_id=message.id)
    if state.startswith("waiting_city_from"):
        """ Обработка города отправки """
        """ Переход к выбору города назначения"""
        city = message.text 
        tkm.set_city_from(tg_id=tg_user_id, city=city.capitalize(), ticket_id=ticket_id)
        if city_validator(city) == False: 
            variable_of_answers = searcher(city, city_list)
            new_root = bot.send_message(chat_id=tg_user_id, text="Город не найден. Вы можете оставить всё как есть, выбрать город из предложеного списка или ввести новый вариант. Не забудьте включить клавиатуру.", reply_markup=kb.variables_of_cities(variable_of_answers))
            scene_manager(tg_user_id, new_root, ticket_id, f"waiting_city_from {ticket_id}", keyboard=kb.skip_city_from)

        else:
            new_root = bot.send_message(chat_id=tg_user_id, text="Введите город, в который хотите отправиться.\nНапример: Санкт-Петербург")
            scene_manager(tg_user_id, new_root, ticket_id, f"waiting_city_to {ticket_id}", keyboard=kb.start_over)
        

    elif state.startswith("waiting_city_to"):
        """ Обработка выбора города прибытия """
        """ Переход к выбору месяца """
        city = message.text 
        city_from = tkm.get_city_from(ticket_id)
        if (city_from.capitalize() in finland) and (city.capitalize() in finland):
            tkm.set_currency(ticket_id,'€')
        else: tkm.set_currency(ticket_id, '₽')

        tkm.set_city_to(tg_id=tg_user_id, city=city.capitalize(), ticket_id=ticket_id)
        if city_validator(city) == False: 
            variable_of_answers = searcher(city, city_list)
            new_root = bot.send_message(chat_id=tg_user_id, text="Город не найден. Вы можете оставить всё как есть, выбрать город из предложеного списка или ввести новый вариант. Не забудьте включить клавиатуру.", reply_markup=kb.variables_of_cities(variable_of_answers))
            scene_manager(tg_user_id, new_root, ticket_id, f"waiting_city_to {ticket_id}", keyboard=kb.skip_city_to)

        else:
            new_root = bot.send_message(chat_id=tg_user_id, text="Выберите месяц поездки:", reply_markup=kb.get_current_months())
            scene_manager(tg_user_id, new_root, ticket_id, f"waiting_choice_of_month {ticket_id}", keyboard=kb.start_over)
        

    elif state.startswith("waiting_trip_time"): 
        """ Обработка стоимости поездки """
        """ Переход к выбору стоимости поездки """
        """ Для водителей """
        try:
            hour = int(re.split(':', message.text)[0])
            minute = int(re.split(':', message.text)[1])
            tkm.set_time(ticket_id=ticket_id, hour=hour, minute=minute)
        except:
            new_root = bot.send_message(tg_user_id, text="Не возможно указать данное время. Пример ввода: 19:30")
            scene_manager(tg_user_id, new_root, ticket_id, f"waiting_trip_time {ticket_id}", keyboard=kb.start_over)

        else:
            kind = tkm.get_ticket_type(ticket_id=ticket_id)
            if kind == "passenger":
                new_root = bot.send_message(tg_user_id, text="Сколько людей поедет:", reply_markup=kb.free_places)

            if kind == "driver":
                new_root = bot.send_message(tg_user_id, text="Выберите колличество свободных мест:", reply_markup=kb.free_places)
            scene_manager(tg_user_id, new_root, ticket_id, f"waiting_places {ticket_id}", keyboard=kb.start_over)


    elif state.startswith("waiting_trip_cost"):
        """ Обработка стоимости поездки """ 
        """ Переход к отправке телефона или выход из редактирования"""
        """ Для водителей """
        cost = int(message.text)
        tkm.set_cost(ticket_id=ticket_id, cost=cost)
        
        new_root = bot.send_message(tg_user_id, 'Если желаете, можете оставить коментарий к поездке', reply_markup=kb.setting_comment) 
        scene_manager(tg_user_id, new_root, ticket_id, f"waiting_trip_comment {ticket_id}", keyboard=kb.start_over)
        

    elif state.startswith('waiting_phone_number'):
        phone = message.text
        tkm.set_phone_number(ticket_id, phone)
        ending(tg_user_id, ticket_id)



    elif state.startswith('waiting_trip_comment'):
        """ Обработка коментария поездки """
        """ Переход к вводу номера """

        comment = message.text
        tkm.set_comment(ticket_id, comment)

        new_root = bot.send_message(tg_user_id, 'Введите или отправьте номер телефона, чтобы с вами смогли связаться:', reply_markup=kb.send_phone) 
        scene_manager(tg_user_id, new_root, ticket_id, f"waiting_phone_number {ticket_id}", keyboard=kb.start_over)
        

@bot.callback_query_handler(func=lambda call: True)
def query_handler(callback):
    tg_user_id = callback.from_user.id
    state = stm.get_state(tg_user_id)
    ticket_id = state.split(" ")[-1]

    if callback.data == 'terms_of_use': view_for_wide_texts(wt.terms_of_use, tg_user_id)
    elif callback.data == 'travel_rules': view_for_wide_texts(wt.travel_rules, tg_user_id)
    elif callback.data == 'personal_data_policy': view_for_wide_texts(wt.personal_data_policy, tg_user_id)
    elif callback.data == 'contacts': bot.send_message(tg_user_id, wt.contacts, tg_user_id)

    elif callback.data.startswith("hide_messages"):
        messages = stm.get_state_list(tg_user_id)
        for message in messages:
            try:bot.delete_message(tg_user_id, message)
            except: pass
        stm.wipe_state_list(tg_user_id)

    elif state.startswith("waiting_choice_of_kind"):
        """ Меню после выбора типа """
        kind = callback.data.split(" ")[-1]
        try:
            start_msg = state.split(' ')[1]
            bot.delete_message(tg_user_id, start_msg)
        except UnboundLocalError: pass
        new_root = show_profile(tg_user_id, kind)
        scene_manager(tg_user_id, new_root, ticket_id, f"{kind}")

    
    elif callback.data.startswith('start_over'):
        """ Переход к началу поиска поездки """
        kind = tkm.get_ticket_type(ticket_id)
        try: bot.delete_message(tg_user_id, tkm.get_demo_message_id(ticket_id))
        except: pass
        ticket_id = tkm.create_ticket(tg_user_id, kind)
        tkm.delete_ticket(ticket_id=ticket_id)
        demo = bot.send_message(tg_user_id, text=tkm.get_ticket_demo(ticket_id), parse_mode='Markdown')
        tkm.set_demo_message_id(ticket_id, demo.id)
        new_root = bot.send_message(tg_user_id, "Введите город из которого хотите уехать.\nНапример: Москва")
        scene_manager(tg_user_id, new_root, ticket_id, f"waiting_city_from {ticket_id}", keyboard=kb.go_to_menu)


    elif callback.data.startswith('select_another_month'):
        """ Перенаправление на повторный выбор месяца """
        new_root = bot.send_message(chat_id=tg_user_id, text="Выберите месяц поездки:", reply_markup=kb.get_current_months())
        scene_manager(tg_user_id, new_root, ticket_id, f"waiting_choice_of_month {ticket_id}", keyboard=kb.start_over)


    elif callback.data.startswith('select_another_day'):
        """ Перенаправление на повторный выбор дня """
        
        ticket = tkm.get_ticket(ticket_id)
        demo_string = tkm.get_ticket_demo(ticket_id)
        demo = bot.send_message(tg_user_id, text=demo_string, parse_mode='markdown')
        tkm.set_demo_message_id(ticket_id, demo.id)
        month = ticket.date.month
        calendar = kb.get_calendar(int(month), ticket_id=ticket_id)
        new_root = bot.send_message(tg_user_id, text="Выберите день поездки:\nГалочкой ✅ отмечен день в который уже назначена поездака.",  reply_markup=calendar)
        scene_manager(tg_user_id, new_root, ticket_id, f"waiting_trip_day {ticket_id}", keyboard=kb.start_over)


    elif callback.data.startswith('search_drive'):
        """ Переход в категорию поиска поездки """
        """ Выбор города отправления """
        state = stm.get_state(tg_user_id)
        kind = state
        ticket_id = tkm.create_ticket(tg_user_id, kind)
        demo = bot.send_message(tg_user_id, text=tkm.get_ticket_demo(ticket_id), parse_mode='Markdown')
        new_root = bot.send_message(tg_user_id, "Введите город из которого хотите уехать.\nНапример: Москва")
        
        tkm.set_demo_message_id(ticket_id, demo.id)
        scene_manager(tg_user_id, new_root, ticket_id, f"waiting_city_from {ticket_id}", keyboard=kb.go_to_menu)


    elif callback.data.startswith('to_start'):
        """ Возврат на момент после старта """
        try:
            demo = tkm.get_demo_message_id(ticket_id)
            bot.delete_message(tg_user_id, demo)
        except: pass

        root = usm.get_root_id(tg_user_id)
        welcome_start(callback)
        bot.delete_message(tg_user_id, root)


    elif state.startswith("waiting_choice_of_month"):
        """ Обработка выбора месяца """
        """ Переход к выбору дня поездки """
        year = re.split(' |-', callback.data)[1]
        month = re.split(' |-', callback.data)[2]
        tkm.set_date(ticket_id=ticket_id, year=int(year), month=int(month))

        calendar = kb.get_calendar(int(month), ticket_id=ticket_id)
        new_root = bot.send_message(tg_user_id, text="Выберите день поездки:\nГалочкой ✅ отмечен день в который уже назначена поездака.",  reply_markup=calendar)
        scene_manager(tg_user_id, new_root, ticket_id, f"waiting_trip_day {ticket_id}", keyboard=kb.start_over)
        

    elif state.startswith("waiting_trip_day"):
        """ Обработка выбора дня поездки """
        """ Переход к выбору времени поездки """
        year = int(re.split(' |-', callback.data)[1])
        month = int(re.split(' |-', callback.data)[2])
        day = int(re.split(' |-', callback.data)[3])
        tkm.set_date(ticket_id=ticket_id, year=int(year), month=int(month), day=int(day))

        
        kind = tkm.get_ticket_type(ticket_id=ticket_id)
        if kind == "passenger":
            """ ответвление для пассажира """
            demo_id = tkm.get_demo_message_id(ticket_id)
            bot.delete_message(tg_user_id, demo_id)

            ticket = tkm.get_ticket(ticket_id)
            date = ticket.date
            list_of_drive = tkm.check_this_date(date, ticket_id)
            this_date = datetime.datetime(year, month, day).strftime("%d.%m")

            if len(list_of_drive) == 0:
                new_root = bot.send_message(tg_user_id, text=f"На *{this_date}* нет запланированных поездок. Но вы можете оставить свою заявку или посмотреть другой день:", reply_markup=kb.drive_not_found, parse_mode='markdown')

            elif len(list_of_drive) > 0:
                bot.send_message(tg_user_id, text=f"Запланированные поездки на *{this_date}*", parse_mode='markdown')
                for ticket in list_of_drive:
                    text = tkm.get_ticket_demo(ticket.id)
                    bot.send_message(tg_user_id, text=text, parse_mode="markdown")
                new_root = bot.send_message(tg_user_id, text="Выберите пункт меню:", reply_markup=kb.drive_is_found)
            scene_manager(tg_user_id, new_root, ticket_id, f"waiting_trip_time {ticket_id}", keyboard=kb.start_over)

        if kind == "driver":
            new_root = bot.send_message(tg_user_id, text="Введите время поездки. Например: 19:30")
            scene_manager(tg_user_id, new_root, ticket_id, f"waiting_trip_time {ticket_id}", keyboard=kb.start_over)


    elif callback.data.startswith('put_own_request'):
        """ Переход к созданию тикета для пользователей """
        tkm.set_status(ticket_id, 'creating')
        demo_string = tkm.get_ticket_demo(ticket_id)
        demo = bot.send_message(tg_user_id, text=demo_string, parse_mode='markdown')
        tkm.set_demo_message_id(ticket_id, demo.id)
        new_root = bot.send_message(tg_user_id, text="Введите время поездки. Например: 19:30")
        scene_manager(tg_user_id, new_root, ticket_id, f"waiting_trip_time {ticket_id}", keyboard=kb.start_over)


    elif callback.data.startswith('set_places'):
        """ Обработка количества мест """
        """ Переход к выбору стоимости  (пропускается для пассажиров)"""
        count = callback.data.split(" ")[-1]
        tkm.set_free_places(ticket_id, int(count))
        kind = tkm.get_ticket_type(ticket_id=ticket_id)

        if kind == "passenger":
            """ Переход к вводу коментария """
            new_root = bot.send_message(tg_user_id, 'Если желаете, можете оставить коментарий к поездке', reply_markup=kb.setting_comment) 
            scene_manager(tg_user_id, new_root, ticket_id, f"waiting_trip_comment {ticket_id}", keyboard=kb.start_over)

        elif kind == "driver":
            """ Переход к выбору стоимости """
            new_root = bot.send_message(tg_user_id, text="Введите стоимость поездки:")
            scene_manager(tg_user_id, new_root, ticket_id, f"waiting_trip_cost {ticket_id}", keyboard=kb.start_over)


    elif callback.data.startswith('skip_comments'):
        """ Обработка коментария поездки """
        """ Переход к вводу номера """
        new_root = bot.send_message(tg_user_id, 'Введите или отправьте номер телефона, чтобы с вами смогли связаться.', reply_markup=kb.send_phone) 
        scene_manager(tg_user_id, new_root, ticket_id, f"waiting_phone_number {ticket_id}", keyboard=kb.start_over)


    elif callback.data.startswith('cancel_trip'):
        ticket_id = callback.data.split(" ")[-1]
        tkm.set_status(ticket_id=ticket_id, status='complete')
        ticket = tkm.get_ticket(ticket_id) 
        demo_id = ticket.demo_message
        demo_string = f"Поездка завершена.\n {tkm.get_ticket_demo(ticket_id)}"
        bot.edit_message_text(text=demo_string, chat_id=tg_user_id, message_id=demo_id, reply_markup=None, parse_mode="markdown")
    

    elif callback.data.startswith('back_to_menu'): 
        if state.startswith('in_profile'): kind = state.split(" ")[-1]
        else: 
            kind = tkm.get_ticket_type(ticket_id=ticket_id) 
            demo_id = tkm.get_demo_message_id(ticket_id)
            try: bot.delete_message(tg_user_id, demo_id) 
            except: pass
            tkm.delete_ticket(ticket_id)
        new_root = show_profile(tg_user_id, kind)
        scene_manager(tg_user_id, new_root, ticket_id=ticket_id, state=f"{kind}")
        

    elif state.startswith('ending'):
        """ Завершение создания заявки с запуском в публикацию """
        kind = tkm.get_ticket_type(ticket_id=ticket_id) 
        if callback.data.startswith('ticket_to_publish'): 
            tkm.set_status(ticket_id, 'publishing')
            demo_string = tkm.get_ticket_demo(ticket_id)
            demo = bot.send_message(chat_id=tg_user_id, text=demo_string, reply_markup=kb.keyboard_for_publishing(ticket_id), parse_mode='markdown')
            new_root = show_profile(tg_user_id, kind)
            scene_manager(tg_user_id, new_root, ticket_id=ticket_id, state=f"{kind}", keyboard=kb.start_over)
            tkm.set_demo_message_id(ticket_id, demo.id)


            if kind == "passenger":
                """ Сообщает водителям о данной заявке """
                drivers_list = tkm.get_current_drivers(ticket_id)
                if len(drivers_list) != 0:
                    demo_string = tkm.get_ticket_demo(ticket_id)
                    for user in drivers_list:
                        bot.send_message(tg_user_id, text='Для вашей поездки найдена новая заявка:')
                        bot.send_message(user.tg_id, text=demo_string, parse_mode="markdown") 


            elif kind == "driver":
                """ Сообщает водителю о всех подходящих пользователях """
                passenger_list = tkm.get_current_passengers(ticket_id)
                if len(passenger_list) != 0:
                    bot.send_message(tg_user_id, text='Найденные заявки для вашего запроса:')
                    for ticket in passenger_list:
                        demo_string = tkm.get_ticket_demo(ticket.id)
                        bot.send_message(tg_user_id, text=demo_string, parse_mode="markdown") 



    elif callback.data.startswith("skip_city_from"):
        """ Пропускает шаг ввода города """
        new_root = bot.send_message(chat_id=tg_user_id, text="Введите город, в который хотите отправиться.\nНапример: Санкт-Петербург")
        scene_manager(tg_user_id, new_root, ticket_id, f"waiting_city_to {ticket_id}", keyboard=kb.start_over)


    elif callback.data.startswith("skip_city_to"):   
        """ Пропускает шаг ввода города """
        new_root = bot.send_message(chat_id=tg_user_id, text="Выберите месяц поездки:", reply_markup=kb.get_current_months())
        scene_manager(tg_user_id, new_root, ticket_id, f"waiting_choice_of_month {ticket_id}", keyboard=kb.start_over)


    elif callback.data.startswith("show_profile"):
        """ Открывает профиль пользователя """
        profile_string = usm.get_profile(tg_user_id)
        new_root = bot.send_message(chat_id=tg_user_id, text=profile_string, reply_markup=kb.profile, parse_mode="markdown")
        scene_manager(tg_user_id, new_root, ticket_id, f"in_profile {state}")


    elif callback.data.startswith("my_history"):
        """ Возвращает всю историю поездок """
        user = usm.get_user_by_tg_id(tg_user_id)
        all_tickets = tkm.get_all_tickets(user.id)
        if len(all_tickets) == 0:
            msg = bot.send_message(chat_id=tg_user_id, text="Поездки не найдены.", reply_markup=kb.hide_messages())
            stm.update_state_list(tg_user_id, msg.id)
        else:
            for ticket in all_tickets:
                text = f"Маршрут: *{ticket.city_from} -> {ticket.city_to}*\nдата: {ticket.date}"
                msg = bot.send_message(chat_id=tg_user_id, text=text, parse_mode="markdown")
                stm.update_state_list(tg_user_id, msg.id)
            msg = bot.send_message(chat_id=tg_user_id, text="В данном списке представлены все ваши заявки.", reply_markup=kb.hide_messages())
            stm.update_state_list(tg_user_id, msg.id)


    elif callback.data.startswith("my_requests"):
        """ Возвращает список открытых заявок """
        user = usm.get_user_by_tg_id(tg_user_id)
        active_Tickets = tkm.get_active_tickets(user.id)
        if len(active_Tickets) == 0:
            msg = bot.send_message(chat_id=tg_user_id, text="Поездки не найдены.", reply_markup=kb.hide_messages())
            stm.update_state_list(tg_user_id, msg.id)

        else:
            for ticket in active_Tickets:
                text = tkm.get_ticket_demo(ticket.id)
                msg = bot.send_message(chat_id=tg_user_id, text=text, parse_mode="markdown", reply_markup=kb.keyboard_for_publishing(ticket.id))
                tkm.set_demo_message_id(ticket.id, msg.id)
                stm.update_state_list(tg_user_id, msg.id)
            msg = bot.send_message(chat_id=tg_user_id, text="В данном списке представлены все открытые заявки.", reply_markup=kb.hide_messages())
            stm.update_state_list(tg_user_id, msg.id)

    

    print(callback.data, "CALL BACK DATA")


@bot.message_handler(content_types=['contact'])
def contact(message):
    """ Обработка номера телефона """
    """ Переход к завершению """
    tg_user_id = message.from_user.id
    state = stm.get_state(tg_user_id)
    ticket_id = state.split(" ")[-1]
    bot.delete_message(tg_user_id, message.id)
    if state.startswith('waiting_phone_number'):
        if message.contact is not None:
            phone = message.contact.phone_number
            tkm.set_phone_number(ticket_id, phone)
            ending(tg_user_id, ticket_id)
        else:
            new_root = bot.send_message(chat_id=tg_user_id, text="Ошибка ввода телефона. Попробуйте ввести в ручную:")
            scene_manager(tg_user_id, new_root, ticket_id, f"waiting_phone_number {ticket_id}", keyboard=kb.start_over)


def ending(tg_user_id, ticket_id) -> None:
    """Процедура завершения создания тикета"""
    demo_id = tkm.get_demo_message_id(ticket_id=ticket_id)
    bot.delete_message(tg_user_id, demo_id)

    demo_string = tkm.get_ticket_demo(ticket_id)
    new_root = bot.send_message(chat_id=tg_user_id, text=demo_string, reply_markup=kb.ending_keyboard, parse_mode='markdown')
    
    scene_manager(tg_user_id, new_root, ticket_id, f"ending {ticket_id}")



print("Bot has started")
bot.polling(none_stop=True) #запуск



#  Валидатор выбора города
#  Селектор выбора города если не найден
#  Демонстрация доступных вариантов поездки после выбора дня
#  Оформление заявки если доступные поездки не найдены
#  Обработка номера телефона
#  Профиль
#  Отменить поездку
#  Общая рассылка
# TODO Валидатор на контакты
#  Общая рассылка