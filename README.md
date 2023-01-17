# ChatGPT Telegram Bot (**fast** and **no limits**)
We all love [chat.openai.com](https://chat.openai.com), but...

It's TERRIBLY laggy, has daily limits, and is only accessible through an archaic web interface.

This repo is ChatGPT re-created with GPT-3.5 LLM as Telegram Bot. **And it works great.**

## Features
- Low latency replies (it usually takes about 3-5 seconds) 
- No request limits
- Code highlighting
- Different chat modes (👩🏼‍🎓 Assistant, 👩🏼‍💻 Code Assistant, 🎬 Movie Expert)
- `/retry` command to regenerate last bot answer
- Control of allowed Telegram users
- *Next up*: warn user that the size of the context is close to the maximum

## Setup
1. Get your [OpenAI API](https://openai.com/api/) key

2. Get your Telegram bot token from [@BotFather](https://t.me/BotFather)

3. Edit `config.example.yml` to add your tokens and raname it to `config.yml`:
```bash
mv config.example.yml config.yml
```

🔥 And now **run**:

```bash
docker compose up --build
```

## References
1. [*Build ChatGPT from GPT-3*](https://learnprompting.org/docs/applied_prompting/build_chatgpt)