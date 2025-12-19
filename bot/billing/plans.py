"""
Billing Plans Configuration

Defines subscription plans and token packages for the bot.
"""

from typing import Optional

# Subscription plans
PLANS = {
    "free": {
        "name": "Free",
        "description": "Basic access with limited tokens",
        "tokens_per_month": 50_000,
        "models": [
            "gemini-2.5-flash:free",
            "deepseek-chat-v3.1:free",
            "llama-3.1-8b:free",
        ],
        "model_categories": ["free"],
        "tools": ["calculator"],
        "features": {
            "web_search": False,
            "image_generation": False,
            "voice_messages": True,
            "tts": False,
            "documents": False,
            "priority_queue": False,
        },
        "rate_limits": {
            "requests_per_minute": 10,
            "requests_per_hour": 50,
        },
        "price_stars": 0,
        "price_usd": 0,
    },
    "basic": {
        "name": "Basic",
        "description": "More tokens and access to fast models",
        "tokens_per_month": 500_000,
        "models": "fast",  # All models in 'fast' category
        "model_categories": ["free", "fast"],
        "tools": ["calculator", "web_search"],
        "features": {
            "web_search": True,
            "image_generation": False,
            "voice_messages": True,
            "tts": True,
            "documents": True,
            "priority_queue": False,
        },
        "rate_limits": {
            "requests_per_minute": 20,
            "requests_per_hour": 200,
        },
        "price_stars": 50,
        "price_usd": 4.99,
    },
    "pro": {
        "name": "Pro",
        "description": "Full access to smart models and all tools",
        "tokens_per_month": 2_000_000,
        "models": "smart",  # All models in 'smart' category and below
        "model_categories": ["free", "fast", "smart", "coding"],
        "tools": "all",
        "features": {
            "web_search": True,
            "image_generation": True,
            "voice_messages": True,
            "tts": True,
            "documents": True,
            "priority_queue": True,
        },
        "rate_limits": {
            "requests_per_minute": 30,
            "requests_per_hour": 500,
        },
        "price_stars": 200,
        "price_usd": 14.99,
    },
    "ultra": {
        "name": "Ultra",
        "description": "Unlimited access to all models including premium",
        "tokens_per_month": -1,  # Unlimited
        "models": "all",
        "model_categories": ["free", "fast", "smart", "coding", "premium"],
        "tools": "all",
        "features": {
            "web_search": True,
            "image_generation": True,
            "voice_messages": True,
            "tts": True,
            "documents": True,
            "priority_queue": True,
            "api_access": True,
        },
        "rate_limits": {
            "requests_per_minute": 60,
            "requests_per_hour": 1000,
        },
        "price_stars": 500,
        "price_usd": 29.99,
    },
}

# Token packages (pay-as-you-go)
TOKEN_PACKAGES = {
    "small": {
        "name": "Small Pack",
        "tokens": 100_000,
        "bonus": 0,
        "price_stars": 10,
        "price_usd": 0.99,
    },
    "medium": {
        "name": "Medium Pack",
        "tokens": 600_000,
        "bonus": 0.2,  # 20% bonus
        "price_stars": 50,
        "price_usd": 4.99,
    },
    "large": {
        "name": "Large Pack",
        "tokens": 3_000_000,
        "bonus": 0.5,  # 50% bonus
        "price_stars": 200,
        "price_usd": 14.99,
    },
    "mega": {
        "name": "Mega Pack",
        "tokens": 10_000_000,
        "bonus": 1.0,  # 100% bonus (double)
        "price_stars": 500,
        "price_usd": 29.99,
    },
}


def get_plan(plan_id: str) -> Optional[dict]:
    """Get plan by ID."""
    return PLANS.get(plan_id)


def get_plan_limits(plan_id: str) -> dict:
    """Get rate limits for a plan."""
    plan = PLANS.get(plan_id, PLANS["free"])
    return plan.get("rate_limits", {})


def get_plan_tokens(plan_id: str) -> int:
    """Get monthly token limit for a plan."""
    plan = PLANS.get(plan_id, PLANS["free"])
    return plan.get("tokens_per_month", 50_000)


def can_use_model(plan_id: str, model_category: str) -> bool:
    """Check if plan allows using a model category."""
    plan = PLANS.get(plan_id, PLANS["free"])
    allowed_categories = plan.get("model_categories", ["free"])
    return model_category in allowed_categories


def can_use_feature(plan_id: str, feature: str) -> bool:
    """Check if plan allows using a feature."""
    plan = PLANS.get(plan_id, PLANS["free"])
    features = plan.get("features", {})
    return features.get(feature, False)


def get_package(package_id: str) -> Optional[dict]:
    """Get token package by ID."""
    return TOKEN_PACKAGES.get(package_id)


def calculate_package_tokens(package_id: str) -> int:
    """Calculate total tokens including bonus."""
    package = TOKEN_PACKAGES.get(package_id)
    if not package:
        return 0
    base_tokens = package["tokens"]
    bonus = package.get("bonus", 0)
    return int(base_tokens * (1 + bonus))


def format_plan_info(plan_id: str) -> str:
    """Format plan info for display."""
    plan = PLANS.get(plan_id)
    if not plan:
        return "Unknown plan"

    tokens = plan["tokens_per_month"]
    if tokens == -1:
        tokens_str = "Unlimited"
    else:
        tokens_str = f"{tokens:,}"

    features_list = []
    features = plan.get("features", {})
    if features.get("web_search"):
        features_list.append("Web Search")
    if features.get("image_generation"):
        features_list.append("Image Gen")
    if features.get("tts"):
        features_list.append("TTS")
    if features.get("documents"):
        features_list.append("Documents")
    if features.get("priority_queue"):
        features_list.append("Priority")

    features_str = ", ".join(features_list) if features_list else "Basic"

    price = plan["price_stars"]
    if price == 0:
        price_str = "Free"
    else:
        price_str = f"{price} Stars/month"

    return f"""
<b>{plan['name']}</b>
{plan['description']}

Tokens: {tokens_str}/month
Features: {features_str}
Price: {price_str}
"""


def format_all_plans() -> str:
    """Format all plans for display."""
    text = "<b>Subscription Plans</b>\n\n"

    for plan_id, plan in PLANS.items():
        emoji = "🆓" if plan_id == "free" else "⭐" * (list(PLANS.keys()).index(plan_id))
        tokens = plan["tokens_per_month"]
        tokens_str = "Unlimited" if tokens == -1 else f"{tokens:,}"
        price = plan["price_stars"]
        price_str = "Free" if price == 0 else f"{price} Stars"

        text += f"{emoji} <b>{plan['name']}</b> — {price_str}\n"
        text += f"   {tokens_str} tokens/month\n\n"

    return text
