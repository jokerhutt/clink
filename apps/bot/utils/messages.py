from typing import Any
from hikari import OwnUser


def build_me_info(bot_user: OwnUser | None) -> dict[str, Any]:
    return {
        "bot_name": bot_user.display_name if bot_user else "Bot",
        "bot_id": str(bot_user.id) if bot_user else None
    }

