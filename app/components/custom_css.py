import streamlit as st


def apply_custom_css():
    """Inject custom CSS for the Streamlit app."""

    st.markdown("""
    <style>
        body {
            background: linear-gradient(to right, #f2f6f8, #e8edf3);
            color: #333;
            font-family: Arial, sans-serif;
        }
        .title {
            background-color: #0f4c81;
            color: white;
            padding: 15px;
            text-align: center;
            border-radius: 10px;
            font-size: 2em;
            margin-bottom: 20px;
        }

        /* Chat Container */
        .chat-container {
            max-height: 60vh;
            overflow-y: auto;
            padding: 10px;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }

        /* User Message Styling */
        .user {
            background-color: #cce5ff;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            align-self: flex-end;
            max-width: 80%;
        }

        /* Assistant Message Styling */
        .assistant {
            background-color: #d4edda;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            align-self: flex-start;
            max-width: 80%;
        }

        /* Error Message Styling */
        .error {
            color: red;
            font-weight: bold;
        }

        /* Sidebar Title */
        .sidebar-title {
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 10px;
        }

        /* Button Styling */
        .stButton > button {
            width: 100%;
            padding: 10px;
            border-radius: 5px;
            border: none;
            font-size: 1em;
            cursor: pointer;
        }

        /* Start Listening Button */
        #start-listening {
            background-color: #28a745;
            color: white;
        }

        /* Stop Listening Button */
        #stop-listening {
            background-color: #dc3545;
            color: white;
        }

    </style>
    """, unsafe_allow_html=True)

    # Additional CSS snippet to create a "fake" right sidebar container
    # We'll insert an empty <div> and position it on the right if debug mode is on.
    st.markdown("""
    <style>
    /* Our custom right-sidebar container */
    #debug-right-sidebar {
        position: fixed;
        top: 0;
        right: 0;
        width: 350px;            /* Adjust width as desired */
        height: 100%;
        padding: 15px;
        background-color: #f9f9f9;
        border-left: 1px solid #ccc;
        overflow-y: auto;
        z-index: 9999;
        display: none;           /* We'll show/hide via script depending on debug mode */
    }
    </style>
    """, unsafe_allow_html=True)
