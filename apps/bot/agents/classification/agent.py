import dspy
from apps.llm_config import get_llm_model
from logging import getLogger
from apps.bot.agents.classification import models, signatures

logger = getLogger(__name__)
CLASSIFICATION_LM = get_llm_model("fast")

class ClassificationAgent() :
    def __init__(self):
        self._classifier = dspy.Predict(signatures.ClassificationSignature)

    def _estimate_token_usage(self, conversation_timeline: str) -> int:
        return len(conversation_timeline) // 4 + 100


    async def classify(self, conversation_timeline: str, trigger_message_id: str, bot_id: str) -> models.ClassificationResult:
        try: 

            # Classify with dspy
            with dspy.context(lm=CLASSIFICATION_LM):
                result = self._classifier(
                    conversation_timeline = conversation_timeline,
                    trigger_message_id = trigger_message_id,
                    bot_id = bot_id
                )

            # Validate that shit
            parsed = models.ClassificationResult.model_validate(result)

            # Estimate with tokens (about 4 tokens per word)
            estimated_tokens = self._estimate_token_usage(conversation_timeline)

            # Package it nicely
            res = models.ClassificationResult(
                should_respond=parsed.should_respond,
                intent=parsed.intent,
                relevant_message_ids=parsed.relevant_message_ids,
                context_summary=parsed.context_summary,
                tokens_used = estimated_tokens
            )

            # Return it
            return res

        except Exception as e:
            logger.exception("Classification failed")
            return models.ClassificationResult(
                should_respond=False,
                intent="",
                context_summary="",
                relevant_message_ids=[],
                tokens_used = 0
            )

_classification_agent: ClassificationAgent | None = None

def get_classification_agent() -> ClassificationAgent:
    global _classification_agent
    if _classification_agent is None:
        _classification_agent = ClassificationAgent()
    return _classification_agent
