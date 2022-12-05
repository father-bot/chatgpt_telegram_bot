# ChatGPT Telegram Bot

## Setup
1. Get your ChatGPT session token. You can find it in [chat.openai.com](https://chat.openai.com) cookies (key: `"__Secure-next-auth.session-token"`)

2. Get your Telegram bot token from [@BotFather](https://t.me/BotFather)

3. Edit `config.env.example` to add your tokens. It looks like this:
```bash
TELEGRAM_TOKEN="<YOU TELEGRAM BOT TOKE>"
CHATGPT_SESSION_TOKEN="<YOUR CHATGPT SESSION ID>"
ALLOWED_TELEGRAM_USERS="<@USERNAME>"
```

4. Rename `config.env.example` to `config.env`:
```bash
mv config.env.example config.env
```

## Run

```bash
docker compose up --build
```
