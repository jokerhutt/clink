
from collections.abc import Sequence
from datetime import datetime
import hikari
import lightbulb
import uuid
from logging import getLogger

from apps.bot.agents.classification.agent import get_classification_agent
from apps.bot.agents.response.agent import get_response_agent
from apps.bot.utils import messages
from apps.bot.utils.conversation_timeline import ConversationTimelineBuilder
from apps.bot.utils.messages import build_me_info

logger = getLogger()

plugin = lightbulb.Plugin("mention")

@plugin.listener(hikari.GuildMessageCreateEvent)
async def on_message_create(event: hikari.GuildMessageCreateEvent) -> None:

    # Ignore bot messages
    if event.message.author.is_bot:
        return

    # Ignore messages in DMs
    if not event.guild_id:
        return

    # Get bot user for mention checking
    bot_user = plugin.bot.get_me()
    if not bot_user:
        return

    if not event.message.user_mentions_ids :
        return

    # Check if bot is mentioned
    is_mentioned = bot_user.id in event.message.user_mentions_ids

    if is_mentioned:
        # Handle direct @mention with multi-agent pipeline
        await handle_mention(event)


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

async def handle_mention(event: hikari.GuildMessageCreateEvent) -> None:

    # Logging crap
    request_id = str(uuid.uuid4())[:8]

    guild_id = event.guild_id
    channel_id = event.channel_id
    trigger_message_id = event.message_id

    # Get bot id
    bot = plugin.bot
    if not bot:
        return
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
        timeline_builder = ConversationTimelineBuilder(bot, guild_id = guild_id)
        conversation_timeline = await timeline_builder.build(channel_id = channel_id, trigger_message_id= trigger_message_id, limit = 20)
        logger.info("TIMELINE:\n%s", conversation_timeline)

        classification_agent = get_classification_agent()

        classification = await classification_agent.classify(
            conversation_timeline=conversation_timeline,
            trigger_message_id = str(trigger_message_id),
            bot_id = str(bot_id)
        )

        total_tokens += classification.tokens_used

        logger.info(
            f"[{request_id}] Classification result: should_respond={classification.should_respond}, "
            f"intent='{classification.intent[:80]}...', "
        )

        if not classification.should_respond:
            logger.info(
                f"[{request_id}] Classification decided NOT to respond - exiting pipeline"
            )
            return

        response_agent = get_response_agent()

        # keep only relevant messages
        relevant_messages = timeline_builder.filter_relevant_messages(
            conversation_timeline, 
            classification.relevant_message_ids + [str(event.message_id)]
        )

        me_info = build_me_info(bot_user)

        result = await response_agent.respond(
            relevant_messages=relevant_messages,
            intent = classification.intent,
            context_summary = classification.context_summary,
            me = me_info
        )

        await bot.rest.create_message(
            channel = channel_id,
            content = result.response
        )

    except Exception as e:
        logger.exception(
            f"[{request_id}] Error while processing mention: {e}"
        )

        try:
            await bot.rest.create_message(
                channel=channel_id,
                content="Sorry, something went wrong while processing your request."
            )

        except Exception:
            logger.exception(
                f"[{request_id}] Failed to send error message"
            )


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)

def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin) 




    
