# ChatGPT Telegram Bot with custom modes
### GPT-4o (text and vision),  GPT-3.5-turbo (text), DALL-E 2 (image generation)

Deploy your own GPT and DALL-E bot.

## Features
- Low latency replies (it usually takes about 3-5 seconds)
- No request limits
- Message streaming
- GPT-4o with text and vision support
- Group Chat support (/help_group_chat to get instructions)
- DALLE 2 (choose 👩‍🎨 Artist mode to generate images)
- Voice message recognition
- Code highlighting
- Dynamic custom system prompts support (/custom) 
- List of allowed Telegram users
- Track $ balance spent on OpenAI API

---

## Latest updates

[Full changelog](CHANGELOG.md)

*20 May 2024*: forked from original repo with new features
  - Added GPT-4o support (text and vision)
  - Removed legacy completion models, only gpt-4o and gpt-3.5-turbo remain
  - Removed excessive chat modes
  - Added dynamic custom system prompt support

## Bot commands
- `/retry` – Regenerate last bot answer
- `/new` – Start new dialog
- `/mode` – Select chat mode
- `/balance` – Show balance
- `/settings` – Show settings
- `/help` – Show help
- `/custom` - Set custom system prompt

## Setup
1. Get your [OpenAI API](https://platform.openai.com/api-keys) key

2. Get your Telegram bot token from [@BotFather](https://t.me/BotFather)

3. Edit `config/config.example.yml` to set your tokens and run 2 commands below (*if you're advanced user, you can also edit* `config/config.example.env`):
    ```bash
    cp config/config.example.yml config/config.yml
    cp config/config.example.env config/config.env
    ```

4. 🔥 And now **run**:
    ```bash
    docker-compose --env-file config/config.env up --build
    ```

## Contributors
- Original bot creator: [@karfly](https://github.com/karfly)
- Maintainer of this fork: [@Otter-man](https://github.com/Otter-man)