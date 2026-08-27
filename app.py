"""
frontend/app.py
----------------
Streamlit client for an AI-powered educational application. Collects
user text, and dispatches it to a backend REST service for either
summarization or automated quiz generation.

Run with:
    streamlit run frontend/app.py

Requires a `.env` file (same directory the app is launched from, or any
parent directory python-dotenv can discover) containing:
    BACKEND_URL=http://localhost:8000
"""

import os
from typing import Any, Dict, List, Optional

import requests
import streamlit as st
from dotenv import load_dotenv

# --------------------------------------------------------------------------
# CONSTANTS
# --------------------------------------------------------------------------
REQUEST_TIMEOUT_SECONDS = 30


# --------------------------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------------------------
def get_backend_url() -> Optional[str]:
    """
    Load environment variables from .env and return the configured
    backend URL, or None if it isn't set.
    """
    load_dotenv()
    backend_url = os.getenv("BACKEND_URL")
    if backend_url:
        return backend_url.rstrip("/")
    return None


# --------------------------------------------------------------------------
# SESSION STATE
#    Streamlit reruns this script top-to-bottom on every interaction, so
#    fetched results and per-question quiz progress must live in
#    st.session_state to survive each button click and radio selection.
# --------------------------------------------------------------------------
def initialize_session_state() -> None:
    """Create every session_state key the app relies on, exactly once."""
    defaults: Dict[str, Any] = {
        "input_text": "",
        "summary": None,
        "quiz_questions": None,
        # quiz_progress maps question id -> {"checked": bool, "is_correct": bool}
        "quiz_progress": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# --------------------------------------------------------------------------
# BACKEND CALLS
# --------------------------------------------------------------------------
def fetch_summary(backend_url: str, text: str) -> Optional[str]:
    """
    POST the given text to {backend_url}/summarize and return the summary
    string, or None if the request failed (an st.error is shown in that
    case, so the caller doesn't need to display anything further).
    """
    try:
        response = requests.post(
            f"{backend_url}/summarize",
            json={"text": text},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.exceptions.ConnectionError:
        st.error(
            "Could not connect to the backend. Confirm it is running and "
            "that BACKEND_URL in your .env file is correct."
        )
        return None
    except requests.exceptions.Timeout:
        st.error("The summarization request timed out. Please try again.")
        return None
    except requests.exceptions.RequestException as exc:
        st.error(f"An unexpected network error occurred: {exc}")
        return None

    if response.status_code != 200:
        st.error(
            f"Summarization failed (HTTP {response.status_code}): "
            f"{response.text}"
        )
        return None

    try:
        return response.json()["summary"]
    except (ValueError, KeyError):
        st.error("The backend returned an unexpected response format.")
        return None


def fetch_quiz(backend_url: str, text: str) -> Optional[List[Dict[str, Any]]]:
    """
    POST the given text to {backend_url}/quiz and return the list of
    question dicts, or None if the request failed.
    """
    try:
        response = requests.post(
            f"{backend_url}/quiz",
            json={"text": text},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.exceptions.ConnectionError:
        st.error(
            "Could not connect to the backend. Confirm it is running and "
            "that BACKEND_URL in your .env file is correct."
        )
        return None
    except requests.exceptions.Timeout:
        st.error("The quiz generation request timed out. Please try again.")
        return None
    except requests.exceptions.RequestException as exc:
        st.error(f"An unexpected network error occurred: {exc}")
        return None

    if response.status_code != 200:
        st.error(
            f"Quiz generation failed (HTTP {response.status_code}): "
            f"{response.text}"
        )
        return None

    try:
        return response.json()["questions"]
    except (ValueError, KeyError):
        st.error("The backend returned an unexpected response format.")
        return None


# --------------------------------------------------------------------------
# RENDERING HELPERS
# --------------------------------------------------------------------------
def render_summary_section() -> None:
    """Display the stored summary, if one has been fetched."""
    if st.session_state.summary:
        st.subheader("📝 Summary")
        with st.container(border=True):
            st.markdown(st.session_state.summary)


def render_quiz() -> None:
    """
    Render every stored quiz question as a radio group with its own
    "Check Answer" button. Each question's checked/correct state is kept
    in st.session_state.quiz_progress so feedback persists across the
    reruns triggered by other questions' buttons.
    """
    questions = st.session_state.quiz_questions
    if not questions:
        return

    st.subheader("🧠 Quiz")

    for question in questions:
        q_id = question["id"]
        options: List[str] = question["options"]
        correct_index: int = question["correct_index"]
        radio_key = f"quiz_radio_{q_id}"
        button_key = f"quiz_check_{q_id}"

        # Ensure this question has a progress entry before it's read below.
        st.session_state.quiz_progress.setdefault(
            q_id, {"checked": False, "is_correct": False}
        )

        with st.container(border=True):
            st.markdown(f"**Q{q_id}. {question['question']}**")

            # `key=radio_key` binds the widget directly to session_state,
            # so the selection survives reruns from any other widget.
            selected_option = st.radio(
                label="Choose an answer:",
                options=options,
                index=None,
                key=radio_key,
                label_visibility="collapsed",
            )

            if st.button("Check Answer", key=button_key):
                if selected_option is None:
                    st.warning("Please select an option before checking.")
                else:
                    selected_index = options.index(selected_option)
                    is_correct = selected_index == correct_index
                    st.session_state.quiz_progress[q_id] = {
                        "checked": True,
                        "is_correct": is_correct,
                    }

            # Show feedback for this question if it has been checked,
            # on this rerun or a previous one.
            progress = st.session_state.quiz_progress[q_id]
            if progress["checked"]:
                if progress["is_correct"]:
                    st.success("Correct! ✅")
                else:
                    st.error(f"Not quite. Correct answer: {options[correct_index]}")


# --------------------------------------------------------------------------
# MAIN ENTRY POINT
# --------------------------------------------------------------------------
def main() -> None:
    st.set_page_config(page_title="AI Study Assistant", page_icon="🎓", layout="wide")
    initialize_session_state()

    st.title("🎓 AI Study Assistant")
    st.caption("Paste text below, then summarize it or generate a quiz from it.")

    backend_url = get_backend_url()
    if not backend_url:
        st.error(
            "BACKEND_URL is not set. Create a `.env` file in your project "
            "root with a line like `BACKEND_URL=http://localhost:8000`, "
            "then restart the app."
        )
        st.stop()

    st.session_state.input_text = st.text_area(
        "Input text",
        value=st.session_state.input_text,
        height=220,
        placeholder="Paste an article, chapter, or notes here...",
    )

    col_summarize, col_quiz = st.columns(2)
    with col_summarize:
        summarize_clicked = st.button("📝 Summarize", use_container_width=True)
    with col_quiz:
        quiz_clicked = st.button("🧠 Generate Quiz", use_container_width=True)

    text = st.session_state.input_text.strip()

    if summarize_clicked:
        if not text:
            st.warning("Please enter some text before requesting a summary.")
        else:
            with st.spinner("Summarizing..."):
                result = fetch_summary(backend_url, text)
            if result is not None:
                st.session_state.summary = result

    if quiz_clicked:
        if not text:
            st.warning("Please enter some text before generating a quiz.")
        else:
            with st.spinner("Generating quiz..."):
                result = fetch_quiz(backend_url, text)
            if result is not None:
                st.session_state.quiz_questions = result
                # Reset progress so a freshly generated quiz starts unchecked.
                st.session_state.quiz_progress = {}

    render_summary_section()
    render_quiz()


if __name__ == "__main__":
    main()
