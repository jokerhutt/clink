
import hikari
import lightbulb
import uuid
from logging import getLogger

logger = getLogger()

plugin = lightbulb.Plugin("mention")

from apps.bot.utils.stop_detection import (is_channel_on_cooldown, is_stop_request)

async def handle_mention(event: hikari.MessageCreateEvent) -> None:

    request_id = str(uuid.uuid4())[:8]

    if (is_channel_on_cooldown(event.channel_id)) :
        logger.info(f"[{request_id}] Channel {event.channel_id} is on cooldown - ignoring")
        return

    if not event.message.user_mentions_ids :
        return

    bot_user = plugin.bot.get_me()

    if not bot_user:
        return

    user_question = event.content

    if not user_question:
        return

    for user_id in event.message.user_mentions_ids:
        if user_id == bot_user.id:
            user_question = user_question.replace(f"<@{user_id}>", "").replace(f"@!{user_id}>", "")
    user_question = user_question.strip()

    if is_stop_request(event.content or "") :
        # TODO IMPLEMENT
        return

    # TODO IMPLEMENT RATE LIMITER CHECK

    




    
