
import os
from pprint import pprint
from typing import Any, Awaitable, Callable
import dspy

from apps.bot.agents.base import BaseAgent
from apps.bot.agents.response.models import ResponseAgentOutput
from apps.bot.agents.response.signatures import ResponseSignature

from apps.bot.agents.response.tools import create_response_tools
from apps.bot.services.research.status_reporter import ResearchEventHandler, ResearchStatusReporter
from apps.llm_config import get_llm_model
from apps.shared.config import get_settings

DEFAULT_PERSONALITY = """
You are a Discord bot responding to users.

Be concise and helpful.
"""

RESPONSE_LM = get_llm_model()
PERSONALITY = get_settings().bot_personality or os.getenv(
    "CUSTOM_PERSONALITY",
    DEFAULT_PERSONALITY,
)

class ResponseAgent(BaseAgent):

    async def respond(
        self,
        relevant_messages: str,
        intent: str,
        context_summary: str,
        me: dict[str, Any],
        research_handler: ResearchEventHandler
    ) -> ResponseAgentOutput:

        tools = create_response_tools(
            research_handler = research_handler
        )

        react = dspy.ReAct(
            ResponseSignature,
            tools = tools
        )

        with dspy.context(lm=RESPONSE_LM):
            result = await react.acall(
                personality = PERSONALITY,
                relevant_messages = relevant_messages,
                intent = intent,
                context_summary = context_summary,
                me = me,
            )

        pprint(RESPONSE_LM.history[-1])


        print("DSPY RESULT:")
        print(result)
        print(vars(result))

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
