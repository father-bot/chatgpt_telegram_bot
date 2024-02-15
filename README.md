# ChatGPT Telegram Bot: **GPT-4. Fast. No daily limits. Special chat modes**

<div align="center">
<img src="https://raw.githubusercontent.com/karfly/chatgpt_telegram_bot/main/static/header.png" align="center" style="width: 100%" />
</div>

<br>
We all love [chat.openai.com](https://chat.openai.com), but... It's TERRIBLY laggy, has daily limits, and is only accessible through an archaic web interface.

This repo is ChatGPT re-created as Telegram Bot. **And it works great.**

## Features
- Low latency replies (it usually takes about 3-5 seconds)
- No request limits
- Message streaming (watch demo)
- GPT-4 and GPT-4 Turbo support
- Group Chat support (/help_group_chat to get instructions)
- DALLE 2 (choose 👩‍🎨 Artist mode to generate images)
- Voice message recognition
- Code highlighting
- 15 special chat modes: 👩🏼‍🎓 Assistant, 👩🏼‍💻 Code Assistant, 👩‍🎨 Artist, 🧠 Psychologist, 🚀 Elon Musk and other. You can easily create your own chat modes by editing `config/chat_modes.yml`
- Support of [ChatGPT API](https://platform.openai.com/docs/guides/chat/introduction)
- List of allowed Telegram users
- Track $ balance spent on OpenAI API

<p align="center">
  <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYmM2ZWVjY2M4NWQ3ZThkYmQ3MDhmMTEzZGUwOGFmOThlMDIzZGM4YiZjdD1n/unx907h7GSiLAugzVX/giphy.gif" />
</p>

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

## Bot commands
- `/retry` – Regenerate last bot answer
- `/new` – Start new dialog
- `/mode` – Select chat mode
- `/balance` – Show balance
- `/settings` – Show settings
- `/help` – Show help

## Setup
1. Get your [OpenAI API](https://openai.com/api/) key

2. Get your Telegram bot token from [@BotFather](https://t.me/BotFather)

3. Edit `config/config.example.yml` to set your tokens and run 2 commands below (*if you're advanced user, you can also edit* `config/config.example.env`):
    ```bash
    mv config/config.example.yml config/config.yml
    mv config/config.example.env config/config.env
    ```

4. 🔥 And now **run**:
    ```bash
    docker-compose -f docker-compose.yml up --build
    ```

## References
1. [*Build ChatGPT from GPT-3*](https://learnprompting.org/docs/applied_prompting/build_chatgpt)
