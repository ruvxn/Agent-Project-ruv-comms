import time
from langchain_core.messages import HumanMessage, AIMessage
from src.backend.agent.Agent import Agent
from src.backend.tools.webscrape import WebScrape
from src.backend.tools.websearch import WebSearch
from src.backend.tools.memorytool import MemoryTool
from src.backend.tools.date_time import DateTime
import streamlit as st
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from src.frontend.main import main
import random

def load_css():
    with open("src/frontend/styles/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def load_message(messages, state):
    for message in messages["messages"]:
        if isinstance(message, HumanMessage):
            if message.content:
                state.append({"role": "user", "content": message.content})
        elif isinstance(message, AIMessage):
            if message.content:
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
        st.session_state.config = {"configurable": {"thread_id": "3"}}
       #"""thread id is used for concurrency and state management for the agent however there is no way to save this on the client side yet so conversations will be lost"""
        websearch = WebSearch()
        webscrape = WebScrape()
        datetime = DateTime()
       #memory = MemoryTool() #must have qdrant running to use this otherwise it will break the code
        tools = [websearch, webscrape, datetime]
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
            print("graph built")
            input = {"messages": [HumanMessage(content=user_input)]}

            try:
                 with st.spinner("Agent is thinking..."):
                     print("Agent is thinking...")
                     final_state = graph.invoke(input=input, config=st.session_state.config)
                     load_message(final_state, st.session_state.messages)
                     msg = final_state["messages"][-1].content

                     with st.chat_message("agent"):
                            st.markdown(
                                f'<div class="agent-message-container"><div class="agent-message">{msg}</div></div>',
                                unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred: here {e}")
        else:
            st.warning("Please enter a query.")

if __name__ == "__main__":
    app()
    #main()
