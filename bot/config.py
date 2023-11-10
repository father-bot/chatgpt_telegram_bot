import yaml
import dotenv
from pathlib import Path
from os import environ

config_dir = Path(__file__).parent.parent.resolve() / "config"

# load yaml config
with open(config_dir / "config.yml", "r") as f:
    config_yaml = yaml.safe_load(f)

# load .env config
config_env = dotenv.dotenv_values(config_dir / "config.env")

# config parameters
telegram_base_url = config_yaml.get("telegram_base_url", "https://api.telegram.org/bot")
telegram_token = config_yaml.get("telegram_token")
openai_api_key = config_yaml["openai_api_key"]
openai_api_base = config_yaml.get("openai_api_base", None)
allowed_telegram_usernames = config_yaml["allowed_telegram_usernames"]
new_dialog_timeout = config_yaml["new_dialog_timeout"]
enable_message_streaming = config_yaml.get("enable_message_streaming", True)
return_n_generated_images = config_yaml.get("return_n_generated_images", 1)
image_size = config_yaml.get("image_size", "512x512")
n_chat_modes_per_page = config_yaml.get("n_chat_modes_per_page", 5)
mongodb_uri = f"mongodb://mongo:{config_env['MONGODB_PORT']}"

# env config overrides
telegram_base_url = environ.get("TELEGRAM_BASE_URL", telegram_base_url)
telegram_token = environ.get("TELEGRAM_TOKEN", telegram_token)
openai_api_key = environ.get("OPENAI_API_KEY", openai_api_key)
mongodb_uri = environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017/mongo")
# chat_modes
with open(config_dir / "chat_modes.yml", "r") as f:
    chat_modes = yaml.safe_load(f)

# models
with open(config_dir / "models.yml", "r") as f:
    models = yaml.safe_load(f)

# files
help_group_chat_video_path = (
    Path(__file__).parent.parent.resolve() / "static" / "help_group_chat.mp4"
)
