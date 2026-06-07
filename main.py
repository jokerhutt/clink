import logging

import hikari
import lightbulb

from apps.shared.config import get_settings
from apps.shared.httpx_client import close_http_client, init_http_client

logger = logging.getLogger(__name__)

def load_plugins(bot: lightbulb.BotApp) -> None:
    try :
        logger.info("loading mention plugin...")
        bot.load_extensions("apps.bot.plugins.mention")
        logger.info("✓ loaded mention plugin")
    except Exception as e:
        logger.error(f"failed to load plugins: {e}")
        import traceback

        logger.error(f"plugin loading traceback: {traceback.format_exc()}")
        logger.warning("bot will run without plugins")




def create_bot_app() -> lightbulb.BotApp:
    settings = get_settings()
    if not settings.discord_bot_token:
        raise RuntimeError("DISCORD_BOT_TOKEN is required")
    if settings.discord_application_id is None:
        raise RuntimeError("DISCORD_APPLICATION_ID is required")

    bot = lightbulb.BotApp(
        token=settings.discord_bot_token,
        intents=(
            hikari.Intents.GUILDS
            | hikari.Intents.GUILD_MESSAGES
            | hikari.Intents.MESSAGE_CONTENT
        ),
        logs="INFO",
    )

    load_plugins(bot)

    async def on_starting(_: hikari.StartingEvent) -> None:
        init_http_client()

    async def on_ready(event: hikari.ShardReadyEvent) -> None:
        if int(event.application_id) != settings.discord_application_id:
            raise RuntimeError(
                "DISCORD_APPLICATION_ID does not match the connected bot application"
            )
        logger.info(
            "Bot online as %s (%s)",
            event.my_user.username,
            event.my_user.id,
        )

    async def on_message(event: hikari.GuildMessageCreateEvent) -> None:
        if event.is_bot or event.author.is_bot:
            return
        logger.debug(
            "Message received in guild=%s channel=%s author=%s message=%s",
            event.guild_id,
            event.channel_id,
            event.author.id,
            event.message_id,
        )

    async def on_stopping(_: hikari.StoppingEvent) -> None:
        await close_http_client()

    bot.subscribe(hikari.StartingEvent, on_starting)
    bot.subscribe(hikari.ShardReadyEvent, on_ready)
    bot.subscribe(hikari.GuildMessageCreateEvent, on_message)
    bot.subscribe(hikari.StoppingEvent, on_stopping)

    return bot


def main() -> None:
    bot = create_bot_app()
    bot.run(check_for_updates=False)


if __name__ == "__main__":
    main()
