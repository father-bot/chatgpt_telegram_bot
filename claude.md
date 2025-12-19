# AI Telegram Bot на базе NagaAI

## Обзор проекта

**Название:** AI Telegram Bot на базе NagaAI
**Базовое решение:** karfly/chatgpt_telegram_bot (Python)
**API провайдер:** NagaAI (https://api.naga.ac/v1)

**Цель:** Создать многофункционального телеграм-бота с AI-возможностями, поддержкой множества моделей, расширенным функционалом (tool calling, voice, documents) и монетизацией через Telegram Stars.

---

## NagaAI API Reference

### Основная информация

- **Base URL:** `https://api.naga.ac/v1`
- **Docs:** https://api.naga.ac/docs
- **Совместимость:** OpenAI SDK (замена только `base_url`)

### Аутентификация

```python
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
```

### Endpoints

#### 1. Chat Completions
`POST /v1/chat/completions`

```python
{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello"}],
    "temperature": 0.7,
    "stream": False,
    "tools": [],  # для tool calling
    "web_search_options": {},  # для веб-поиска
    "response_format": {"type": "json_schema", ...}  # structured output
}
```

**Поддерживаемые content types:**
- `text` — текст
- `image_url` — изображение (Vision)
- `file` — файл (PDF и др.)
- `input_audio` — аудио

#### 2. Image Generation
`POST /v1/images/generations`

```python
{
    "model": "dall-e-3",
    "prompt": "A beautiful sunset",
    "size": "1024x1024",
    "quality": "standard",
    "n": 1
}
```

#### 3. Speech-to-Text (Whisper)
`POST /v1/audio/transcriptions`

```python
# multipart/form-data
{
    "model": "whisper-1",
    "file": audio_file,
    "language": "ru"
}
```

#### 4. Text-to-Speech
`POST /v1/audio/speech`

```python
{
    "model": "tts-1",
    "input": "Привет, мир!",
    "voice": "alloy",
    "response_format": "mp3"
}
```

#### 5. Embeddings
`POST /v1/embeddings`

```python
{
    "model": "text-embedding-3-small",
    "input": ["text1", "text2"]
}
```

#### 6. Models List
`GET /v1/models`

#### 7. Account
- `GET /v1/account/balance` — баланс
- `GET /v1/account/activity` — статистика использования
- `GET/POST/PATCH/DELETE /v1/account/keys` — управление API ключами

### Tool Calling

```python
{
    "model": "gpt-4",
    "messages": [...],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather for a city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"}
                    },
                    "required": ["location"]
                }
            }
        }
    ],
    "tool_choice": "auto"
}
```

### Web Search

```python
{
    "model": "gpt-4",
    "messages": [...],
    "web_search_options": {
        "enabled": True
    }
}
```

Поддерживается: Grok, OpenAI, Google, Sonar модели.

### Streaming

```python
{
    "model": "gpt-4",
    "messages": [...],
    "stream": True,
    "stream_options": {"include_usage": True}
}
```

---

## Оценка ТЗ

### Совместимость с NagaAI

| Функция | Поддержка | Endpoint |
|---------|-----------|----------|
| Chat | ✅ | `/v1/chat/completions` |
| Streaming | ✅ | `stream: true` |
| Tool Calling | ✅ | `tools` parameter |
| Vision | ✅ | `image_url` в content |
| Image Gen | ✅ | `/v1/images/generations` |
| STT | ✅ | `/v1/audio/transcriptions` |
| TTS | ✅ | `/v1/audio/speech` |
| Web Search | ✅ | `web_search_options` |
| Structured Output | ✅ | `json_schema` |
| Embeddings | ✅ | `/v1/embeddings` |

### Сложность по этапам

| Этап | Сложность | Дни |
|------|-----------|-----|
| 1. Подготовка | 🟢 Низкая | 1-2 |
| 2. NagaAI интеграция | 🟢 Низкая | 2-3 |
| 3. Базовый функционал | 🟡 Средняя | 2-3 |
| 4. Tool Calling | 🟡 Средняя | 3-4 |
| 5. Voice | 🟢 Низкая | 2-3 |
| 6. Documents | 🟡 Средняя | 2-3 |
| 7. Billing | 🔴 Высокая | 3-4 |
| 8. Telegram Stars | 🔴 Высокая | 2-3 |
| 9. Уникальные фичи | 🔴 Высокая | 4-5 |
| 10. Developer API | 🟡 Средняя | 3-4 |
| 11. Admin panel | 🟡 Средняя | 2-3 |
| 12. Testing | 🟡 Средняя | 3-4 |
| 13. Deploy | 🟡 Средняя | 2-3 |
| 14. Docs | 🟢 Низкая | 1-2 |

**Итого:** 32-46 дней (6-9 недель full-time)

### Критические риски

1. **Telegram Payments (Stars)** — мало документации
2. **Code Execution sandbox** — безопасность (рекомендуется Judge0 API)
3. **Smart Routing** — нужен классификатор
4. **Масштабируемость** — очередь задач при росте

---

## Архитектура

### Текущая структура (karfly/chatgpt_telegram_bot)

```
chatgpt_telegram_bot/
├── bot/
│   ├── __init__.py
│   ├── config.py           # Конфигурация
│   ├── database.py         # MongoDB
│   ├── openai_utils.py     # OpenAI клиент
│   └── bot.py              # Основная логика
├── config/
│   ├── config.example.yml
│   ├── config.example.env
│   ├── chat_modes.yml
│   └── models.yml
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

### Целевая структура

```
ai-telegram-bot/
├── bot/
│   ├── __init__.py
│   ├── config.py
│   ├── database/
│   │   ├── mongodb.py
│   │   ├── models.py
│   │   └── redis.py
│   ├── ai/
│   │   ├── naga_client.py       # NagaAI клиент
│   │   ├── models_config.py
│   │   ├── smart_routing.py
│   │   └── agents.py
│   ├── tools/
│   │   ├── base.py
│   │   ├── web_search.py
│   │   ├── image_gen.py
│   │   ├── code_exec.py
│   │   └── calculator.py
│   ├── voice/
│   │   ├── stt.py
│   │   └── tts.py
│   ├── documents/
│   │   ├── pdf_handler.py
│   │   ├── image_handler.py
│   │   └── ocr.py
│   ├── billing/
│   │   ├── plans.py
│   │   ├── tokens_tracker.py
│   │   └── limits.py
│   ├── payments/
│   │   ├── telegram_stars.py
│   │   └── webhooks.py
│   ├── memory/
│   │   ├── context_manager.py
│   │   └── long_term_memory.py
│   ├── referrals/
│   │   └── referral_system.py
│   ├── handlers/
│   │   ├── message_handler.py
│   │   ├── command_handler.py
│   │   ├── callback_handler.py
│   │   └── payment_handler.py
│   ├── admin/
│   │   ├── admin_panel.py
│   │   └── analytics.py
│   └── telegram_bot.py
├── api/
│   ├── main.py              # FastAPI
│   ├── routes/
│   └── auth.py
├── tests/
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Тарифные планы

```python
PLANS = {
    "free": {
        "tokens_per_month": 50_000,
        "models": ["gemini-2.5-flash:free", "deepseek-chat-v3.1:free"],
        "tools": ["web_search", "calculator"],
        "price_stars": 0
    },
    "basic": {
        "tokens_per_month": 500_000,
        "models": ["gpt-4o-mini", "claude-haiku-4-5", "gemini-flash"],
        "tools": ["all"],
        "price_stars": 50
    },
    "pro": {
        "tokens_per_month": 2_000_000,
        "models": ["all_except_opus"],
        "tools": ["all"],
        "priority": True,
        "price_stars": 200
    },
    "ultra": {
        "tokens_per_month": "unlimited",
        "models": ["all"],
        "tools": ["all"],
        "priority": True,
        "api_access": True,
        "price_stars": 500
    }
}

TOKEN_PACKAGES = {
    "small": {"tokens": 100_000, "price_stars": 10, "bonus": 0},
    "medium": {"tokens": 600_000, "price_stars": 50, "bonus": 0.2},
    "large": {"tokens": 3_000_000, "price_stars": 200, "bonus": 0.5}
}
```

---

## База данных (MongoDB)

### Collections

**users**
```json
{
    "_id": "telegram_user_id",
    "username": "string",
    "first_name": "string",
    "created_at": "datetime",
    "subscription_plan": "free|basic|pro|ultra",
    "subscription_expires": "datetime",
    "tokens_balance": 50000,
    "tokens_used_total": 0,
    "selected_model": "gpt-4o-mini",
    "settings": {
        "auto_tts": false,
        "voice_type": "alloy",
        "language": "ru",
        "smart_routing": false
    },
    "referral_code": "ABC123",
    "referred_by": null
}
```

**chats**
```json
{
    "_id": "ObjectId",
    "user_id": "telegram_user_id",
    "chat_id": "telegram_chat_id",
    "messages": [
        {
            "role": "user|assistant|system",
            "content": "string",
            "timestamp": "datetime",
            "model": "string",
            "tokens": 150
        }
    ],
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

**payments**
```json
{
    "_id": "ObjectId",
    "user_id": "telegram_user_id",
    "payment_id": "string",
    "amount_stars": 50,
    "product": "subscription|tokens",
    "product_id": "basic|small",
    "status": "pending|success|failed",
    "created_at": "datetime"
}
```

**memory**
```json
{
    "_id": "ObjectId",
    "user_id": "telegram_user_id",
    "facts": [
        {
            "fact": "User is a Python developer",
            "category": "technical",
            "timestamp": "datetime"
        }
    ]
}
```

### Redis Keys

- `rate_limit:{user_id}` — rate limiting
- `context:{chat_id}` — временный контекст (TTL 1 час)
- `cache:models` — кеш моделей (TTL 1 день)
- `session:{user_id}` — сессия пользователя

---

## План реализации

### MVP (Phase 1) — 2-3 недели

- [x] Оценка ТЗ и документация
- [ ] NagaAI клиент (замена OpenAI)
- [ ] Переключение моделей
- [ ] История диалогов
- [ ] Базовый billing (Free/Pro)
- [ ] Telegram Stars оплата
- [ ] Web Search tool

### Phase 2 — 2-3 недели

- [ ] Voice (STT/TTS)
- [ ] Работа с документами (PDF, images)
- [ ] Умная маршрутизация
- [ ] Полный набор tools

### Phase 3 — 2-3 недели

- [ ] Multi-agent система
- [ ] Долгосрочная память
- [ ] Реферальная система
- [ ] Admin панель

### Phase 4 — 2-3 недели

- [ ] Developer API (FastAPI)
- [ ] Групповые чаты
- [ ] Продвинутая аналитика
- [ ] Тесты и документация

---

## Полезные ссылки

- **NagaAI:** https://naga.ac
- **NagaAI API Docs:** https://api.naga.ac/docs
- **NagaAI Models:** https://naga.ac/models
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **Telegram Payments:** https://core.telegram.org/bots/payments
- **python-telegram-bot:** https://python-telegram-bot.org/

---

## Команды бота (планируемые)

### Основные
- `/start` — начало работы
- `/help` — справка
- `/model` — выбрать модель
- `/models` — список моделей
- `/clear` — очистить контекст
- `/history` — история диалогов

### Голос
- `/voice on|off` — авто-TTS
- `/voice_select` — выбор голоса

### Tools
- `/search <query>` — веб-поиск
- `/image <prompt>` — генерация изображения
- `/tools` — список инструментов

### Billing
- `/balance` — баланс токенов
- `/usage` — статистика
- `/subscribe` — подписка
- `/buy_tokens` — купить токены

### Memory
- `/memory` — показать память
- `/memory_add` — добавить факт
- `/memory_clear` — очистить

### Admin
- `/admin` — панель администратора
- `/broadcast` — рассылка
- `/stats` — статистика

---

## NagaAI Client Example

```python
from openai import OpenAI

class NagaAIClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(
            base_url="https://api.naga.ac/v1",
            api_key=api_key
        )

    def chat(self, messages: list, model: str = "gpt-4o-mini", **kwargs):
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )

    def chat_stream(self, messages: list, model: str = "gpt-4o-mini", **kwargs):
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            **kwargs
        )

    def transcribe(self, audio_file, language: str = "ru"):
        return self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language
        )

    def speak(self, text: str, voice: str = "alloy"):
        return self.client.audio.speech.create(
            model="tts-1",
            input=text,
            voice=voice
        )

    def generate_image(self, prompt: str, size: str = "1024x1024"):
        return self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size
        )

    def get_models(self):
        return self.client.models.list()
```

---

*Документ создан: 2025-12-19*
*Последнее обновление: 2025-12-19*
