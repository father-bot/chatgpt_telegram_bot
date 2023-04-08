import abc
from typing import Optional, Any

import pymongo
import uuid
from datetime import datetime

import config

class AbstractDB:
    @abc.abstractmethod
    def check_if_user_exists(self, user_id: int, raise_exception: bool = False):
        pass

    @abc.abstractmethod
    def add_new_user(self, user: dict):
        pass

    @abc.abstractmethod
    def add_dialog(self, dialog: dict):
        pass

    @abc.abstractmethod
    def get_user(self, user_id: int):
        pass

    @abc.abstractmethod
    def set_user_attribute(self, user_id: int, key: str, value: Any):
        pass

    @abc.abstractmethod
    def get_dialog(self, dialog_id: int, user_id: int):
        pass

    @abc.abstractmethod
    def set_dialog_messages(self, dialog_id: int, user_id: int, dialog_messages: list):
        pass


class MongoDB(AbstractDB):
    def __init__(self):
        self.client = pymongo.MongoClient(config.mongodb_uri)
        self.db = self.client["chatgpt_telegram_bot"]

        self.user_collection = self.db["user"]
        self.dialog_collection = self.db["dialog"]

    def check_if_user_exists(self, user_id: int, raise_exception: bool = False):
        if self.user_collection.count_documents({"_id": user_id}) > 0:
            return True
        else:
            if raise_exception:
                raise ValueError(f"User {user_id} does not exist")
            else:
                return False

    def add_new_user(self, user: dict):
        self.user_collection.insert_one(user)

    def add_dialog(self, dialog: dict):
        self.dialog_collection.insert_one(dialog)

        # update user's current dialog
        self.user_collection.update_one(
            {"_id": dialog["user_id"]},
            {"$set": {"current_dialog_id": dialog["_id"]}}
        )

    def get_user(self, user_id: int):
        return self.user_collection.find_one({"_id": user_id})

    def set_user_attribute(self, user_id: int, key: str, value: Any):
        self.user_collection.update_one({"_id": user_id}, {"$set": {key: value}})

    def get_dialog(self, dialog_id: int, user_id: int):
        return self.dialog_collection.find_one({"_id": dialog_id, "user_id": user_id})

    def set_dialog_messages(self, dialog_id: int, user_id: int, dialog_messages: list):
        self.dialog_collection.update_one(
            {"_id": dialog_id, "user_id": user_id},
            {"$set": {"messages": dialog_messages}}
        )


class Database:
    db: AbstractDB

    def __init__(self, db_type:str):
        if db_type == "mongodb":
            self.db = MongoDB()
        else:
            raise ValueError(f"Unknown database type {db_type}")

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
            "current_model": config.models["available_text_models"][0],

            "n_used_tokens": {},

            "n_transcribed_seconds": 0.0  # voice message transcription
        }

        if not self.db.check_if_user_exists(user_id):
            self.db.add_new_user(user_dict)

    def start_new_dialog(self, user_id: int):
        self.db.check_if_user_exists(user_id, raise_exception=True)

        dialog_id = str(uuid.uuid4())
        dialog_dict = {
            "_id": dialog_id,
            "user_id": user_id,
            "chat_mode": self.get_user_attribute(user_id, "current_chat_mode"),
            "start_time": datetime.now(),
            "model": self.get_user_attribute(user_id, "current_model"),
            "messages": []
        }

        # add new dialog
        self.db.add_dialog(dialog_dict)

        return dialog_id

    def get_user_attribute(self, user_id: int, key: str):
        self.db.check_if_user_exists(user_id, raise_exception=True)
        user_dict = self.db.get_user(user_id)

        if key not in user_dict:
            return None

        return user_dict[key]

    def set_user_attribute(self, user_id: int, key: str, value: Any):
        self.db.check_if_user_exists(user_id, raise_exception=True)
        self.db.set_user_attribute(user_id, key, value)

    def update_n_used_tokens(self, user_id: int, model: str, n_input_tokens: int, n_output_tokens: int):
        n_used_tokens_dict = self.get_user_attribute(user_id, "n_used_tokens")

        if model in n_used_tokens_dict:
            n_used_tokens_dict[model]["n_input_tokens"] += n_input_tokens
            n_used_tokens_dict[model]["n_output_tokens"] += n_output_tokens
        else:
            n_used_tokens_dict[model] = {
                "n_input_tokens": n_input_tokens,
                "n_output_tokens": n_output_tokens
            }

        self.set_user_attribute(user_id, "n_used_tokens", n_used_tokens_dict)

    def get_dialog_messages(self, user_id: int, dialog_id: Optional[str] = None):
        self.db.check_if_user_exists(user_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")

        dialog_dict = self.db.get_dialog(dialog_id, user_id)
        return dialog_dict["messages"]

    def set_dialog_messages(self, user_id: int, dialog_messages: list, dialog_id: Optional[str] = None):
        self.db.check_if_user_exists(user_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")

        self.db.set_dialog_messages(dialog_id, user_id, dialog_messages)
