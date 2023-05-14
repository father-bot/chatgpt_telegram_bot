from typing import Optional, Any

import pymongo
import uuid
from datetime import datetime

import config


class Database:
    def __init__(self):
        # TODO: Comment this back:
        self.client = pymongo.MongoClient(config.mongodb_uri)
        # if mongodb_uri is not working try this instead:
        # This is due to docker local network
        # self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["chatgpt_telegram_bot"]

        self.user_collection = self.db["user"]
        self.dialog_collection = self.db["dialog"]

    """
    check_if_user_exists(self, user_id: int, raise_exception: bool = False):
    This method checks if a user with the given user_id exists in the database.
    It queries the user_collection collection and checks if any documents match the given user ID.
    If raise_exception is set to True, it raises a ValueError with a message indicating that the user
    does not exist. If the user exists, it returns True; otherwise, it returns False.
    """

    def check_if_user_exists(self, user_id: int, raise_exception: bool = False):
        if self.user_collection.count_documents({"_id": user_id}) > 0:
            return True
        else:
            if raise_exception:
                raise ValueError(f"User {user_id} does not exist")
            else:
                return False

    # add_new_user(self, user_id: int, chat_id: int, username: str = "", first_name: str = "", last_name: str = ""):
    # This method adds a new user to the database. It takes the user_id, chat_id, and optional username,
    # first_name, and last_name as parameters. It creates a dictionary representing the user's information and
    # inserts it into the user_collection collection if the user does not already exist.
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
            "n_transcribed_seconds": 0.0,  # voice message transcription
        }

        if not self.check_if_user_exists(user_id):
            self.user_collection.insert_one(user_dict)

    def start_new_dialog(self, user_id: int):
        self.check_if_user_exists(user_id, raise_exception=True)

        dialog_id = str(uuid.uuid4())
        dialog_dict = {
            "_id": dialog_id,
            "user_id": user_id,
            "chat_mode": self.get_user_attribute(user_id, "current_chat_mode"),
            "start_time": datetime.now(),
            "model": self.get_user_attribute(user_id, "current_model"),
            "messages": [],
        }

        # add new dialog
        self.dialog_collection.insert_one(dialog_dict)

        # update user's current dialog
        self.user_collection.update_one(
            {"_id": user_id}, {"$set": {"current_dialog_id": dialog_id}}
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

    def update_n_used_tokens(
        self,
        user_id: int,
        model: str,
        n_input_tokens: int,
        n_output_tokens: int,
        n_newly_added_tokens: int = 0,
    ):
        """
        Updates the count of used tokens for a specific user and model.

        Args:
            user_id (int): The ID of the user.
            model (str): The name of the model.
            n_input_tokens (int): The number of input tokens used.
            n_output_tokens (int): The number of output tokens used.
            n_newly_added_tokens (int, optional): The number of newly added tokens for the model. Defaults to 0.

        Returns:
            int: The remaining number of available output tokens for the model.

        Raises:
            ValueError: If the user does not exist in the database.

        """
        n_used_tokens_dict = self.get_user_attribute(user_id, "n_used_tokens")

        if model in n_used_tokens_dict:
            n_used_tokens_dict[model]["n_input_tokens"] += n_input_tokens
            n_used_tokens_dict[model]["n_output_tokens"] += n_output_tokens
        else:
            n_used_tokens_dict[model] = {
                "n_input_tokens": n_input_tokens,
                "n_output_tokens": n_output_tokens,
                "n_available_output_token": config.available_token_new_user,
            }
        # data backfill in case this field doesn't exist
        if "n_available_output_token" not in n_used_tokens_dict[model]:
            n_used_tokens_dict[model]["n_available_output_token"] = n_used_tokens_dict[
                model
            ]["n_output_tokens"]

        if n_newly_added_tokens > 0:
            n_used_tokens_dict[model][
                "n_available_output_token"
            ] += n_newly_added_tokens

        remaining_tokens = (
            n_used_tokens_dict[model]["n_available_output_token"]
            - n_used_tokens_dict[model]["n_output_tokens"]
        )

        if remaining_tokens > 0:
            self.set_user_attribute(user_id, "n_used_tokens", n_used_tokens_dict)
            return remaining_tokens
        else:
            # no token remaining, adjust available output token to be equal to total amount of token consumed
            # by the user, and then return 0 to indicate the user needs to pay to get more token
            n_used_tokens_dict[model]["n_available_output_token"] = n_used_tokens_dict[
                model
            ]["n_output_tokens"]
            return 0

    def get_dialog_messages(self, user_id: int, dialog_id: Optional[str] = None):
        self.check_if_user_exists(user_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")

        dialog_dict = self.dialog_collection.find_one(
            {"_id": dialog_id, "user_id": user_id}
        )
        return dialog_dict["messages"]

    def set_dialog_messages(
        self, user_id: int, dialog_messages: list, dialog_id: Optional[str] = None
    ):
        self.check_if_user_exists(user_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")

        self.dialog_collection.update_one(
            {"_id": dialog_id, "user_id": user_id},
            {"$set": {"messages": dialog_messages}},
        )
