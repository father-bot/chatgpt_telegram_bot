"""
Configuration module for AI Telegram Bot

Loads configuration from YAML files and environment variables.
"""

import yaml
from pathlib import Path

config_dir = Path(__file__).parent.parent.resolve() / "config"

# Load YAML config
config_path = config_dir / "config.yml"
if config_path.exists():
    with open(config_path, 'r') as f:
        config_yaml = yaml.safe_load(f) or {}
else:
    config_yaml = {}

# Load .env config
try:
    import dotenv
    config_env = dotenv.dotenv_values(config_dir / "config.env")
except Exception:
    config_env = {}

# Telegram configuration
telegram_token = config_yaml.get("telegram_token", "")

# NagaAI API configuration
openai_api_key = config_yaml.get("openai_api_key", "")
openai_api_base = config_yaml.get("openai_api_base", "https://api.naga.ac/v1")

# Access control
allowed_telegram_usernames = config_yaml.get("allowed_telegram_usernames", [])
admin_telegram_usernames = config_yaml.get("admin_telegram_usernames", [])

# Dialog settings
new_dialog_timeout = config_yaml.get("new_dialog_timeout", 600)
max_dialog_messages = config_yaml.get("max_dialog_messages", 50)

# Streaming
enable_message_streaming = config_yaml.get("enable_message_streaming", True)

# Image generation
return_n_generated_images = config_yaml.get("return_n_generated_images", 1)
image_size = config_yaml.get("image_size", "1024x1024")

# UI settings
n_chat_modes_per_page = config_yaml.get("n_chat_modes_per_page", 5)
n_models_per_page = config_yaml.get("n_models_per_page", 8)

# Database
mongodb_port = config_env.get('MONGODB_PORT', '27017')
mongodb_host = config_env.get('MONGODB_HOST', 'mongo')
mongodb_uri = config_yaml.get("mongodb_uri", f"mongodb://{mongodb_host}:{mongodb_port}")

# Redis (optional, for caching)
redis_host = config_env.get('REDIS_HOST', 'redis')
redis_port = config_env.get('REDIS_PORT', '6379')
redis_uri = config_yaml.get("redis_uri", f"redis://{redis_host}:{redis_port}")

# Voice settings
stt_model = config_yaml.get("stt_model", "scribe-v1")
tts_model = config_yaml.get("tts_model", "tts-1")
default_tts_voice = config_yaml.get("default_tts_voice", "alloy")

# Default model
default_model = config_yaml.get("default_model", "gpt-4o-mini")

# Chat modes
chat_modes_path = config_dir / "chat_modes.yml"
if chat_modes_path.exists():
    with open(chat_modes_path, 'r') as f:
        chat_modes = yaml.safe_load(f) or {}
else:
    chat_modes = {
        "assistant": {
            "name": "Assistant",
            "welcome_message": "Hi! I'm your AI assistant. How can I help you today?",
            "prompt_start": "You are a helpful AI assistant. Be concise and helpful.",
            "parse_mode": "html"
        }
    }

# Models configuration (static fallback, will be loaded dynamically from API)
models_path = config_dir / "models.yml"
if models_path.exists():
    with open(models_path, 'r') as f:
        models = yaml.safe_load(f) or {}
else:
    models = {
        "available_text_models": ["gpt-4o-mini", "gpt-4o"],
        "info": {}
    }

# Static files
static_dir = Path(__file__).parent.parent.resolve() / "static"
help_group_chat_video_path = static_dir / "help_group_chat.mp4"

# Feature flags
features = {
    "billing_enabled": config_yaml.get("billing_enabled", True),
    "telegram_stars_enabled": config_yaml.get("telegram_stars_enabled", True),
    "web_search_enabled": config_yaml.get("web_search_enabled", True),
    "image_generation_enabled": config_yaml.get("image_generation_enabled", True),
    "voice_enabled": config_yaml.get("voice_enabled", True),
    "documents_enabled": config_yaml.get("documents_enabled", True),
}

# Billing settings
free_tokens_on_signup = config_yaml.get("free_tokens_on_signup", 10000)
referral_bonus_tokens = config_yaml.get("referral_bonus_tokens", 5000)
