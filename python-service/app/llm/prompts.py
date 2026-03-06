from typing import Any


# Builds a simple prompt string from goal and optional profile data.
def build_goal_prompt(user_goal: str, user_profile: dict[str, Any] | None = None) -> str:
    profile_snippet = f" Profile: {user_profile!r}" if user_profile else ""
    return f"User goal: {user_goal}.{profile_snippet}"

