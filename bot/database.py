import abc
import os
from collections import defaultdict
from typing import Optional, Any

import pymongo
import uuid
from datetime import datetime

import yaml

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


class PlainFileUser:

    def __init__(self):
        self.user = None
        self.dialogs = {}

    def _folder_name(self):
        return self.user.get("username", str(self.user["_id"]))

    def commit(self):
        if not os.path.exists(os.path.join(PlainFileDB.DB_PATH, self._folder_name())):
            os.makedirs(os.path.join(PlainFileDB.DB_PATH, self._folder_name()))
        with open(os.path.join(PlainFileDB.DB_PATH, self._folder_name(), "user.yaml"), "w") as f:
            yaml.safe_dump(self.user, f)
        for dialog_id, dialog in self.dialogs.items():
            with open(os.path.join(PlainFileDB.DB_PATH, self._folder_name(), f"dialog_{dialog_id}.yaml"), "w") as f:
                yaml.safe_dump(dialog, f)



class PlainFileDB(AbstractDB):
    DB_PATH = "db"

    def load_user(self, name):
        path = os.path.join(self.DB_PATH, name)
        for file in os.listdir(path):
            if not file.endswith(".yaml"):
                raise ValueError(f"Unknown file type {path}")
            if file.startswith("user"):
                with open(os.path.join(path, file), "r") as f:
                    user = yaml.safe_load(f)
                    self.user_collection[user["_id"]].user = user
            elif file.startswith("dialog"):
                with open(os.path.join(path, file), "r") as f:
                    dialog = yaml.safe_load(f)
                    self.user_collection[dialog["user_id"]].dialogs[dialog["_id"]] = dialog

    def __init__(self):
        self.user_collection = defaultdict(PlainFileUser)

        if not os.path.exists(self.DB_PATH):
            os.makedirs(self.DB_PATH)
        for file in os.listdir(self.DB_PATH):
            if not os.path.isdir(os.path.join(self.DB_PATH, file)):
                raise ValueError(f"Unknown file type {file}")
            self.load_user(file)

    def check_if_user_exists(self, user_id: int, raise_exception: bool = False):
        if self.user_collection[user_id].user is not None:
            return True
        else:
            if raise_exception:
                raise ValueError(f"User {user_id} does not exist")
            else:
                return False

    def add_new_user(self, user: dict):
        db_user = self.user_collection[user["_id"]]
        db_user.user = user
        db_user.commit()


    def add_dialog(self, dialog: dict):
        self.user_collection[dialog["user_id"]].dialogs[dialog["_id"]] = dialog

        # update user's current dialog
        self.user_collection[dialog["user_id"]].user["current_dialog_id"] = dialog["_id"]

        self.user_collection[dialog["user_id"]].commit()

    def get_user(self, user_id: int):
        return self.user_collection[user_id].user

    def set_user_attribute(self, user_id: int, key: str, value: Any):
        self.user_collection[user_id].user[key] = value
        self.user_collection[user_id].commit()

    def get_dialog(self, dialog_id: int, user_id: int):
        return self.user_collection[user_id].dialogs[dialog_id]

    def set_dialog_messages(self, dialog_id: int, user_id: int, dialog_messages: list):
        self.user_collection[user_id].dialogs[dialog_id]["messages"] = dialog_messages
        self.user_collection[user_id].commit()


class Database:
    db: AbstractDB

    def __init__(self):
        if config.db_type == "mongodb":
            self.db = MongoDB()
        elif config.db_type == "plain_file":
            self.db = PlainFileDB()
        else:
            raise ValueError(f"Unknown database type {config.db_type}")
    def check_if_user_exists(self, user_id: int, raise_exception: bool = False):
        return self.db.check_if_user_exists(user_id, raise_exception)

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
