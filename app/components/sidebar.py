import streamlit as st


def display_sidebar_settings() -> str:
    """
    Display sidebar language selection & debug toggle. Return the chosen language option.

    Returns:
        str: The chosen language option.
    """
    st.sidebar.markdown('<div class="sidebar-title">⚙️ Settings</div>', unsafe_allow_html=True)

    # 1. Store language in session state so it persists
    #    on re-runs and doesn't get reset if you move away from the default.
    if "language_option" not in st.session_state:
        st.session_state.language_option = "Auto Detect"

    # 2. Make the radio button use the stored value (index trick).
    languages = ["Auto Detect", "English", "Arabic"]
    default_index = languages.index(st.session_state.language_option)
    language_option = st.sidebar.radio(
        "🌍 Choose language:",
        languages,
        index=default_index
    )

    # 3. Update the session state on each re-run
    st.session_state.language_option = language_option

    # 4) Debug mode toggle
    debug_mode = st.sidebar.checkbox("Debug Mode", value=st.session_state.debug_mode)
    st.session_state.debug_mode = debug_mode

    # 5) Clear chat button
    if st.sidebar.button("🗑️ Clear Chat / New Session"):
        st.session_state.clear_chat = True
        st.rerun()

    return st.session_state.language_option
