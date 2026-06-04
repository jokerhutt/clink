import dspy

class ClassificationSignature(dspy.Signature):

    # Inputs
    conversation_timeline: str = dspy.InputField(
        description="Chronological conversation timeline with message IDs, timestamps, authors, and content"
    )
    trigger_message_id: str = dspy.InputField(
        description="The message ID that triggered this mention (the one containing the @mention)"
    )
    bot_id: str = dspy.InputField(
        description="The bot's user ID for identifying self-references"
    )

    # Outputs
    should_respond: bool = dspy.OutputField(
        description="True if the message is directed AT the bot and requires a response, False if it's ABOUT the bot or doesn't need response"
    )
    intent: str = dspy.OutputField(
        description="1-2 sentence description of what the user is asking or wanting (empty if should_respond is False)"
    )
    relevant_message_ids: list[str] = dspy.OutputField(
        description="Comma-separated list of message IDs that are relevant to this request (from the timeline's [ID: ...] prefixes)"
    )
    context_summary: str = dspy.OutputField(
        description="2-3 sentence summary of the relevant conversation context"
    )
