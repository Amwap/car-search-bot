from modules.models import *
import  modules.ticket_methods as tkm

def check_user(tg_id) -> None:
    """ Проверяет наличие пользователя в базе. Если нет, то создаёт его"""
    user = User.get_or_none(User.tg_id == tg_id)
    if user is None:
        user = User(tg_id=tg_id)
        user.save()


def set_name(tg_id, name) -> None:
    """ Устанавливает имя пользователя """
    user = User.get(tg_id=tg_id)
    user.name = name
    user.save()


def set_root_message(tg_id, msg) -> None:
    user = User.get(tg_id=tg_id)
    user.root_message = msg
    user.save()

def get_root_id(tg_id) -> None:
    user = User.get(tg_id=tg_id)
    return user.root_message


def add_msg_in_pool(tg_id, msg) -> None:
    user = User.get(tg_id=tg_id)


def create_new_user(tg_id) -> None:
    user = User(tg_id=tg_id)
    user.save()

def get_phone(tg_id) -> str:
    """ Возвращает телефон """
    user = User(tg_id=tg_id)
    return user.phone

def set_phone(tg_id, phone) -> None:
    """ Сохраняет номер телефона """
    user = User(tg_id=tg_id)
    user.phone = phone
    user.save()

def get_profile(tg_user_id) -> str:
    """ Возвращает строку профиля """
    user = User.get(tg_id=tg_user_id)
    active_Tickets = tkm.get_active_tickets(user.id)
    all_tickets = tkm.get_all_tickets(user.id)
    who = 'Пассажир'
    if user.state == 'driver':
        who = 'Водитель'
    profile_string = f"""
Ваш профиль:
{who}
Активные заявки: *{len(active_Tickets)}*
Все заявки: *{len(all_tickets)}*
"""
    return profile_string

def get_user_by_tg_id(tg_user_id):
    return User.get(tg_id=tg_user_id)

def get_all_tg_id() -> list:
    """ Возвращает все телеграм id для рассылки """
    tg_id_list = User.select(User.tg_id)
    return tg_id_list