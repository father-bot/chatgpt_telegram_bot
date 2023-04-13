from typing import Optional, Any

import pymongo
import uuid
from datetime import datetime

import config


class Database:
    def __init__(self):
        self.client = pymongo.MongoClient(config.mongodb_uri)
        self.db = self.client["chatgpt_telegram_bot"]

        self.chat_collection = self.db["chat"]
        self.dialog_collection = self.db["dialog"]

    def chat_exists(self, chat_id: int):
        return self.chat_collection.count_documents({"_id": chat_id}) > 0

    def create_chat(self, chat_id: int):
        chat_dict = {
            "_id": chat_id,
            "last_interaction": datetime.now(),
            "first_seen": datetime.now(),
            "current_dialog_id": None,
            "current_chat_mode": "assistant",
            "current_model": config.models["available_text_models"][0],
            "n_used_tokens": {},  # {"model_name": {"n_input_tokens": 0, "n_output_tokens": 0}}
            "n_transcribed_seconds": 0.0  # voice message transcription
        }

        if not self.chat_exists(chat_id):
            self.chat_collection.insert_one(chat_dict)

    def start_new_dialog(self, chat_id: int):
        if not self.chat_exists(chat_id):
            raise ValueError(f"Chat {chat_id} does not exist")

        dialog_id = str(uuid.uuid4())
        dialog_dict = {
            "_id": dialog_id,
            "chat_id": chat_id,
            "chat_mode": self.get_chat_attribute(chat_id, "current_chat_mode"),
            "start_time": datetime.now(),
            "model": self.get_chat_attribute(chat_id, "current_model"),
            "messages": []
        }

        # add new dialog
        self.dialog_collection.insert_one(dialog_dict)

        # update chat's current dialog
        self.chat_collection.update_one(
            {"_id": chat_id},
            {"$set": {"current_dialog_id": dialog_id}}
        )

        return dialog_id

    def get_chat_attribute(self, chat_id: int, key: str):
        if not self.chat_exists(chat_id):
            raise ValueError(f"Chat {chat_id} does not exist")

        chat_dict = self.chat_collection.find_one({"_id": chat_id})

        if key not in chat_dict:
            return None

        return chat_dict[key]

    def set_chat_attribute(self, chat_id: int, key: str, value: Any):
        if not self.chat_exists(chat_id):
            raise ValueError(f"Chat {chat_id} does not exist")

        self.chat_collection.update_one({"_id": chat_id}, {"$set": {key: value}})

    def update_n_used_tokens(self, chat_id: int, model: str, n_input_tokens: int, n_output_tokens: int):
        n_used_tokens_dict = self.get_chat_attribute(chat_id, "n_used_tokens")

        if model in n_used_tokens_dict:
            n_used_tokens_dict[model]["n_input_tokens"] += n_input_tokens
            n_used_tokens_dict[model]["n_output_tokens"] += n_output_tokens
        else:
            n_used_tokens_dict[model] = {
                "n_input_tokens": n_input_tokens,
                "n_output_tokens": n_output_tokens
            }

        self.set_chat_attribute(chat_id, "n_used_tokens", n_used_tokens_dict)

    def get_dialog_messages(self, chat_id: int, dialog_id: Optional[str] = None):
        if not self.chat_exists(chat_id):
            raise ValueError(f"Chat {chat_id} does not exist")

        if dialog_id is None:
            dialog_id = self.get_chat_attribute(chat_id, "current_dialog_id")

        dialog_dict = self.dialog_collection.find_one({"_id": dialog_id, "chat_id": chat_id})
        return dialog_dict["messages"]

    def set_dialog_messages(self, chat_id: int, dialog_messages: list, dialog_id: Optional[str] = None):
        if not self.chat_exists(chat_id):
            raise ValueError(f"Chat {chat_id} does not exist")

        if dialog_id is None:
            dialog_id = self.get_chat_attribute(chat_id, "current_dialog_id")

        self.dialog_collection.update_one(
            {"_id": dialog_id, "chat_id": chat_id},
            {"$set": {"messages": dialog_messages}}
        )
