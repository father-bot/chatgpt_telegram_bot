"""
Models Configuration for NagaAI Bot

This module manages AI models configuration with dynamic loading from API
and fallback to static configuration.
"""

import logging
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Model categories for UI
CATEGORY_NAMES = {
    "free": "Free Models",
    "fast": "Fast Models",
    "smart": "Smart Models",
    "premium": "Premium Models",
    "coding": "Coding Models",
    "image": "Image Models",
    "audio": "Audio Models",
    "embedding": "Embedding Models",
    "other": "Other Models",
}

CATEGORY_EMOJIS = {
    "free": "🆓",
    "fast": "⚡",
    "smart": "🧠",
    "premium": "💎",
    "coding": "💻",
    "image": "🎨",
    "audio": "🎵",
    "embedding": "📊",
    "other": "📦",
}

# Default models for each category (fallback if API unavailable)
DEFAULT_MODELS = {
    "free": [
        {
            "id": "gemini-2.5-flash:free",
            "name": "Gemini 2.5 Flash (Free)",
            "description": "Fast and free model from Google",
            "pricing": {"input": 0, "output": 0},
            "supports_vision": True,
            "supports_tools": True,
        },
        {
            "id": "deepseek-chat-v3.1:free",
            "name": "DeepSeek Chat (Free)",
            "description": "Powerful free model from DeepSeek",
            "pricing": {"input": 0, "output": 0},
            "supports_vision": False,
            "supports_tools": True,
        },
    ],
    "fast": [
        {
            "id": "gpt-4o-mini",
            "name": "GPT-4o Mini",
            "description": "Fast and affordable GPT-4 variant",
            "pricing": {"input": 0.15, "output": 0.6},
            "supports_vision": True,
            "supports_tools": True,
        },
        {
            "id": "claude-3-5-haiku-latest",
            "name": "Claude 3.5 Haiku",
            "description": "Fast Claude model for quick tasks",
            "pricing": {"input": 0.25, "output": 1.25},
            "supports_vision": True,
            "supports_tools": True,
        },
        {
            "id": "gemini-2.0-flash",
            "name": "Gemini 2.0 Flash",
            "description": "Google's fastest Gemini model",
            "pricing": {"input": 0.075, "output": 0.3},
            "supports_vision": True,
            "supports_tools": True,
        },
    ],
    "smart": [
        {
            "id": "gpt-4o",
            "name": "GPT-4o",
            "description": "OpenAI's flagship multimodal model",
            "pricing": {"input": 2.5, "output": 10},
            "supports_vision": True,
            "supports_tools": True,
        },
        {
            "id": "claude-3-5-sonnet-latest",
            "name": "Claude 3.5 Sonnet",
            "description": "Anthropic's balanced model for most tasks",
            "pricing": {"input": 3, "output": 15},
            "supports_vision": True,
            "supports_tools": True,
        },
        {
            "id": "gemini-2.5-pro-preview",
            "name": "Gemini 2.5 Pro",
            "description": "Google's most capable model",
            "pricing": {"input": 1.25, "output": 5},
            "supports_vision": True,
            "supports_tools": True,
        },
    ],
    "premium": [
        {
            "id": "claude-3-opus-latest",
            "name": "Claude 3 Opus",
            "description": "Most powerful Claude for complex tasks",
            "pricing": {"input": 15, "output": 75},
            "supports_vision": True,
            "supports_tools": True,
        },
        {
            "id": "gpt-4-turbo",
            "name": "GPT-4 Turbo",
            "description": "Enhanced GPT-4 with larger context",
            "pricing": {"input": 10, "output": 30},
            "supports_vision": True,
            "supports_tools": True,
        },
    ],
    "coding": [
        {
            "id": "deepseek-coder",
            "name": "DeepSeek Coder",
            "description": "Specialized model for coding tasks",
            "pricing": {"input": 0.14, "output": 0.28},
            "supports_vision": False,
            "supports_tools": True,
        },
        {
            "id": "codestral-latest",
            "name": "Codestral",
            "description": "Mistral's coding-focused model",
            "pricing": {"input": 0.3, "output": 0.9},
            "supports_vision": False,
            "supports_tools": True,
        },
    ],
}

# Cache for models loaded from API
_api_models_cache = {
    "models": None,
    "by_category": None,
    "last_updated": None,
    "ttl": timedelta(hours=24)
}


class ModelsManager:
    """Manages AI models configuration with dynamic API loading."""

    def __init__(self):
        self._models = {}
        self._by_category = {}
        self._initialized = False

    async def initialize(self, naga_client=None):
        """Initialize models from API or use defaults."""
        if self._initialized and self._models:
            return

        try:
            if naga_client:
                api_models = await naga_client.get_models_with_pricing()
                if api_models:
                    self._models = api_models
                    self._organize_by_category()
                    self._initialized = True
                    logger.info(f"Loaded {len(api_models)} models from NagaAI API")
                    return
        except Exception as e:
            logger.warning(f"Failed to load models from API: {e}")

        # Fallback to defaults
        self._load_defaults()
        self._initialized = True
        logger.info("Using default models configuration")

    def _load_defaults(self):
        """Load default models configuration."""
        self._models = {}
        for category, models in DEFAULT_MODELS.items():
            for model in models:
                model["category"] = category
                self._models[model["id"]] = model
        self._organize_by_category()

    def _organize_by_category(self):
        """Organize models by category."""
        self._by_category = {}
        for model_id, model in self._models.items():
            category = model.get("category", "other")
            if category not in self._by_category:
                self._by_category[category] = []
            self._by_category[category].append(model)

    def get_all_models(self) -> dict:
        """Get all available models."""
        if not self._initialized:
            self._load_defaults()
        return self._models

    def get_model(self, model_id: str) -> Optional[dict]:
        """Get specific model by ID."""
        return self._models.get(model_id)

    def get_models_by_category(self, category: str) -> list:
        """Get models filtered by category."""
        return self._by_category.get(category, [])

    def get_all_categories(self) -> list:
        """Get list of all categories with models."""
        return list(self._by_category.keys())

    def get_text_models(self) -> list:
        """Get all text/chat models (excluding image, audio, embedding)."""
        exclude_categories = {"image", "audio", "embedding"}
        result = []
        for category, models in self._by_category.items():
            if category not in exclude_categories:
                result.extend(models)
        return result

    def get_vision_models(self) -> list:
        """Get models that support vision/image input."""
        return [m for m in self._models.values() if m.get("supports_vision")]

    def get_free_models(self) -> list:
        """Get free models."""
        return [m for m in self._models.values() if m.get("is_free")]

    def get_default_model(self) -> str:
        """Get default model ID."""
        # Prefer free models, then fast
        free_models = self.get_free_models()
        if free_models:
            return free_models[0]["id"]

        fast_models = self.get_models_by_category("fast")
        if fast_models:
            return fast_models[0]["id"]

        # Fallback
        return "gpt-4o-mini"

    def format_model_for_display(self, model_id: str) -> str:
        """Format model info for display in bot."""
        model = self.get_model(model_id)
        if not model:
            return f"Unknown model: {model_id}"

        category = model.get("category", "other")
        emoji = CATEGORY_EMOJIS.get(category, "📦")
        name = model.get("name", model_id)
        pricing = model.get("pricing", {})

        if pricing.get("input", 0) == 0 and pricing.get("output", 0) == 0:
            price_str = "Free"
        else:
            price_str = f"${pricing.get('input', 0)}/{pricing.get('output', 0)} per 1M tokens"

        features = []
        if model.get("supports_vision"):
            features.append("Vision")
        if model.get("supports_tools"):
            features.append("Tools")

        features_str = ", ".join(features) if features else ""

        return f"{emoji} <b>{name}</b>\n{price_str}\n{features_str}"

    def format_models_list(self, category: Optional[str] = None) -> str:
        """Format models list for display."""
        if category:
            models = self.get_models_by_category(category)
            category_name = CATEGORY_NAMES.get(category, category.title())
            emoji = CATEGORY_EMOJIS.get(category, "📦")
            text = f"{emoji} <b>{category_name}</b>\n\n"
        else:
            models = self.get_text_models()
            text = "📋 <b>Available Models</b>\n\n"

        for model in models:
            name = model.get("name", model["id"])
            pricing = model.get("pricing", {})

            if pricing.get("input", 0) == 0:
                price_str = "🆓 Free"
            else:
                price_str = f"${pricing.get('input', 0):.2f}"

            text += f"• <code>{model['id']}</code>\n  {name} ({price_str})\n"

        return text


# Global instance
models_manager = ModelsManager()


async def get_models_manager() -> ModelsManager:
    """Get initialized models manager."""
    if not models_manager._initialized:
        from .naga_client import NagaAI
        naga = NagaAI()
        await models_manager.initialize(naga)
    return models_manager
