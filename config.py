import yaml


with open("config.yml", 'r') as f:
    config = yaml.safe_load(f)

telegram_token = config["telegram_token"]
openai_api_key = config["openai_api_key"]
allowed_telegram_usernames = config["allowed_telegram_usernames"]
persistence_path = config["persistence_path"]
reset_timeout = config["reset_timeout"]
