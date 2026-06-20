from system_sl.chatbot.system_prompts import FRIEND_PROMPT, SYSTEM_MENTOR_PROMPT
# NOTE: import the lazy factories, NOT instantiated agents. Importing
# `system_agent`/`adi_agent` here would build the LLM at package-import time
# (before the API key is secured) and crash on startup.
from system_sl.chatbot.system_adi import get_system_agent, get_adi_agent
from system_sl.chatbot.client import ChatSession
from system_sl.chatbot.config import ChatConfigError


__all__ = [
    "FRIEND_PROMPT",
    "SYSTEM_MENTOR_PROMPT",
    "get_system_agent",
    "get_adi_agent",
    "ChatSession",
    "ChatConfigError"
]