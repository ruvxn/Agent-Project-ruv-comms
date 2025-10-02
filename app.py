from langchain_core.messages import HumanMessage, AIMessage

from src.backend.agent.Agent import Agent
from src.backend.tools.webscrape import WebScrape
from src.backend.tools.websearch import WebSearch
from src.backend.tools.memorytool import MemoryTool
import streamlit as st
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from src.frontend.main import main
import random

def load_css():
    with open("src/frontend/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def load_message(messages, state):
    for message in messages["messages"]:
        if isinstance(message, HumanMessage):
            state.append({"role": "user", "content": message.content})
        elif isinstance(message, AIMessage):
            state.append({"role": "agent", "content": message.content})
        else:
            continue
    return state

def app():
    load_css()
    st.set_page_config(layout="wide")
    st.title("Agent")
    if "config" not in st.session_state:
        id = random.randint(1000, 10000)
        st.session_state.config = {"configurable": {"thread_id": id}}
        websearch = WebSearch()
        webscrape = WebScrape()
        memory = MemoryTool()
        tools = [memory, websearch, webscrape]
        st.session_state.messages = []
        st.session_state.agent = Agent(tools=tools, name="WebAgent")
        with sqlite3.connect('src/backend/db/WebAgent.db', check_same_thread=False) as conn:
            memory = SqliteSaver(conn)
            checkpoint = memory.get_tuple(config = st.session_state.config)
        if checkpoint:
            value = checkpoint.checkpoint['channel_values']
            st.session_state.messages = load_message(value, st.session_state.messages)


    if st.session_state.messages:
        for msg in st.session_state.messages:
            with st.chat_message(msg.get("role")):
                if msg.get("role") == "agent":
                    st.markdown(
                        f'<div class="agent-message-container"><div class="agent-message">{msg["content"]}</div></div>',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        f'<div class="user-message-container"><div class="user-message">{msg["content"]}</div></div>',
                        unsafe_allow_html=True)
    if user_input := st.chat_input("Enter your query:"):
        if user_input:
            with st.chat_message(user_input):
                st.markdown(f'<div class="user-message-container"><div class="user-message">{user_input}</div></div>', unsafe_allow_html=True)
            graph = st.session_state.agent.graph_builder()

            input = {"messages": [HumanMessage(content=user_input)]}
            try:
                with st.spinner("Processing..."):
                    for event in graph.stream(
                        input,
                        config=st.session_state.config ,
                        stream_mode="updates"
                    ):
                        for node_name, value in event.items():
                            if "messages" in value and value is not None:
                                st.session_state.messages = load_message(value, st.session_state.messages)
                            if node_name == "__end__":
                                break
                for msg in st.session_state.messages:
                    with st.chat_message(msg.get("role")):
                        if msg.get("role") == "agent":
                            st.markdown(f'<div class="agent-message-container"><div class="agent-message">{msg["content"]}</div></div>', unsafe_allow_html=True)
                        else:
                            continue
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a query.")

if __name__ == "__main__":
    app()
    #main()