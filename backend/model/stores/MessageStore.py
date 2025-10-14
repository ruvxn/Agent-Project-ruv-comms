from typing import Union
from langchain_core.messages import HumanMessage, AIMessage
from constants import SYSTEM_MESSAGE_LIST


class MessageStore(list):
    def __init__(self, message_placeholder=None):
        super().__init__()
        self.user_query_list: list[HumanMessage] = []
        self.ai_response_list: list[AIMessage] = []
        self.system_message_list = SYSTEM_MESSAGE_LIST
        self.message_history: list[Union[HumanMessage, AIMessage]] = []
        self.message_placeholder = message_placeholder

    def append(self, message: Union[HumanMessage, AIMessage]):
        super().append(message)
        self.message_history.append(message)

        if isinstance(message, HumanMessage):
            self.user_query_list.append(message)

        if isinstance(message, AIMessage):
            self.ai_response_list.append(message)

        if hasattr(self.message_placeholder, "container"):
            from frontend.utils import render_message
            render_message(self, self.message_placeholder)

    def extend(self, messages):
        for message in messages:
            if not self._message_exists(message):
                self.append(message)

    def _message_exists(self, message):
        return any(m.content == message.content and type(m) == type(message) for m in self)
