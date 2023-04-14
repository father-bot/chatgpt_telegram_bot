import os
import yaml
from pathlib import Path

config_dir = Path(__file__).parent.parent.resolve() / "config"

# load yaml config if it exists, else use environment variables
config_yaml_file = config_dir / "config.yml"
if config_yaml_file.exists():
    with open(config_yaml_file, 'r') as f:
        config_yaml = yaml.safe_load(f)
else:
    config_yaml = {}

# load .env config if it exists, else use environment variables
config_env_file = config_dir / "config.env"
if config_env_file.exists():
    import dotenv
    config_env = dotenv.dotenv_values(config_env_file)
else:
    config_env = {}

# config parameters
telegram_token = config_yaml.get("telegram_token", os.environ.get("TELEGRAM_TOKEN"))
openai_api_key = config_yaml.get("openai_api_key", os.environ.get("OPENAI_API_KEY"))
use_chatgpt_api = config_yaml.get("use_chatgpt_api", os.environ.get("USE_CHATGPT_API", True))
allowed_telegram_usernames = config_yaml.get("allowed_telegram_usernames", os.environ.get("ALLOWED_TELEGRAM_USERNAMES"))
new_dialog_timeout = config_yaml.get("new_dialog_timeout", os.environ.get("NEW_DIALOG_TIMEOUT"))
enable_message_streaming = config_yaml.get("enable_message_streaming", os.environ.get("ENABLE_MESSAGE_STREAMING", True))
mongodb_uri = f"mongodb://mongo:{config_env.get('MONGODB_PORT', os.environ.get('MONGODB_PORT'))}"

# chat_modes
chat_modes_file = config_dir / "chat_modes.yml"
with open(chat_modes_file, 'r') as f:
        chat_modes = yaml.safe_load(f)

# models
models_file = config_dir / "models.yml"
with open(models_file, 'r') as f:
        models = yaml.safe_load(f)
