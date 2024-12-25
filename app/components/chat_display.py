import streamlit as st

def display_chat_history(chat_history: list, container: st.container) -> None:
    """
    Display the chat history container on the UI.

    Args:
        chat_history (list): List of chat messages.
        container (streamlit.container): Streamlit container to display the chat history.
    """
    with container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in chat_history:
            role_class = "user" if message["role"] == "user" else "assistant"
            role_label = "🧑‍💻 You" if message["role"] == "user" else "🤖 Assistant"
            st.markdown(
                f'<div class="{role_class}"><b>{role_label}:</b> {message["content"]}</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
        print("Chat history displayed.")
