### Version 1.0.0 - 20 May 2024

The day the fork diverged from the repo and took a life of its own.

  - Added GPT-4o support (text and vision)
  - Removed legacy completion models, only gpt-4o and gpt-3.5-turbo remain
  - Removed excessive chat modes
  - Added dynamic custom system prompt support

Old changes for posterity:
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

