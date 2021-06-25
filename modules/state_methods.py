from modules.models import *
import json


def set_state(tg_id, state_string:str) -> None:
    """ Сохраняет состояние """
    user = User.get(User.tg_id == tg_id)
    user.state = state_string
    user.save()
    print(state_string)

def get_state(tg_id) -> str:
    """ Возвращает состояние """
    user = User.get(User.tg_id == tg_id)
    return user.state

def drop_state(tg_id) -> None:
    """ Сбрасывает состояние """
    user = User.get(User.tg_id == tg_id)
    user.state = ''
    user.save()

def set_root_message(tg_id, root_message) -> None:
    """ Устанавливает корневое сообщение """
    user = User.get(User.tg_id == tg_id)
    user.root_message = root_message.id
    user.save()


def get_root_message(tg_id) -> int:
    """ Возвращает id root_message """ 
    user = User.get(User.tg_id == tg_id)
    return user.root_message

def update_state_list(tg_id, message_id):
    user = User.get(tg_id=tg_id)
    msg_list = json.loads(user.message_list)
    msg_list.append(message_id)
    user.message_list = json.dumps(msg_list)
    user.save()

def get_state_list(tg_id) -> list:
    user = User.get(User.tg_id == tg_id)
    return json.loads(user.message_list)

def wipe_state_list(tg_id):
    user = User.get(User.tg_id == tg_id)
    user.message_list = "[]"
    user.save()