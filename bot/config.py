import yaml
import dotenv
from pathlib import Path

config_dir = Path(__file__).parent.parent.resolve() / "config"

# load yaml config
with open(config_dir / "config.yml", 'r') as f:
    config_yaml = yaml.safe_load(f)

# load .env config
config_env = dotenv.dotenv_values(config_dir / "config.env")

# config parameters
telegram_token = config_yaml["telegram_token"]
openai_api_key = config_yaml["openai_api_key"]
use_chatgpt_api = config_yaml.get("use_chatgpt_api", True)
allowed_telegram_usernames = config_yaml["allowed_telegram_usernames"]
new_dialog_timeout = config_yaml["new_dialog_timeout"]
mongo_host = config_env.get("MONGODB_HOST", "mongo")
enable_message_streaming = config_yaml.get("enable_message_streaming", True)
mongodb_uri = f"mongodb://{mongo_host}:{config_env['MONGODB_PORT']}"

# chat_modes
with open(config_dir / "chat_modes.yml", 'r', encoding="utf8") as f:
    chat_modes = yaml.safe_load(f)

# prices
chatgpt_price_per_1000_tokens = config_yaml.get("chatgpt_price_per_1000_tokens", 0.002)
gpt_price_per_1000_tokens = config_yaml.get("gpt_price_per_1000_tokens", 0.02)
whisper_price_per_1_min = config_yaml.get("whisper_price_per_1_min", 0.006)

enable_azure_tts = config_yaml.get("enable_azure_tts", False)
azure_tts_key = config_yaml.get("azure_tts_key", "")
azure_tts_region = config_yaml.get("azure_tts_region", "westus")
azure_tts_name = config_yaml.get("azure_tts_name", "en-US-JessaNeural")