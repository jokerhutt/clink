from typing import Any
import dspy

class ResponseSignature(dspy.Signature):

    """
    Respond to the user.

    Use the supplied personality instructions.

    You already possess extensive general knowledge

    Use research_tool only when:
    - the question depends on current or recent information
    - the answer may have changed over time
    - the user explicitly asks you to research, verify, check, cite, or find sources
    - you are genuinely uncertain of the answer

    Do not use research_tool simply because a question is factual.

    For most questions, answer directly without using tools.

    If the user provides a URL, use url_tool.
    If the answer exists in the conversation context, do not research it.

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
