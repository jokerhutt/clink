
from logging import getLogger

logger = getLogger()

MAX_PENDING_MESSAGES = 50
MAX_MESSAGE_AGE_SECONDS = 600

class ChannelWatchState:
    def __init__(self, channel_id: int):
        self.channel_id = channel_id
        self.watchers: dict[str, Watcher]
