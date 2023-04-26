from typing import Optional, Any, List, Dict
from datetime import datetime
import uuid
from azure.cosmos import CosmosClient, PartitionKey
import time
import config

class Database:
    def __init__(self):
        self.client = CosmosClient.from_connection_string(config.cosmosdb_connection_string)
        self.database = self.client.get_database_client(config.cosmosdb_database_id)
        self.user_container = self.database.get_container_client("user")
        self.dialog_container = self.database.get_container_client("dialog")


    def generate_sequential_uuid(self):
        timestamp = int(time.time() * 10000000)
        namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
        sequential_uuid = uuid.uuid5(namespace, str(timestamp))
        return sequential_uuid

    def check_if_user_exists(self, user_id: int, raise_exception: bool = False):
        query = f"SELECT VALUE COUNT(1) FROM c WHERE c._id = {user_id}"

        try:
            result = list(self.user_container.query_items(query, enable_cross_partition_query=True))
            if result[0] > 0:
                return True
                
        except Exception:
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
            "id": str(user_id),
            "_id": user_id,
            "chat_id": chat_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "last_interaction": datetime.now().isoformat(),
            "first_seen": datetime.now().isoformat(),
            "current_dialog_id": None,
            "current_chat_mode": "assistant",
            "current_model": config.models["available_text_models"][0],
            "n_used_tokens": {},
            "n_generated_images": 0,
            "n_transcribed_seconds": 0.0  # voice message transcription
        }

        if not self.check_if_user_exists(user_id):
            self.user_container.create_item(body=user_dict)

    def start_new_dialog(self, user_id: int):
        self.check_if_user_exists(user_id, raise_exception=True)

        dialog_id = str(self.generate_sequential_uuid())
        dialog_dict = {
            "id": dialog_id,
            "_id": dialog_id,
            "user_id": user_id,
            "chat_mode": self.get_user_attribute(user_id, "current_chat_mode"),
            "start_time": datetime.now().isoformat(),
            "model": self.get_user_attribute(user_id, "current_model"),
            "messages": []
        }

        # add new dialog
        self.dialog_container.create_item(body=dialog_dict)

        # update user's current dialog
        user = self.get_user_by_id(user_id)
        user["current_dialog_id"] = dialog_id
        self.user_container.upsert_item(body=user)

        return dialog_id

    def get_user_attribute(self, user_id: int, key: str):
        query = f"SELECT u.{key} FROM user u WHERE u.id = @user_id"
        params = [{"name": "@user_id", "value": str(user_id)}]
        result = list(self.user_container.query_items(query=query, parameters=params, enable_cross_partition_query=True))

        if len(result) > 0:
            if key == 'last_interaction':
                return datetime.strptime(result[0][key],"%Y-%m-%dT%H:%M:%S.%f")
            else:
                return result[0][key]
        else:
            return None

    def set_user_attribute(self, user_id: int, key: str, value: Any):
        user = self.get_user_by_id(user_id)
        if isinstance(value, datetime):
            value = value.isoformat()
        user[key] = value
        self.user_container.upsert_item(body=user)

    def update_n_used_tokens(self, user_id: int, model: str, n_input_tokens: int, n_output_tokens: int):
        self.check_if_user_exists(user_id, raise_exception=True)

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

    def get_dialog_messages(self, user_id: int, dialog_id: int = None) -> List[Dict[str, any]]:
        if not dialog_id:
            dialog_id = self.get_user_attribute(user_id, 'current_dialog_id')
            dialog = self.get_dialog_by_id(dialog_id)
            return dialog['messages'] if dialog else []
        else:
            dialog = self.get_dialog_by_id(dialog_id)
            return dialog['messages'] if dialog else []

    def set_dialog_messages(self, user_id: str, messages: List[Dict[str, any]], dialog_id: int = None):
        dialog_id = self.get_user_attribute(user_id, 'current_dialog_id')
        dialog = self.get_dialog_by_id(dialog_id)
        for message in messages:
            message['date'] = message['date'].isoformat()
        dialog['messages'] = messages
        self.dialog_container.upsert_item(body=dialog)


    def get_user_by_id(self, user_id: int):
        query = "SELECT * FROM c WHERE c.id = @user_id"
        params = [{"name": "@user_id", "value": str(user_id)}]
        options = {"enable_cross_partition_query": True}
        result = list(self.user_container.query_items(
            query=query, parameters=params, enable_cross_partition_query=True
        ))
        user =  result[0] if result else []
        return user

    def get_dialog_by_id(self, dialog_id: int):
        query = "SELECT * FROM c WHERE c.id = @dialog_id"
        params = [{"name": "@dialog_id", "value": str(dialog_id)}]
        options = {"enable_cross_partition_query": True}
        result = list(self.dialog_container.query_items(
            query=query, parameters=params, enable_cross_partition_query=True
        ))
        dialog = result[0] if result else []
        return dialog

    def set_last_interaction_now(self, user_id:int):
        self.set_user_attribute(user_id, "last_interaction", datetime.now().isoformat())
    def get_last_interaction(self, user_id:int):
         return datetime.strptime(self.get_user_attribute(user_id, "last_interaction"),"%Y-%m-%dT%H:%M:%S.%f")
