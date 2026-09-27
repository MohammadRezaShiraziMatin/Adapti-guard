from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from adapti_guard.evaluation.target_model import load_model_config

@dataclass(frozen=True)
class ModelExecutionMetadata:
    role: str
    config_key: str
    model_id: str
    provider: str
    temperature: float | None
    seed: int | None
    timestamp_utc: str

def metadata_from_config(config_key: str, *, role: str, config_path: str | Path = "configs/models.yaml", seed: int | None = None) -> ModelExecutionMetadata:
    spec = load_model_config(config_path)["models"][config_key]
    return ModelExecutionMetadata(role, config_key, str(spec.get("model", "")), str(spec.get("provider", "")),
        spec.get("temperature"), seed, datetime.now(timezone.utc).isoformat())
