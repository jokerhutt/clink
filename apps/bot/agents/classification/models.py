from pydantic import BaseModel, Field

class ClassificationResult(BaseModel):

    """Result of pre-classifying an incoming mention."""
    should_respond: bool = False
    intent: str = ""
    relevant_message_ids: list[str] = Field(default_factory=list)
    context_summary: str = ""
    tokens_used: int = 0


