
from collections.abc import Sequence
from datetime import datetime
import hikari
import lightbulb
import uuid
from logging import getLogger

from apps.bot.agents.classification.agent import get_classification_agent

logger = getLogger()

plugin = lightbulb.Plugin("mention")

def is_bot_mention(message: hikari.Message, content: str | None, bot_id: hikari.Snowflake) -> bool:
    if not message.user_mentions_ids :
        return False
    if not content:
        return False
    return True
    

def remove_bot_mention(user_question: str | None, user_mentions_ids: Sequence[hikari.Snowflake], bot_id: hikari.Snowflake) -> str:
    if not user_question :
        return ""
    for user_id in user_mentions_ids :
        if user_id == bot_id:
            user_question = user_question.replace(f"<@{user_id}", "").replace(f"@!{user_id}>", "")
    return user_question.strip()

async def handle_mention(event: hikari.MessageCreateEvent) -> None:

    # Logging crap
    request_id = str(uuid.uuid4())[:8]

    # Get bot id
    bot_user = plugin.bot.get_me()
    if not bot_user:
        return
    bot_id = bot_user.id

    user_mentions_ids = event.message.user_mentions_ids
    user_question = event.content

    # Validate if mentioning the bot
    if not user_mentions_ids or not user_question or not bot_id:
        return

    # Remove the mention to the bot
    user_question = remove_bot_mention(user_question, user_mentions_ids, bot_id)

    # TODO IMPLEMENT RATE LIMITER CHECK

    start_time = datetime.now()
    total_tokens = 0

    try:
        logger.debug(f"[{request_id}] Building conversation context...")

        classification_agent = get_classification_agent()





    except Exception :


    




    
