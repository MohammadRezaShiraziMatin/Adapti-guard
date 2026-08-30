from garak.generators import Generator
from garak.attempt import Message

from src.adapti_guard.core.pipeline import DefensePipeline


class AdaptiGuard(Generator):
    """ADAPTI-GUARD adaptive prompt injection defense."""

    name = "adapti_guard"
    generator_family_name = "adapti_guard"

    def __init__(self, name="adapti_guard", config_root=None, **kwargs):
        super().__init__(name=name, config_root=config_root, **kwargs)
        self.pipeline = DefensePipeline()

    def _call_model(self, prompt, generations_this_call=1):
        text = prompt.turns[-1].content.text

        result = self.pipeline.run(
            text=text,
            contextual_risk=0.0,
            tool_sensitive=False,
        )

        return [Message(text=result.response)]
