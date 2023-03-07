import yaml
import dotenv
import logging

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
mongodb_uri = f"mongodb://mongo:{config_env['MONGODB_PORT']}"

log_debug = config_yaml.get("log_debug", False)
log_format = config_yaml["log_format"]

use_redis = config_yaml.get("use_redis", False)
redis_host = config_env["REDIS_HOST"]
redis_port = config_env["REDIS_PORT"]
redis_db = config_env["REDIS_DB"]
redis_pwd = config_env["REDIS_PWD"]

logging.basicConfig(
    level=logging.DEBUG if log_debug else logging.INFO,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)
