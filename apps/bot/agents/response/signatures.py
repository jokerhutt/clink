from typing import Any
import dspy

class ResponseSignature(dspy.Signature):

    """
    Respond to the user.

    Use the supplied personality instructions.

    Use research_tool when the answer requires web research, current information, or external sources.

    Do not use research_tool for information already present in the conversation context.
    """

    personality: str = dspy.InputField(
        description="System instructions describing the bot's personality, behavior, tone, and response style"
    )

    relevant_messages: str = dspy.InputField(
        description="Filtered conversation timeline containing only the relevant messages for this request"
    )
    intent: str = dspy.InputField(
        description="What the user is asking for or trying to accomplish"
    )
    context_summary: str = dspy.InputField(
        description="Brief summary of the conversation context"
    )

    me: dict[str, Any] = dspy.InputField(
        description="Bot info with bot_name and bot_id fields"
    )

    response: str = dspy.OutputField(
        description="Your response (tools handle actual sending - this is for logging)"
    )

