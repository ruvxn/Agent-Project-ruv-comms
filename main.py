import streamlit as st
from backend.model.states.GraphState import GraphState
from frontend.home_ui import render_main_section, render_sidebar


def start():
    if "state" not in st.session_state:
        st.session_state.state = GraphState()

    state = st.session_state.state

    if "message_placeholder" not in st.session_state:
        st.session_state.message_placeholder = st.empty()

    state = render_sidebar(state)
    render_main_section(state)


start()
