from dataclasses import dataclass

@dataclass
class ResponseAgentOutput:
    response: str
    tokens_used: int
    used_research: bool = False

    @classmethod
    def from_agent_result(cls, result, tokens_used: int) -> "ResponseAgentOutput":
        return cls(
            response = result.response,
            tokens_used = tokens_used
        )
