"""
Token Usage Tracker

Tracks token usage per user and enforces limits based on subscription plans.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple

from .plans import PLANS, get_plan_tokens

logger = logging.getLogger(__name__)


class TokensTracker:
    """Tracks and manages token usage for users."""

    def __init__(self, database):
        self.db = database

    def get_user_tokens(self, user_id: int) -> dict:
        """Get user's token balance and usage."""
        user = self.db.user_collection.find_one({"_id": user_id})
        if not user:
            return {
                "balance": 0,
                "used_this_month": 0,
                "plan_limit": 50_000,
                "bonus_tokens": 0,
            }

        plan_id = user.get("subscription_plan", "free")
        plan_limit = get_plan_tokens(plan_id)

        # Calculate used tokens this month
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        used_this_month = self._calculate_monthly_usage(user_id, month_start)

        return {
            "balance": user.get("tokens_balance", 0),
            "used_this_month": used_this_month,
            "plan_limit": plan_limit,
            "bonus_tokens": user.get("bonus_tokens", 0),
            "plan": plan_id,
        }

    def _calculate_monthly_usage(self, user_id: int, month_start: datetime) -> int:
        """Calculate token usage for current month."""
        n_used_tokens = self.db.get_user_attribute(user_id, "n_used_tokens")
        if not n_used_tokens:
            return 0

        total = 0
        for model, usage in n_used_tokens.items():
            if isinstance(usage, dict):
                total += usage.get("n_input_tokens", 0) + usage.get("n_output_tokens", 0)

        return total

    def check_can_use_tokens(self, user_id: int, estimated_tokens: int = 1000) -> Tuple[bool, str]:
        """
        Check if user can use the estimated number of tokens.
        Returns (can_use, reason).
        """
        tokens = self.get_user_tokens(user_id)
        plan_limit = tokens["plan_limit"]
        used = tokens["used_this_month"]
        bonus = tokens["bonus_tokens"]

        # Unlimited plan
        if plan_limit == -1:
            return True, "Unlimited plan"

        # Check against plan limit + bonus tokens
        available = (plan_limit - used) + bonus
        if available < estimated_tokens:
            return False, f"Insufficient tokens. Available: {available:,}, Required: ~{estimated_tokens:,}"

        return True, "OK"

    def use_tokens(self, user_id: int, model: str, input_tokens: int, output_tokens: int) -> dict:
        """
        Record token usage for a request.
        Deducts from bonus tokens first, then from plan allocation.
        """
        total_tokens = input_tokens + output_tokens

        # Update the n_used_tokens in database
        n_used_tokens = self.db.get_user_attribute(user_id, "n_used_tokens") or {}

        if model in n_used_tokens:
            n_used_tokens[model]["n_input_tokens"] += input_tokens
            n_used_tokens[model]["n_output_tokens"] += output_tokens
        else:
            n_used_tokens[model] = {
                "n_input_tokens": input_tokens,
                "n_output_tokens": output_tokens
            }

        self.db.set_user_attribute(user_id, "n_used_tokens", n_used_tokens)

        # Check if we need to deduct from bonus tokens
        bonus_tokens = self.db.get_user_attribute(user_id, "bonus_tokens") or 0
        tokens_info = self.get_user_tokens(user_id)

        if tokens_info["plan_limit"] != -1:  # Not unlimited
            plan_remaining = tokens_info["plan_limit"] - tokens_info["used_this_month"]
            if plan_remaining < 0 and bonus_tokens > 0:
                # Deduct from bonus
                deduct_from_bonus = min(abs(plan_remaining), bonus_tokens)
                new_bonus = bonus_tokens - deduct_from_bonus
                self.db.set_user_attribute(user_id, "bonus_tokens", new_bonus)

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "model": model,
        }

    def add_bonus_tokens(self, user_id: int, tokens: int, reason: str = "") -> int:
        """Add bonus tokens to user's account."""
        current_bonus = self.db.get_user_attribute(user_id, "bonus_tokens") or 0
        new_bonus = current_bonus + tokens
        self.db.set_user_attribute(user_id, "bonus_tokens", new_bonus)

        logger.info(f"Added {tokens} bonus tokens to user {user_id}. Reason: {reason}")
        return new_bonus

    def get_usage_stats(self, user_id: int) -> dict:
        """Get detailed usage statistics for a user."""
        n_used_tokens = self.db.get_user_attribute(user_id, "n_used_tokens") or {}
        n_generated_images = self.db.get_user_attribute(user_id, "n_generated_images") or 0
        n_transcribed_seconds = self.db.get_user_attribute(user_id, "n_transcribed_seconds") or 0

        total_input = 0
        total_output = 0
        by_model = {}

        for model, usage in n_used_tokens.items():
            if isinstance(usage, dict):
                input_t = usage.get("n_input_tokens", 0)
                output_t = usage.get("n_output_tokens", 0)
                total_input += input_t
                total_output += output_t
                by_model[model] = {
                    "input": input_t,
                    "output": output_t,
                    "total": input_t + output_t,
                }

        return {
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "by_model": by_model,
            "images_generated": n_generated_images,
            "audio_transcribed_seconds": n_transcribed_seconds,
        }

    def format_balance(self, user_id: int) -> str:
        """Format balance info for display."""
        tokens = self.get_user_tokens(user_id)
        stats = self.get_usage_stats(user_id)

        plan_limit = tokens["plan_limit"]
        if plan_limit == -1:
            limit_str = "Unlimited"
            remaining_str = "Unlimited"
        else:
            limit_str = f"{plan_limit:,}"
            remaining = max(0, plan_limit - tokens["used_this_month"])
            remaining_str = f"{remaining:,}"

        text = f"""
<b>Your Balance</b>

Plan: <b>{tokens['plan'].title()}</b>
Monthly Limit: {limit_str} tokens

<b>This Month:</b>
Used: {tokens['used_this_month']:,} tokens
Remaining: {remaining_str}

<b>Bonus Tokens:</b> {tokens['bonus_tokens']:,}

<b>All-time Usage:</b>
Total: {stats['total_tokens']:,} tokens
Images: {stats['images_generated']}
Audio: {stats['audio_transcribed_seconds']:.0f} seconds
"""
        return text

    def format_usage(self, user_id: int) -> str:
        """Format detailed usage for display."""
        stats = self.get_usage_stats(user_id)

        text = "<b>Usage by Model</b>\n\n"

        if not stats["by_model"]:
            text += "No usage yet."
            return text

        # Sort by total usage
        sorted_models = sorted(
            stats["by_model"].items(),
            key=lambda x: x[1]["total"],
            reverse=True
        )

        for model, usage in sorted_models:
            text += f"<b>{model}</b>\n"
            text += f"  Input: {usage['input']:,} tokens\n"
            text += f"  Output: {usage['output']:,} tokens\n"
            text += f"  Total: {usage['total']:,} tokens\n\n"

        return text
