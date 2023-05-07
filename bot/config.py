import yaml
import os
from pathlib import Path

config_dir = Path(__file__).parent.parent.resolve() / "config"

telegram_token = os.environ["TELEGRAM_TOKEN"]
sudo_users = os.environ.get('SUDO_USERS', '')
user_whitelist = os.environ.get('USER_WHITELIST', '')
new_dialog_timeout = int(os.environ["new_dialog_timeout"])
n_images = int(os.environ["return_n_generated_images"])
mongodb_uri = f"mongodb://{os.environ['MONGODB_USERNAME']}:{os.environ['MONGODB_PASSWORD']}@{os.environ['MONGODB_HOST']}/?retryWrites=true&w=majority"

# apis
with open(config_dir / "api.yml", 'r') as f:
    api = yaml.safe_load(f)

# chat_modes
with open(config_dir / "chat_mode.yml", 'r') as f:
    chat_mode = yaml.safe_load(f)

# models
with open(config_dir / "model.yml", 'r') as f:
    model = yaml.safe_load(f)

# files
help_group_chat_video_path = Path(__file__).parent.parent.resolve() / "static" / "help_group_chat.mp4"

split_string = lambda s: s.split(',') if s else []
