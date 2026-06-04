import asyncio
import hashlib
import time
from typing import Any

from logging import getLogger

logger = getLogger()


class ChannelMonitorState:

    def __init__(self):
        self.agent_running: bool = False  # Is agent currently processing
        self.typing_active: bool = False  # Is typing indicator currently shown
        self.typing_task: asyncio.Task[None] | None = None  # Background typing indicator task
        self.continue_monitoring: bool = False  # Does agent want to continue monitoring
        self.last_message_id_seen: str | None = None  # Checkpoint for fetch_new_messages
        self.message_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()  # Messages for wait_for_messages
        self.queue_updated_event: asyncio.Event = asyncio.Event()  # Signals new messages
        self.messages_processed: int = 0  # Total messages processed in this conversation session
        self.recent_messages: dict[str, float] = {}  # Message content hash -> timestamp for deduplication
        self.conversation_summary: str | None = None  # Summary for context continuity across restarts
        self.last_context_message_id: str | None = None  # Last message ID included in agent's context (for restart catch-up)
        self.limit_reached_this_session: bool = False  # Prevents infinite loop when message limit is reached


    def _hash_message(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
        
    def _cleanup_old_messages(self) -> None:
        current_time = time.time()
        
        # 60 sec expiry
        expired_hashes = [
                msg_hash for msg_hash, timestamp in self.recent_messages.items()
                if current_time - timestamp > 60
        ]

        for msg_hash in expired_hashes :
            del self.recent_messages[msg_hash]
        if expired_hashes:
            logger.debug(f"Cleaned up {len(expired_hashes)} expired message hashes")

    def is_duplicate_message(self, content: str) -> bool:
        self._cleanup_old_messages()
        msg_hash = self._hash_message(content)
        return msg_hash in self.recent_messages

    def add_recent_message(self, content: str) -> None:

        self._cleanup_old_messages()
        msg_hash = self._hash_message(content)
        self.recent_messages[msg_hash] = time.time()
        logger.debug(f"Tracked message hash {msg_hash[:8]}... (total tracked: {len(self.recent_messages)})")
