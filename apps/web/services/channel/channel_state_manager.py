import asyncio
from apps.web.services.channel.channel_monitor_state import ChannelMonitorState

from logging import getLogger


logger = getLogger()

class ChannelStateManager:

    def __init__(self):
        self.states: dict[int, ChannelMonitorState] = {}
        logger.info("ChannelStateManager initialized for agentic monitoring")

    def get_state(self, channel_id: int) -> ChannelMonitorState:

        if channel_id not in self.states:
            self.states[channel_id] = ChannelMonitorState()
        return self.states[channel_id]

    def start_agent(self, channel_id: int) -> bool:
        state = self.get_state(channel_id)
        if state.agent_running:
            logger.debug(f"Channel {channel_id}: Agent already running, skipping")
            return False

        state.agent_running = True
        state.continue_monitoring = False
        logger.debug(f"Channel {channel_id}: Agent started")
        return True

    def finish_agent(self, channel_id: int) -> None:
        state = self.get_state(channel_id)
        state.agent_running = False
        logger.debug(f"Channel {channel_id}: Agent finished")

    def is_agent_running(self, channel_id: int) -> bool:
        state = self.get_state(channel_id)
        return state.agent_running

    def set_continue_monitoring(self, channel_id: int, continue_monitoring: bool) -> None:
        state = self.get_state(channel_id)
        state.continue_monitoring = continue_monitoring
        logger.debug(f"Channel {channel_id}: Continue monitoring set to {continue_monitoring}")


    def should_continue_monitoring(self, channel_id: int, active: bool) -> None:
        state = self.get_state(channel_id)
        state.typing_active = active
        logger.debug(f"Channel {channel_id}: Typing indicator {'started' if active else 'stopped'}")

    def set_typing_active(self, channel_id: int, active: bool) -> None:
        state = self.get_state(channel_id)
        state.typing_active = active
        logger.debug(f"Channel {channel_id}: Typing indicator {'started' if active else 'stopped'}")

    def is_typing_active(self, channel_id: int) -> bool:
        state = self.get_state(channel_id)
        return state.typing_active

    async def start_typing_task(
        self,
        channel_id: int,
        bot_rest_callback
    ) -> None:
        state = self.get_state(channel_id)

        if state.typing_task and not state.typing_task.done():
            state.typing_task.cancel()

        async def typing_loop():
            try:
                while state.typing_active:
                    await bot_rest_callback(channel_id)
                    await asyncio.sleep(9)
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Error in typing loop for channel {channel_id}: {e}")

        state.typing_task = asyncio.create_task(typing_loop())
        logger.debug(f"Channel {channel_id}: Started typing indicator task")


    def stop_typing_task(self, channel_id: int) -> None:
        state = self.get_state(channel_id)

        if state.typing_task and not state.typing_task.done():
            state.typing_task.cancel()
            logger.debug(f"Channel {channel_id}: Cancelled typing indicator task")

        state.typing_task = None


    def set_last_message_id(self, channel_id: int, message_id: str) -> None:
        state = self.get_state(channel_id)
        state.last_message_id_seen = message_id
        logger.debug(f"Channel {channel_id}: Updated last message checkpoint to {message_id}")


    def get_last_message_id(self, channel_id: int) -> str | None:
        state = self.get_state(channel_id)
        return state.last_message_id_seen


    async def queue_message(self, channel_id: int, message: dict[str, object]) -> None:
        state = self.get_state(channel_id)
        await state.message_queue.put(message)
        state.queue_updated_event.set()
        logger.debug(f"Channel {channel_id}: Queued message (queue size: {state.message_queue.qsize()})")


    def get_message_queue(self, channel_id: int) -> asyncio.Queue[dict[str, object]]:
        state = self.get_state(channel_id)
        return state.message_queue


    def get_queue_event(self, channel_id: int) -> asyncio.Event:
        state = self.get_state(channel_id)
        return state.queue_updated_event


    def clear_queue(self, channel_id: int) -> None:
        state = self.get_state(channel_id)

        while not state.message_queue.empty():
            try:
                state.message_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

        state.queue_updated_event.clear()
        logger.debug(f"Channel {channel_id}: Cleared message queue")


    def increment_messages_processed(self, channel_id: int, count: int = 1) -> int:
        state = self.get_state(channel_id)
        state.messages_processed += count
        logger.debug(f"Channel {channel_id}: Messages processed incremented to {state.messages_processed}")
        return state.messages_processed


    def get_messages_processed(self, channel_id: int) -> int:
        state = self.get_state(channel_id)
        return state.messages_processed


    def reset_messages_processed(self, channel_id: int) -> None:
        state = self.get_state(channel_id)
        state.messages_processed = 0
        logger.debug(f"Channel {channel_id}: Messages processed reset to 0")


    def set_conversation_summary(self, channel_id: int, summary: str | None) -> None:
        state = self.get_state(channel_id)
        state.conversation_summary = summary

        if summary:
            logger.debug(f"Channel {channel_id}: Conversation summary set ({len(summary)} chars)")
        else:
            logger.debug(f"Channel {channel_id}: Conversation summary cleared")


    def get_conversation_summary(self, channel_id: int) -> str | None:
        state = self.get_state(channel_id)
        return state.conversation_summary


    def set_last_context_message_id(self, channel_id: int, message_id: str | None) -> None:
        state = self.get_state(channel_id)
        state.last_context_message_id = message_id

        if message_id:
            logger.debug(f"Channel {channel_id}: Last context message ID set to {message_id}")
        else:
            logger.debug(f"Channel {channel_id}: Last context message ID cleared")


    def get_last_context_message_id(self, channel_id: int) -> str | None:
        state = self.get_state(channel_id)
        return state.last_context_message_id


    def cleanup_channel(self, channel_id: int) -> None:
        if channel_id in self.states:
            state = self.states[channel_id]

            self.clear_queue(channel_id)

            if state.typing_active:
                logger.debug(f"Channel {channel_id}: Cleaned up state with active typing indicator")

            del self.states[channel_id]
            logger.debug(f"Channel {channel_id}: Cleaned up channel state")

