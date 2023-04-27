import json
import os

import yaml
import dotenv
from pathlib import Path

config_dir = Path(__file__).parent.parent.resolve() / "config"

# load .env config
config_env = os.environ.copy()

# config parameters
telegram_token = config_env["telegram_token"]
openai_api_key = config_env["openai_api_key"]
use_chatgpt_api = config_env.get("use_chatgpt_api", True)
if config_env["allowed_telegram_usernames"]:
    allowed_telegram_usernames = json.loads(config_env["allowed_telegram_usernames"])
else:
    allowed_telegram_usernames = []
new_dialog_timeout = config_env["new_dialog_timeout"]
enable_message_streaming = config_env.get("enable_message_streaming", True)
return_n_generated_images = config_env.get("return_n_generated_images", 1)
n_chat_modes_per_page = config_env.get("n_chat_modes_per_page", 5)
mongodb_uri = config_env["mongodb_uri"]

# chat_modes
with open(config_dir / "chat_modes.yml", 'r') as f:
    chat_modes = yaml.safe_load(f)

# models
with open(config_dir / "models.yml", 'r') as f:
    models = yaml.safe_load(f)

# files
help_group_chat_video_path = Path(__file__).parent.parent.resolve() / "static" / "help_group_chat.mp4"
