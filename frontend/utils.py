from __future__ import annotations
import streamlit as st


def render_log(logs, log_placeholder):
    if hasattr(log_placeholder, "container"):
        with log_placeholder.container():
            for log in logs:
                st.write(log)
                st.write("**********")


def render_message(messages, message_placeholder):
    if hasattr(message_placeholder, "container"):
        with message_placeholder.container():
            for message in messages:
                st.write(message.content)
