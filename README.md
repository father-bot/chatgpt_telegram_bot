# ChatGPT Telegram Bot (**fast** and **no limits**)
We all love [chat.openai.com](https://chat.openai.com), but...

It's TERRIBLY laggy, has daily limits, and is only accessible through an archaic web interface.

This repo is ChatGPT re-created with GPT-3.5 LLM as Telegram Bot. **And it works great.**

## Features
- Low latency replies (it usually takes about 3-5 seconds) 
- No request limits
- Code highlighting
- Different chat modes: 👩🏼‍🎓 Assistant, 👩🏼‍💻 Code Assistant, 🎬 Movie Expert. More soon
- List of allowed Telegram users
- Track $ balance spent on OpenAI API

## Bot commands
- `/retry` – Regenerate last bot answer
- `/new` – Start new dialog
- `/mode` – Select chat mode
- `/balance` – Show balance
- `/help` – Show help

## Setup
1. Get your [OpenAI API](https://openai.com/api/) key

2. Get your Telegram bot token from [@BotFather](https://t.me/BotFather)

3. Edit `config/config.example.yml` to set your tokens and run 2 commands below (*if you're advanced user, you can also edit* `config/config.example.env`):
```bash
mv config/config.example.yml config/config.yml
mv config/config.example.env config/config.env
```

🔥 And now **run**:

```bash
docker compose --env-file config/config.env up --build
```

## References
1. [*Build ChatGPT from GPT-3*](https://learnprompting.org/docs/applied_prompting/build_chatgpt)