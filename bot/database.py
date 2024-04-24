from typing import Optional, Any

import pymongo
import uuid
from datetime import datetime

import config


class Database:
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

            "n_generated_images": 0,
            "n_transcribed_seconds": 0.0  # voice message transcription
        }

        if not self.check_if_user_exists(user_id):
            self.user_collection.insert_one(user_dict)

    def start_new_dialog(self, user_id: int):
        self.check_if_user_exists(user_id, raise_exception=True)

        self.__remove_current_dialog(user_id)
        
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
        self.dialog_collection.insert_one(dialog_dict)

        # update user's current dialog
        self.user_collection.update_one(
            {"_id": user_id},
            {"$set": {"current_dialog_id": dialog_id}}
        )

        return dialog_id

    def get_user_attribute(self, user_id: int, key: str):
        self.check_if_user_exists(user_id, raise_exception=True)
        user_dict = self.user_collection.find_one({"_id": user_id})

        if key not in user_dict:
            return None

        return user_dict[key]

    def set_user_attribute(self, user_id: int, key: str, value: Any):
        self.check_if_user_exists(user_id, raise_exception=True)
        self.user_collection.update_one({"_id": user_id}, {"$set": {key: value}})

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
        self.check_if_user_exists(user_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")

        dialog_dict = self.dialog_collection.find_one({"_id": dialog_id, "user_id": user_id})
        return dialog_dict["messages"]

    def set_dialog_messages(self, user_id: int, dialog_messages: list, dialog_id: Optional[str] = None):
        self.check_if_user_exists(user_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")

        self.dialog_collection.update_one(
            {"_id": dialog_id, "user_id": user_id},
            {"$set": {"messages": dialog_messages}}
        )

    def __remove_current_dialog(self, user_id: int, ) -> None:
        """
        Removes the current dialog for the user

        Args:
            user_id (int): user identifier
            
        Notes:
            User's current_dialog_id is set to None, make sure you call `start_new_session` after this.
            
            If you want to completely remove all the dialogs, use `remove_all_dialogs` instead. 
            
        Side Effects:
            User's current_dialog_id is set to None.
        """
        self.check_if_user_exists(user_id, raise_exception=True)

        dialog_id = self.get_user_attribute(user_id, "current_dialog_id")
        self.set_user_attribute(user_id, "current_dialog_id", None)
        
        if dialog_id is None:
            return
        self.dialog_collection.delete_one({"_id": dialog_id})

    def remove_all_dialogs(self, user_id: int):
        """
        Removes all dialogs for the user

        Args:
            user_id (int): user identifier
            
        Notes:
            User's current_dialog_id is set to None, make sure you call `start_new_session` after this.
            
        """
        result = self.dialog_collection.delete_many({"user_id": user_id})
        print(f"Deleted: {result.deleted_count} dialogs")
        self.set_user_attribute(user_id, "current_dialog_id", None)
    
    
    def try_resume_dialog(self, user_id: int, current_chat_mode: str = None) -> str:
        """
        Try to resume an existing dialog for the user
        
        Args:
            user_id (int): user identifier
            current_chat_mode (str, optional): the selected chat mode Defaults to None.

        Returns:
            str: currrent_dialog_id
            
        Notes:
            This function is called when the user switch between modes. If cannot find existing dialog, create a new one.
        """
        self.check_if_user_exists(user_id, raise_exception=True)
        if current_chat_mode is None:
            current_chat_mode = self.get_user_attribute(user_id, "chat_mode")
        # 
        """
        Get dialog_id of the most recent dialog

        Notes:
            `sort` and `limit` are used to support old project with tons of unremoved dialogs in the DB.
        """
        dialog_ids = self.dialog_collection.find(
                filter={"user_id": user_id, "chat_mode": current_chat_mode},
                projection={"_id": 1},
            ).sort("start_time", -1).limit(1)
        
        if dialog_ids is not None:
            return self.start_new_dialog(user_id)
        latest_relevant_dialog_id = dialog_ids[0]
        cid = latest_relevant_dialog_id['_id']
        self.set_user_attribute(
            user_id, "current_dialog_id", cid
        )
        return cid