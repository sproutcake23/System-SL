import json
from typing import Literal

from openai import OpenAI

from system_sl.chatbot.config import ChatConfig, load_config
from system_sl.chatbot.system_prompts import FRIEND_PROMPT, SYSTEM_MENTOR_PROMPT
from system_sl.chatbot.tools import TOOL_SCHEMAS, call_tool


Mode = Literal["system", "friend"]


def _build_client(config: ChatConfig) -> OpenAI:
    kwargs: dict = {"api_key": config.api_key}
    if config.base_url:
        kwargs["base_url"] = config.base_url
    return OpenAI(**kwargs)


class ChatSession:
    MAX_TOOL_ROUNDS = 6

    def __init__(self, mode: Mode, config: ChatConfig | None = None):
        self.mode: Mode = mode
        self.config = config or load_config()
        self.client = _build_client(self.config)
        self.history: list[dict] = [
            {"role": "system", "content": self._system_prompt()}
        ]

    def _system_prompt(self) -> str:
        return SYSTEM_MENTOR_PROMPT if self.mode == "system" else FRIEND_PROMPT

    def _model(self) -> str:
        return (
            self.config.system_model
            if self.mode == "system"
            else self.config.friend_model
        )

    def _tools(self) -> list[dict] | None:
        return TOOL_SCHEMAS if self.mode == "system" else None

    def run_turn(self, user_msg: str) -> str:
        
        

        
        return "[The System stalled — too many tool rounds without a final reply.]"
