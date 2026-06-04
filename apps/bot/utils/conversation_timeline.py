
from datetime import UTC, datetime
import hikari


class ConversationTimelineBuilder:
    def __init__(self, bot: hikari.GatewayBot, guild_id: hikari.Snowflake):
        self.bot = bot
        self.guild_id = guild_id

    # fuck it
    def _format_relative_time(self, created_at: datetime) -> str:
        seconds = int((datetime.now(UTC) - created_at).total_seconds())
        if seconds < 60:
            return f"{seconds}s ago"
        if seconds < 3600:
            return f"{seconds // 60}m ago"
        if seconds < 86400:
            return f"{seconds // 3600}h ago"
        return f"{seconds // 86400}d ago"

    # 5 minutes (300 sec) is recent message
    def _is_recent_message(self, created_at: datetime) -> bool :
        seconds = int((datetime.now(UTC) - created_at).total_seconds())
        return seconds < 300

    def _format_message(self, message: hikari.Message) -> :
        author = message.author.display_name or message.author.username or "unknown user"
        content = message.content or ""
        created_at_relative = self._format_relative_time(message.created_at)
        formatted = f"[id: {message.id}] [{created_at_relative}]  {author}: {content}"
        return formatted

    async def build(self, channel_id: hikari.Snowflake, trigger_message_id: hikari.Snowflake | None = None, limit: int = 10) -> str :

        # Get Channel
        channel = await self.bot.rest.fetch_channel(channel_id)
        if hasattr(channel, "name"):
            channel_name = channel.name
        else :
            channel_name = "unknown"

        # unique {user_id: display_name }
        conversation_participants : dict[hikari.Snowflake, str] = {}

        # less than 5 minutes ago
        recent_message_count = 0

        # Get Messages
        formatted_messages : list[str] = []

        # Reverse messages to do oldest at top
        messages = [
            message
            async for message in self.bot.rest.fetch_messages(channel_id).limit(limit)
        ]

        messages.reverse()

        # loopedy loop
        for message in messages:
            formatted_messages.append(self._format_message(message))
            conversation_participants[message.author.id] = message.author.display_name or message.author.username or "unkown user"
            if (self._is_recent_message(message.created_at)) :
                recent_message_count += 1

        participants_list = ", ".join(conversation_participants.values())
        message_count = len(formatted_messages)
        messages_text = "\n".join(formatted_messages)

        built_message = f"""
        === Conversation Summary ===
        Pariticipants: {participants_list}
        Messages: {message_count}
        Recent activity: {recent_message_count} in last 5 minutes
        ============================

        === Conversation in #{channel_name}

        {messages_text}

        === End of conversation ===
        """

        return built_message







        





