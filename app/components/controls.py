import streamlit as st

def display_controls(button_container: st.container) -> tuple:
    """
    Display the control buttons on the UI.

    Args:
        button_container (streamlit.container): Streamlit container to display the buttons.

    Returns:
        tuple: Start and Stop buttons
    """
    with button_container:
        cols = st.columns(2)
        with cols[0]:
            start_button = st.button("Start Listening", key="start-listening", help="Start real-time transcription and assistant responses")
        with cols[1]:
            stop_button = st.button("Stop Listening", key="stop-listening", help="Stop transcription and assistant responses")
    return start_button, stop_button


