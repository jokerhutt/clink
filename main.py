import os

import hikari
import lightbulb

from apps.shared.httpx_client import close_http_client, init_http_client


def create_bot_app() -> lightbulb.BotApp:
    bot = lightbulb.BotApp(
        token=os.environ["DISCORD_BOT_TOKEN"],
        intents=(
            hikari.Intents.GUILDS
            | hikari.Intents.GUILD_MESSAGES
            | hikari.Intents.MESSAGE_CONTENT
        ),
    )

    async def on_starting(_: hikari.StartingEvent) -> None:
        init_http_client()

    async def on_stopping(_: hikari.StoppingEvent) -> None:
        await close_http_client()

    bot.subscribe(hikari.StartingEvent, on_starting)
    bot.subscribe(hikari.StoppingEvent, on_stopping)

    return bot


def main() -> None:
    bot = create_bot_app()
    bot.run(check_for_updates=False)


if __name__ == "__main__":
    main()
