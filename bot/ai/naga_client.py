"""
NagaAI Client - OpenAI-compatible API client for NagaAI

This module provides a unified interface for interacting with NagaAI API,
which is fully compatible with OpenAI SDK.
"""

import base64
import logging
import json
from io import BytesIO
from typing import AsyncGenerator, Optional, Any
from datetime import datetime, timedelta

import tiktoken
import httpx
from openai import AsyncOpenAI

import config

logger = logging.getLogger(__name__)

# NagaAI API configuration
NAGA_API_BASE = "https://api.naga.ac/v1"

# Default completion options
DEFAULT_COMPLETION_OPTIONS = {
    "temperature": 0.7,
    "max_tokens": 4096,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}

# Cache for models list
_models_cache = {
    "models": None,
    "last_updated": None,
    "ttl": timedelta(hours=24)
}


class NagaAI:
    """
    NagaAI API Client

    Provides access to chat completions, image generation,
    speech-to-text, text-to-speech, and embeddings.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or config.openai_api_key
        self.base_url = base_url or config.openai_api_base or NAGA_API_BASE

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    async def chat_completion(
        self,
        messages: list,
        model: str = "gpt-4o-mini",
        stream: bool = False,
        **kwargs
    ):
        """Send a chat completion request."""
        options = {**DEFAULT_COMPLETION_OPTIONS, **kwargs}

        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=stream,
            **options
        )

        return response

    async def chat_completion_stream(
        self,
        messages: list,
        model: str = "gpt-4o-mini",
        **kwargs
    ) -> AsyncGenerator:
        """Send a streaming chat completion request."""
        options = {**DEFAULT_COMPLETION_OPTIONS, **kwargs}

        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            **options
        )

        async for chunk in stream:
            yield chunk

    async def transcribe_audio(
        self,
        audio_file: BytesIO,
        model: str = "scribe-v1",
        language: Optional[str] = None
    ) -> str:
        """Transcribe audio to text using Scribe v1."""
        kwargs = {"model": model, "file": audio_file}
        if language:
            kwargs["language"] = language

        response = await self.client.audio.transcriptions.create(**kwargs)
        return response.text or ""

    async def generate_speech(
        self,
        text: str,
        model: str = "tts-1",
        voice: str = "alloy",
        response_format: str = "mp3"
    ) -> bytes:
        """Generate speech from text."""
        response = await self.client.audio.speech.create(
            model=model,
            input=text,
            voice=voice,
            response_format=response_format
        )
        return response.content

    async def generate_image(
        self,
        prompt: str,
        model: str = "dall-e-3",
        size: str = "1024x1024",
        n: int = 1,
        quality: str = "standard"
    ) -> list[str]:
        """Generate images from text prompt."""
        response = await self.client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            n=n,
            quality=quality
        )
        return [item.url for item in response.data]

    async def create_embedding(
        self,
        text: str | list[str],
        model: str = "text-embedding-3-small"
    ) -> list:
        """Create embeddings for text."""
        response = await self.client.embeddings.create(
            model=model,
            input=text
        )
        return [item.embedding for item in response.data]

    async def list_models(self, force_refresh: bool = False) -> list[dict]:
        """
        Get list of available models with their info from NagaAI API.
        Results are cached for 24 hours.
        """
        global _models_cache

        # Check cache
        if not force_refresh and _models_cache["models"] is not None:
            if _models_cache["last_updated"] and \
               datetime.now() - _models_cache["last_updated"] < _models_cache["ttl"]:
                return _models_cache["models"]

        try:
            response = await self.client.models.list()
            models = []

            for model in response.data:
                model_info = {
                    "id": model.id,
                    "object": model.object,
                    "created": model.created,
                    "owned_by": getattr(model, "owned_by", "unknown"),
                }

                # Try to extract additional info if available
                if hasattr(model, "pricing"):
                    model_info["pricing"] = model.pricing

                models.append(model_info)

            # Update cache
            _models_cache["models"] = models
            _models_cache["last_updated"] = datetime.now()

            return models

        except Exception as e:
            logger.error(f"Failed to fetch models: {e}")
            # Return cached data if available, even if expired
            if _models_cache["models"]:
                return _models_cache["models"]
            return []

    async def get_models_with_pricing(self) -> dict:
        """
        Fetch models with pricing information from NagaAI.
        Returns a dict with model info suitable for the config.
        """
        try:
            async with httpx.AsyncClient() as client:
                # First, get the models list
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()

                models_dict = {}
                for model in data.get("data", []):
                    model_id = model.get("id", "")
                    if not model_id:
                        continue

                    # Categorize model
                    category = self._categorize_model(model_id)

                    models_dict[model_id] = {
                        "id": model_id,
                        "name": self._format_model_name(model_id),
                        "category": category,
                        "owned_by": model.get("owned_by", "unknown"),
                        "created": model.get("created", 0),
                        # Pricing will be estimated if not provided
                        "pricing": self._estimate_pricing(model_id, model),
                        "supports_vision": self._supports_vision(model_id),
                        "supports_tools": self._supports_tools(model_id),
                        "is_free": ":free" in model_id.lower() or "free" in model_id.lower(),
                    }

                return models_dict

        except Exception as e:
            logger.error(f"Failed to fetch models with pricing: {e}")
            return {}

    def _categorize_model(self, model_id: str) -> str:
        """Categorize model based on its name."""
        model_lower = model_id.lower()

        if ":free" in model_lower or "free" in model_lower:
            return "free"
        elif "claude" in model_lower:
            if "opus" in model_lower:
                return "premium"
            elif "sonnet" in model_lower:
                return "smart"
            else:
                return "fast"
        elif "gpt-4" in model_lower:
            if "mini" in model_lower:
                return "fast"
            else:
                return "smart"
        elif "gpt-3" in model_lower or "gpt-5" in model_lower:
            return "smart"
        elif "gemini" in model_lower:
            if "flash" in model_lower:
                return "fast"
            elif "pro" in model_lower:
                return "smart"
            else:
                return "smart"
        elif "deepseek" in model_lower:
            if "coder" in model_lower:
                return "coding"
            else:
                return "smart"
        elif "codestral" in model_lower or "coder" in model_lower:
            return "coding"
        elif "mistral" in model_lower or "mixtral" in model_lower:
            return "fast"
        elif "llama" in model_lower:
            return "fast"
        elif "dall-e" in model_lower or "flux" in model_lower or "stable" in model_lower:
            return "image"
        elif "whisper" in model_lower or "scribe" in model_lower:
            return "audio"
        elif "tts" in model_lower or "speech" in model_lower:
            return "audio"
        elif "embedding" in model_lower:
            return "embedding"
        else:
            return "other"

    def _format_model_name(self, model_id: str) -> str:
        """Format model ID to a human-readable name."""
        # Remove common suffixes
        name = model_id.replace(":free", " (Free)")
        name = name.replace("-preview", " Preview")
        name = name.replace("-latest", "")

        # Capitalize properly
        parts = name.split("-")
        formatted = []
        for part in parts:
            if part.lower() in ["gpt", "dall", "tts", "stt"]:
                formatted.append(part.upper())
            elif part.isdigit() or part.replace(".", "").isdigit():
                formatted.append(part)
            else:
                formatted.append(part.capitalize())

        return " ".join(formatted)

    def _estimate_pricing(self, model_id: str, model_data: dict) -> dict:
        """Estimate pricing for a model based on its name/category."""
        # If pricing is provided in API response, use it
        if "pricing" in model_data:
            return model_data["pricing"]

        model_lower = model_id.lower()

        # Estimated prices per 1M tokens (input/output)
        pricing_estimates = {
            # Free models
            "free": {"input": 0, "output": 0},
            # GPT models
            "gpt-4o-mini": {"input": 0.15, "output": 0.6},
            "gpt-4o": {"input": 2.5, "output": 10},
            "gpt-4-turbo": {"input": 10, "output": 30},
            "gpt-4": {"input": 30, "output": 60},
            # Claude models
            "claude-3-5-sonnet": {"input": 3, "output": 15},
            "claude-3-5-haiku": {"input": 0.25, "output": 1.25},
            "claude-3-opus": {"input": 15, "output": 75},
            # Gemini models
            "gemini-flash": {"input": 0.075, "output": 0.3},
            "gemini-pro": {"input": 1.25, "output": 5},
            # DeepSeek
            "deepseek": {"input": 0.14, "output": 0.28},
            # Default
            "default": {"input": 1, "output": 3},
        }

        if ":free" in model_lower or "free" in model_lower:
            return pricing_estimates["free"]

        for key, pricing in pricing_estimates.items():
            if key in model_lower:
                return pricing

        return pricing_estimates["default"]

    def _supports_vision(self, model_id: str) -> bool:
        """Check if model supports vision/image input."""
        model_lower = model_id.lower()
        vision_models = [
            "gpt-4o", "gpt-4-vision", "gpt-4-turbo",
            "claude-3", "gemini", "llava"
        ]
        return any(vm in model_lower for vm in vision_models)

    def _supports_tools(self, model_id: str) -> bool:
        """Check if model supports tool/function calling."""
        model_lower = model_id.lower()
        # Most modern models support tools
        no_tools = ["dall-e", "whisper", "tts", "embedding", "scribe"]
        return not any(nt in model_lower for nt in no_tools)


class ChatGPT:
    """
    ChatGPT-compatible interface for backward compatibility with existing bot code.

    This class wraps NagaAI client and provides the same interface as the original
    openai_utils.ChatGPT class.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.naga = NagaAI()

    async def send_message(
        self,
        message: str,
        dialog_messages: list = None,
        chat_mode: str = "assistant"
    ) -> tuple[str, tuple[int, int], int]:
        """
        Send a message and get a response.

        Returns:
            tuple: (answer, (n_input_tokens, n_output_tokens), n_first_dialog_messages_removed)
        """
        if dialog_messages is None:
            dialog_messages = []

        if chat_mode not in config.chat_modes:
            raise ValueError(f"Chat mode {chat_mode} is not supported")

        n_dialog_messages_before = len(dialog_messages)
        answer = None

        while answer is None:
            try:
                messages = self._generate_prompt_messages(message, dialog_messages, chat_mode)

                response = await self.naga.chat_completion(
                    messages=messages,
                    model=self.model,
                    stream=False
                )

                answer = response.choices[0].message.content
                answer = self._postprocess_answer(answer)

                n_input_tokens = response.usage.prompt_tokens
                n_output_tokens = response.usage.completion_tokens

            except Exception as e:
                error_msg = str(e).lower()
                if "too many tokens" in error_msg or "context_length_exceeded" in error_msg:
                    if len(dialog_messages) == 0:
                        raise ValueError(
                            "Dialog messages is reduced to zero, but still has too many tokens"
                        ) from e
                    dialog_messages = dialog_messages[1:]
                else:
                    raise

        n_first_dialog_messages_removed = n_dialog_messages_before - len(dialog_messages)
        return answer, (n_input_tokens, n_output_tokens), n_first_dialog_messages_removed

    async def send_message_stream(
        self,
        message: str,
        dialog_messages: list = None,
        chat_mode: str = "assistant"
    ) -> AsyncGenerator:
        """
        Send a message and stream the response.

        Yields:
            tuple: (status, answer, (n_input_tokens, n_output_tokens), n_first_dialog_messages_removed)
        """
        if dialog_messages is None:
            dialog_messages = []

        if chat_mode not in config.chat_modes:
            raise ValueError(f"Chat mode {chat_mode} is not supported")

        n_dialog_messages_before = len(dialog_messages)
        answer = None

        while answer is None:
            try:
                messages = self._generate_prompt_messages(message, dialog_messages, chat_mode)

                answer = ""
                async for chunk in self.naga.chat_completion_stream(
                    messages=messages,
                    model=self.model
                ):
                    if chunk.choices and chunk.choices[0].delta.content:
                        answer += chunk.choices[0].delta.content
                        n_input_tokens, n_output_tokens = self._count_tokens_from_messages(
                            messages, answer, model=self.model
                        )
                        n_first_dialog_messages_removed = 0

                        yield "not_finished", answer, (n_input_tokens, n_output_tokens), n_first_dialog_messages_removed

                answer = self._postprocess_answer(answer)

            except Exception as e:
                error_msg = str(e).lower()
                if "too many tokens" in error_msg or "context_length_exceeded" in error_msg:
                    if len(dialog_messages) == 0:
                        raise
                    dialog_messages = dialog_messages[1:]
                    answer = None
                else:
                    raise

        n_first_dialog_messages_removed = n_dialog_messages_before - len(dialog_messages)
        yield "finished", answer, (n_input_tokens, n_output_tokens), n_first_dialog_messages_removed

    async def send_vision_message(
        self,
        message: str,
        dialog_messages: list = None,
        chat_mode: str = "assistant",
        image_buffer: BytesIO = None
    ) -> tuple[str, tuple[int, int], int]:
        """Send a message with an image and get a response."""
        if dialog_messages is None:
            dialog_messages = []

        n_dialog_messages_before = len(dialog_messages)
        answer = None

        while answer is None:
            try:
                messages = self._generate_prompt_messages(
                    message, dialog_messages, chat_mode, image_buffer
                )

                response = await self.naga.chat_completion(
                    messages=messages,
                    model=self.model,
                    stream=False
                )

                answer = response.choices[0].message.content
                answer = self._postprocess_answer(answer)

                n_input_tokens = response.usage.prompt_tokens
                n_output_tokens = response.usage.completion_tokens

            except Exception as e:
                error_msg = str(e).lower()
                if "too many tokens" in error_msg or "context_length_exceeded" in error_msg:
                    if len(dialog_messages) == 0:
                        raise ValueError(
                            "Dialog messages is reduced to zero, but still has too many tokens"
                        ) from e
                    dialog_messages = dialog_messages[1:]
                else:
                    raise

        n_first_dialog_messages_removed = n_dialog_messages_before - len(dialog_messages)
        return answer, (n_input_tokens, n_output_tokens), n_first_dialog_messages_removed

    async def send_vision_message_stream(
        self,
        message: str,
        dialog_messages: list = None,
        chat_mode: str = "assistant",
        image_buffer: BytesIO = None
    ) -> AsyncGenerator:
        """Send a message with an image and stream the response."""
        if dialog_messages is None:
            dialog_messages = []

        n_dialog_messages_before = len(dialog_messages)
        answer = None

        while answer is None:
            try:
                messages = self._generate_prompt_messages(
                    message, dialog_messages, chat_mode, image_buffer
                )

                answer = ""
                async for chunk in self.naga.chat_completion_stream(
                    messages=messages,
                    model=self.model
                ):
                    if chunk.choices and chunk.choices[0].delta.content:
                        answer += chunk.choices[0].delta.content
                        n_input_tokens, n_output_tokens = self._count_tokens_from_messages(
                            messages, answer, model=self.model
                        )
                        n_first_dialog_messages_removed = n_dialog_messages_before - len(dialog_messages)

                        yield "not_finished", answer, (n_input_tokens, n_output_tokens), n_first_dialog_messages_removed

                answer = self._postprocess_answer(answer)

            except Exception as e:
                error_msg = str(e).lower()
                if "too many tokens" in error_msg or "context_length_exceeded" in error_msg:
                    if len(dialog_messages) == 0:
                        raise
                    dialog_messages = dialog_messages[1:]
                    answer = None
                else:
                    raise

        n_first_dialog_messages_removed = n_dialog_messages_before - len(dialog_messages)
        yield "finished", answer, (n_input_tokens, n_output_tokens), n_first_dialog_messages_removed

    def _encode_image(self, image_buffer: BytesIO) -> str:
        """Encode image to base64 string."""
        image_buffer.seek(0)
        return base64.b64encode(image_buffer.read()).decode("utf-8")

    def _generate_prompt_messages(
        self,
        message: str,
        dialog_messages: list,
        chat_mode: str,
        image_buffer: BytesIO = None
    ) -> list:
        """Generate messages for the API request."""
        prompt = config.chat_modes[chat_mode]["prompt_start"]
        messages = [{"role": "system", "content": prompt}]

        for dialog_message in dialog_messages:
            user_content = dialog_message.get("user", "")

            # Handle different user content formats
            if isinstance(user_content, list):
                # New format with type/text structure
                text_parts = [p.get("text", "") for p in user_content if p.get("type") == "text"]
                user_text = " ".join(text_parts)
            else:
                user_text = user_content

            messages.append({"role": "user", "content": user_text})
            messages.append({"role": "assistant", "content": dialog_message.get("bot", "")})

        # Add current message
        if image_buffer is not None:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": message},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{self._encode_image(image_buffer)}",
                            "detail": "high"
                        }
                    }
                ]
            })
        else:
            messages.append({"role": "user", "content": message})

        return messages

    def _postprocess_answer(self, answer: str) -> str:
        """Clean up the answer."""
        return answer.strip() if answer else ""

    def _count_tokens_from_messages(
        self,
        messages: list,
        answer: str,
        model: str = "gpt-4o-mini"
    ) -> tuple[int, int]:
        """Count tokens in messages and answer."""
        try:
            # Try to get encoding for model, fallback to cl100k_base
            try:
                encoding = tiktoken.encoding_for_model(model)
            except KeyError:
                encoding = tiktoken.get_encoding("cl100k_base")

            # Token counts per message vary by model
            tokens_per_message = 3

            n_input_tokens = 0
            for message in messages:
                n_input_tokens += tokens_per_message
                content = message.get("content", "")

                if isinstance(content, list):
                    for sub_message in content:
                        if sub_message.get("type") == "text":
                            n_input_tokens += len(encoding.encode(sub_message.get("text", "")))
                elif isinstance(content, str):
                    n_input_tokens += len(encoding.encode(content))

            n_input_tokens += 2  # For reply priming
            n_output_tokens = 1 + len(encoding.encode(answer))

            return n_input_tokens, n_output_tokens

        except Exception:
            # Fallback: rough estimate (4 chars per token)
            input_text = str(messages)
            return len(input_text) // 4, len(answer) // 4


# Standalone functions for backward compatibility

async def transcribe_audio(audio_file: BytesIO) -> str:
    """Transcribe audio to text using Scribe v1."""
    naga = NagaAI()
    return await naga.transcribe_audio(audio_file, model="scribe-v1")


async def generate_images(prompt: str, n_images: int = 4, size: str = "512x512") -> list[str]:
    """Generate images from text prompt."""
    naga = NagaAI()
    return await naga.generate_image(prompt, n=n_images, size=size)


async def generate_speech(text: str, voice: str = "alloy") -> bytes:
    """Generate speech from text."""
    naga = NagaAI()
    return await naga.generate_speech(text, voice=voice)


async def is_content_acceptable(prompt: str) -> bool:
    """Check if content is acceptable using moderation."""
    # NagaAI uses OpenAI-compatible API, moderation endpoint may vary
    # For now, return True and implement proper moderation later
    return True


async def get_available_models() -> dict:
    """Get all available models with pricing from NagaAI API."""
    naga = NagaAI()
    return await naga.get_models_with_pricing()
