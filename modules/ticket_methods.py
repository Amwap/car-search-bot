from modules.models import *
import datetime
import re 


def create_ticket(tg_id, kind) -> int:
    """ Создаёт пустой тикет """
    user = User.get(tg_id=tg_id)
    # status = "creating"
    
    ticket = Ticket(user=user, kind=kind)
    if kind == 'passenger':
        ticket.status = 'looking'
    ticket.save()
    return ticket.id


def set_city_from(tg_id, city, ticket_id) -> None:
    """ Добавляет город в тикет """
    ticket = Ticket.get(id = ticket_id)
    ticket.city_from = city
    ticket.save()

def set_city_to(tg_id, city, ticket_id) -> None:
    """ Добавляет город в тикет """
    ticket = Ticket.get(id = ticket_id)
    ticket.city_to = city
    ticket.save()

def _check_type(data) -> str:
    """ Возвращает транскрипцию none """ 
    if data == None or data == 0: return "не указано"
    else: return data

def _check_time_type(data) -> str:
    """ Возвращает тип для времени """
    if data == "None": return "не указано"
    else: return data

def _check_comment_type(data) -> str:
    """ Возвращает тип для времени """
    if data == None: return ""
    else: return data


def get_ticket_demo(ticket_id) -> str:
    """ Возвращает демо стринг тикета """
    """ типы: driver, passenger """ 
    ticket = Ticket.get(id = ticket_id)
    if ticket.kind == 'passenger' and ticket.status == "looking":
        string = f"""```
Маршрут: {_check_type(ticket.city_from)} -> {_check_type(ticket.city_to)}
Дата: {_check_type(ticket.date)}
```"""

    elif ticket.kind == 'passenger' and ticket.status == 'creating': 
        string = f"""```
Маршрут: {_check_type(ticket.city_from)} -> {_check_type(ticket.city_to)}
Дата: {_check_type(ticket.date)}
Время: {_check_time_type(str(ticket.time)[0:5])}
Количество пассажиров: {_check_type(ticket.places)}
Телефон: {_check_type(ticket.phone)} 

{_check_comment_type(ticket.comment)}
```"""

    elif ticket.kind == 'driver' and ticket.status == 'creating': 
        string = f"""```
Тип: Водитель
Маршрут: {_check_type(ticket.city_from)} -> {_check_type(ticket.city_to)}
Дата: {_check_type(ticket.date)}
Время: {_check_time_type(str(ticket.time)[0:5])}
Количество мест: {_check_type(ticket.places)}
Стоимость: {_check_type(ticket.cost)}{ticket.currency}
Телефон: {_check_type(ticket.phone)} 

{_check_comment_type(ticket.comment)}
```"""

    elif ticket.kind == 'passenger': 
        string = f"""
Маршрут: *{_check_type(ticket.city_from)} -> {_check_type(ticket.city_to)}*
Дата: *{_check_type(ticket.date)}*
Время: *{_check_time_type(str(ticket.time)[0:5])}*
Количество пассажиров: *{_check_type(ticket.places)}*
Телефон: *{_check_type(ticket.phone)}*

*{_check_comment_type(ticket.comment)}*
"""

    elif ticket.kind == 'driver': 
        string = f"""
Тип: Водитель
Маршрут: *{_check_type(ticket.city_from)} -> {_check_type(ticket.city_to)}*
Дата: *{_check_type(ticket.date)}*
Время: *{_check_time_type(str(ticket.time)[0:5])}*
Количество мест: *{_check_type(ticket.places)}*
Стоимость: *{_check_type(ticket.cost)}{ticket.currency}* 
Телефон: *{_check_type(ticket.phone)}*

*{_check_comment_type(ticket.comment)}*
"""
    return string


def set_demo_message_id(ticket_id, message_id) -> None:
    """ Сохраняет id собщения демонстрации """
    ticket = Ticket.get(id = ticket_id)
    ticket.demo_message = message_id
    ticket.save()


def get_demo_message_id(ticket_id) -> int:
    """ Возвращает id demo тикета """
    ticket = Ticket.get(id = ticket_id)
    return ticket.demo_message

def set_date(ticket_id, year:int, month:int, day:int=1) -> None:
    """ Устанавливает дату тикета """
    ticket = Ticket.get(id = ticket_id)
    ticket.date = datetime.datetime(year, month, day)
    ticket.save()

def set_time(ticket_id, hour:int, minute:int) -> None:
    """ Устанавливает время в тикете """
    time = datetime.time(hour=hour, minute=minute)
    ticket = Ticket.get(id = ticket_id)
    ticket.time = time
    ticket.save()

def set_cost(ticket_id, cost:int) -> None:
    """ Устанавливает цену в тикете """
    ticket = Ticket.get(id = ticket_id)
    ticket.cost = cost
    ticket.save()


def get_ticket_type(ticket_id) -> str:
    """ Возвращает тип тикета (driver or passanger) """
    ticket = Ticket.get(id = ticket_id)
    return ticket.kind    

def wipe_ticket(ticket_id) -> None:
    """ Удаление данных тикета """
    ticket = Ticket.get(id = ticket_id)
    ticket.city_from = None
    ticket.city_to = None
    ticket.date = None
    ticket.time = None
    ticket.cost = None
    ticket.save()


def delete_ticket(ticket_id) -> None:
    """ Удаление тикета """
    ticket = Ticket.get(id = ticket_id)
    ticket.delete()


def check_this_day(ticket_id) -> list:
    """ Проверяет наличие поездок в выбранную дату по тикету"""
    ticket = Ticket.get(id = ticket_id)
    tickets = (Ticket.select().where(
                    Ticket.date == ticket.date
                    & (Ticket.city_from == ticket.city_from)
                    & (Ticket.city_to == ticket.city_to)
                    & (Ticket.status == "publishing")
                    & (Ticket.kind != ticket.kind)
                    )
                )
    return tickets

def check_this_date(date:datetime, ticket_id) -> list:
    """ Проверяет данный день для составления клавиатуры """
    ticket = Ticket.get(id = ticket_id)
    tickets = (Ticket.select().where(
                    (Ticket.date == date)
                    & (Ticket.city_from == ticket.city_from)
                    & (Ticket.city_to == ticket.city_to)
                    & (Ticket.status == "publishing")
                    & (Ticket.kind != ticket.kind)
                    )
                )
    return tickets

def get_ticket(ticket_id):
    """ Возвращает тикет """
    return Ticket.get(id = ticket_id)


def set_free_places(ticket_id, count:int) -> None:
    """ Устанавливает свободные места """
    ticket = Ticket.get(id = ticket_id)
    ticket.places = count
    ticket.save()

def set_phone_number(ticket_id, number) -> None:
    """ Устанавливает номер телефона в тикет """
    ticket = Ticket.get(id = ticket_id)
    ticket.phone = number
    ticket.save()

def set_comment(ticket_id, comment:str) -> None:
    """ Устанавливает коментарий тикета """
    ticket = Ticket.get(id = ticket_id)
    ticket.comment = comment
    ticket.save()

def set_status(ticket_id, status:str) -> None:
    """ Устанавливает статус тикета """
    ticket = Ticket.get(id = ticket_id)
    ticket.status = status
    ticket.save()

def get_current_drivers(ticket_id) -> list:
    ticket = Ticket.get(id=ticket_id)
    tickets = Ticket.select().where(
        (Ticket.date == ticket.date)
        &(Ticket.city_from == ticket.city_from)
        &(Ticket.city_to == ticket.city_to)
        &(Ticket.places >= ticket.places)
        &(Ticket.kind == 'driver')
        )

    users_list = []
    for ticket in tickets:
        user = User.get(id=ticket.user)
        users_list.append(user)
    return users_list


def get_current_passengers(ticket_id) -> list:
    ticket = Ticket.get(id=ticket_id)
    tickets = Ticket.select().where(
        (Ticket.date == ticket.date)
        &(Ticket.city_from == ticket.city_from)
        &(Ticket.city_to == ticket.city_to)
        &(Ticket.places >= ticket.places)
        &(Ticket.kind == 'passenger')
        )
    return tickets

def get_active_tickets(user_id):
    tickets = Ticket.select().where(
        (Ticket.user_id == user_id)
        &(Ticket.date >= datetime.datetime.now())
        &(Ticket.status == 'publishing')
    )
    return tickets

def get_all_tickets(user_id):
    tickets = Ticket.select().where(
        (Ticket.user_id == user_id)
        &((Ticket.status == 'complete')
        |(Ticket.status == 'publishing'))

    )
    return tickets

def set_currency(ticket_id, cur):
    ticket = Ticket.get(id = ticket_id)
    ticket.currency = cur
    ticket.save()

def get_city_from(ticket_id):
    ticket = Ticket.get(id = ticket_id)
    return ticket.city_from