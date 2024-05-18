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

## News
- *21 Apr 2023*:
    - DALLE 2 support
    - Group Chat support (/help_group_chat to get instructions)
    - 10 new hot chat modes and updated chat mode menu with pagination: 🇬🇧 English Tutor, 🧠 Psychologist, 🚀 Elon Musk, 📊 SQL Assistant and other.
- *24 Mar 2023*: GPT-4 support. Run `/settings` command to choose model
- *15 Mar 2023*: Added message streaming. Now you don't have to wait until the whole message is ready, it's streamed to Telegram part-by-part (watch demo)
- *9 Mar 2023*: Now you can easily create your own Chat Modes by editing `config/chat_modes.yml`
- *8 Mar 2023*: Added voice message recognition with [OpenAI Whisper API](https://openai.com/blog/introducing-chatgpt-and-whisper-apis). Record a voice message and ChatGPT will answer you!
- *2 Mar 2023*: Added support of [ChatGPT API](https://platform.openai.com/docs/guides/chat/introduction).
- *1 Aug 2023*: Added OpenAI API Base to config (useful while using OpenAI-compatible API like [LocalAI](https://github.com/go-skynet/LocalAI))
- *15 Nov 2023*: Added support of [GPT-4 Turbo](https://help.openai.com/en/articles/8555510-gpt-4-turbo)
- *2 Apr 2024*: Added [GPT-4 Vision](https://platform.openai.com/docs/guides/vision) support
- *20 May 2024*: forked from original repo with new features
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