

import os
from typing import Any
import dspy

from apps.bot.agents.base import BaseAgent
from apps.bot.agents.response.models import ResponseAgentOutput
from apps.bot.agents.response.signatures import ResponseSignature

from apps.bot.agents.response.tools import create_response_tools
from apps.bot.services.research.brave import BraveSearch
from apps.bot.services.research.jina import JinaReader
from apps.bot.services.research.service import research


RESPONSE_MODEL = "openai:gpt-5-mini"

DEFAULT_PERSONALITY = """
You are a Discord bot responding to users.

Be concise and helpful.
"""

PERSONALITY = os.getenv(
    "CUSTOM_PERSONALITY",
    DEFAULT_PERSONALITY
)

class ResponseAgent(BaseAgent):

    async def respond(
        self,
        relevant_messages: str,
        intent: str,
        context_summary: str,
        me: dict[str, Any],
    ) -> ResponseAgentOutput:

        tools = create_response_tools()

        react = dspy.ReAct(
            ResponseSignature,
            tools = tools
        )

        result = await react.acall(
            personality = PERSONALITY,
            relevant_messages = relevant_messages,
            intent = intent,
            context_summary = context_summary,
            me = me,
        )

        tokens_used = self.estimate_tokens(result.response)

        return ResponseAgentOutput.from_agent_result(
            result = result,
            tokens_used = tokens_used
        )

_response_agent: ResponseAgent | None = None

def get_response_agent() -> ResponseAgent:
    """Get or create the global response agent.

    Returns:
        The global ResponseAgent instance
    """
    global _response_agent
    if _response_agent is None:
        _response_agent = ResponseAgent()
    return _response_agent
