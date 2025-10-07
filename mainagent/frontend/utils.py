from __future__ import annotations
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage


def render_log(logs, log_placeholder):
    if hasattr(log_placeholder, "container"):
        with log_placeholder.container():
            for log in reversed(logs):
                st.write(log)
                st.write("**********")


def render_message(messages, message_placeholder):
    if hasattr(message_placeholder, "container"):
        with message_placeholder.container():
            for message in messages:
                placeholder = st.empty()
                if isinstance(message, HumanMessage):
                    with placeholder.chat_message("user"):
                        st.markdown(message.content)
                elif isinstance(message, AIMessage):
                    with placeholder.chat_message("assistant"):
                        st.markdown(message.content)
