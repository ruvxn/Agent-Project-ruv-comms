import streamlit as st
from backend.model.states.StateManager import StateManager
from frontend.home_ui import render_main_section, render_sidebar


def start():
    if "state" not in st.session_state:
        st.session_state.state = StateManager.get_state()

    if "message_placeholder" not in st.session_state:
        st.session_state.message_placeholder = st.empty()

    state = st.session_state.state

    render_sidebar(state)
    new_state = render_main_section(state)

    st.session_state.state = new_state


start()
