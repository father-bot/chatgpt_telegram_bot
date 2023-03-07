import json
from typing import Optional, Any
import redis
import uuid
from datetime import datetime,date

import setting

class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

class Database:
    def __init__(self):
        self.client = redis.Redis(host=setting.redis_host, port=setting.redis_port, db=setting.redis_db, password=setting.redis_pwd)

    def check_if_user_exists(self, user_id: int, raise_exception: bool = False):
        if self.client.get("user_%d".format(user_id)) is not None:
            return True
        else:
            if raise_exception:
                raise ValueError(f"User {user_id} does not exist")
            else:
                return False
        
    def add_new_user(
        self,
        user_id: int,
        chat_id: int,
        username: str = "",
        first_name: str = "",
        last_name: str = "",
    ):
        user_dict = {
            "_id": user_id,
            "chat_id": chat_id,

            "username": username,
            "first_name": first_name,
            "last_name": last_name,

            "last_interaction": datetime.now(),
            "first_seen": datetime.now(),
            
            "current_dialog_id": None,
            "current_chat_mode": "assistant",

            "n_used_tokens": 0
        }

        if not self.check_if_user_exists(user_id):
            self.client.set("user_%d".format(user_id),json.dumps(user_dict,cls=CJsonEncoder))
            
        # TODO: maybe start a new dialog here?

    def start_new_dialog(self, user_id: int):
        self.check_if_user_exists(user_id, raise_exception=True)
        dialog_id = str(uuid.uuid4())
        dialog_dict = {
            "_id": dialog_id,
            "user_id": user_id,
            "chat_mode": self.get_user_attribute(user_id, "current_chat_mode"),
            "start_time": datetime.now(),
            "messages": []
        }
        self.client.set("dialog_%s".format(dialog_id),json.dumps(dialog_dict,cls=CJsonEncoder))
        self.set_user_attribute(user_id,"current_dialog_id",dialog_id)
        return dialog_id

    def get_user_attribute(self, user_id: int, key: str):
        self.check_if_user_exists(user_id, raise_exception=True)
        user_dict = json.loads(self.client.get("user_%d".format(user_id)))

        if key not in user_dict:
            raise ValueError(f"User {user_id} does not have a value for {key}")

        if key in ['last_interaction',"first_seen"]:
            return datetime.strptime(user_dict[key], '%Y-%m-%d %H:%M:%S')
        return user_dict[key]

    def set_user_attribute(self, user_id: int, key: str, value: Any):
        self.check_if_user_exists(user_id, raise_exception=True)
        user_dict = json.loads(self.client.get("user_%d".format(user_id)))
        user_dict[key] = value
        self.client.set("user_%d".format(user_id),json.dumps(user_dict,cls=CJsonEncoder))

    def get_dialog_messages(self, user_id: int, dialog_id: Optional[str] = None):
        self.check_if_user_exists(user_id, raise_exception=True)
        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")
        rows = self.client.hgetall("message_%d_%s".format(user_id,dialog_id))
        msgs = [json.loads(msg) for msg in rows.values()]
        return sorted(msgs, key=lambda x: x['msg_id'])

    def del_dialog_message(self, user_id: int, msg_id=str,dialog_id: Optional[str] = None):
        self.check_if_user_exists(user_id, raise_exception=True)
        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")
        self.client.hdel("message_%d_%s".format(user_id,dialog_id),msg_id)

    def set_dialog_message(self, user_id: int, dialog_message: dict, dialog_id: Optional[str] = None):
        self.check_if_user_exists(user_id, raise_exception=True)
        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")
        self.client.hset("message_%d_%s".format(user_id,dialog_id),str(dialog_message["msg_id"]),json.dumps(dialog_message,cls=CJsonEncoder))

    def set_dialog_messages(self, user_id: int, dialog_message: dict, dialog_id: Optional[str] = None):
        pass