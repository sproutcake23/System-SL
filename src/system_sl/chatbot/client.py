import json
from typing import Literal, List, Union

from system_sl.chatbot.system_adi import get_system_agent, get_adi_agent

from langsmith import uuid7


Mode = Literal["system", "friend"]

class ChatSession:
    """Manages an active multi-turn conversation session with a specific LangChain agent.
    
    Attributes:
        mode (Mode): The operating persona ("system" or "friend").
        config (dict): The runtime configuration dictionary containing the `thread_id` 
            for state tracking.
        agent (Runnable): The selected pre-compiled LangGraph agent graph.
    """

    def __init__(self, mode: Mode, thread_id: str | None = None, config: dict | None = None):
        """Initializes a new or existing ChatSession.

        Args:
            mode (Mode): The agent persona to use. Must be either "system" or "friend".
            thread_id (str | None, optional): An existing unique identifier to resume a past conversation. If both thread_id and config are None, a new UUIDv7 is generated. Defaults to None.
            config (dict | None, optional): A complete pre-built LangChain/LangGraph 
                configuration dictionary. Overrides thread_id if provided. Defaults to None.
        """
        self.mode: Mode = mode
        
        if config:
            self.config = config
        else:
            chosen_id = thread_id or str(uuid7())
            self.config = { "configurable": { "thread_id": chosen_id } }
        
        # Select the pre-compiled agent. The factory builds the LLM/agent on
        # first use (lazy init) — by the time a ChatSession is created the API
        # key has already been secured in main().
        self.agent = get_system_agent() if mode == "system" else get_adi_agent()

    def wrap_message(self, user_msg: Union[str, List[str]]) -> List[dict]:

        """Formats a raw string or list of strings into the standard message format.

        Args:
            user_msg (Union[str, List[str]]): A single text message string or a list 
                of text message strings sent by the user.

        Returns:
            List[dict]: A list of formatted message dictionaries containing the 'role' 
                and 'content' keys ready for LangGraph input.
        """

        if isinstance(user_msg, str):
            return [{"role": "user", "content": user_msg}]
        else:
            return [{"role": "user", "content": msg} for msg in user_msg]  

    def run_turn(self, user_msg: Union[str, List[str]]) -> str:
            """Executes a single conversational turn with the agent.

            Args:
                user_msg (Union[str, List[str]]): The input text message(s) from the user.

            Returns:
                str: The extracted plain text content of the agent's reply.
            """
            formatted_messages = self.wrap_message(user_msg)

            response = self.agent.invoke(
                {"messages": formatted_messages},  
                config=self.config
            )

            if response is not None and "messages" in response:
                last_message = response["messages"][-1]
                
                # Extract content property from the base message class instance
                if hasattr(last_message, 'content'):
                    content = last_message.content
                    
                    # CASE 1: Content is a rich list: [{'type': 'text', 'text': '...'}]
                    if isinstance(content, list):
                        text_parts = []
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                text_parts.append(block.get("text", ""))
                        return "".join(text_parts) # Merges all text blocks into one clean string
                    
                    # CASE 2: Content is already a standard direct string
                    if isinstance(content, str):
                        return content
                
                # CASE 3: Fallback check if the message structure parsed as a raw dictionary primitive
                elif isinstance(last_message, dict) and 'content' in last_message:
                    content = last_message['content']
                    if isinstance(content, list) and len(content) > 0:
                        return str(content[0].get('text', ''))
                    return str(content)

            return "[The System failed to reply]"

if __name__ == "__main__":
    session = ChatSession("system")
    print(session.run_turn("Hello"))
