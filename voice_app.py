import streamlit as st
import openai
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import io
import json

# ---------------- SETUP ----------------
st.set_page_config(page_title="Voice Content Assistant", page_icon="🧠")
st.title("🧠 Voice Content Assistant")

try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except Exception as e:
    st.error("Missing or invalid OpenAI API key.")
    st.stop()

# ---------------- SESSION ----------------
if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "profile" not in st.session_state:
    st.session_state.profile = {}
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- RULEBOOK ----------------
VOICE_RULEBOOK = {
    "generation": {
        "gen_x": "Be practical and balanced.",
        "millennials": "Use feedback, social, and gamified ideas.",
        "gen_z": "Use fast, visual, playful responses."
    },
    "tech_savviness": {
        "low": "Avoid jargon. Use step-by-step help.",
        "medium": "Use familiar tech terms.",
        "high": "Use confident technical language."
    },
    "culture": {
        "individualist": "Emphasize personal achievement.",
        "collectivist": "Highlight teamwork and group wins."
    },
    "tone_pref": {
        "fun": "Add humor and lightness.",
        "supportive": "Be encouraging and kind.",
        "formal": "Be clear and polished.",
        "direct": "Get to the point confidently."
    },
    "style_of_work": {
        "office_remote": "Avoid in-person activities. Include online collaboration.",
        "office_mixed": "Include both in-person and virtual activities.",
        "field_worker": "Use tasks that work offline or on mobile."
    },
    "personality": {
        "introvert": "Use reflective or solo activities.",
        "extrovert": "Include presenting and collaboration.",
        "mixed": "Mix solo and group tasks."
    }
}

required_traits = list(VOICE_RULEBOOK.keys())