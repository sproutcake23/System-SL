import json
import os
from dataclasses import dataclass

from system_sl.core.my_tasks import get_tasks_file_path


CONFIG_FILENAME = "llm_config.json"

# Defaults target a local Ollama instance — no key required, no network call to
# a third party, fully offline once a model is pulled. Users who prefer
# OpenAI / OpenRouter / vLLM / LM Studio / etc. can override any field in
# ~/.config/system-sl/llm_config.json.
DEFAULT_BASE_URL = "http://localhost:11434/v1"
DEFAULT_API_KEY = "ollama"  # Ollama ignores it; the OpenAI SDK requires non-empty.
DEFAULT_SYSTEM_MODEL = "llama3.1"
DEFAULT_FRIEND_MODEL = "llama3.2:1b"


class ChatConfigError(RuntimeError):
    pass


@dataclass
class ChatConfig:
    api_key: str
    base_url: str | None
    system_model: str
    friend_model: str


def load_config() -> ChatConfig:
    path = get_tasks_file_path(CONFIG_FILENAME)
    data: dict = {}

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read().strip()
            if text:
                data = json.loads(text)
        except OSError as e:
            raise ChatConfigError(f"Failed to read {path}: {e}") from e
        except json.JSONDecodeError as e:
            raise ChatConfigError(f"{path} is not valid JSON: {e}") from e

    api_key = (
        data.get("api_key")
        or os.environ.get("LLM_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or DEFAULT_API_KEY
    )
    base_url = (
        data.get("base_url")
        or os.environ.get("LLM_BASE_URL")
        or DEFAULT_BASE_URL
    )

    return ChatConfig(
        api_key=api_key,
        base_url=base_url or None,
        system_model=data.get("system_model") or DEFAULT_SYSTEM_MODEL,
        friend_model=data.get("friend_model") or DEFAULT_FRIEND_MODEL,
    )
