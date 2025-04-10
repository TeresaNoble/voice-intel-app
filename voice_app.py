import openai
import streamlit as st
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import io
import json

# ---------------------- TONE GUIDES ----------------------

TONE_GUIDES = {
    "generation": {
        "Gen Z": "Use fast, emoji-rich, punchy language.",
        "Millennials": "Be purpose-driven, friendly, modern.",
        "Gen X": "Be efficient, practical, slightly formal.",
        "Boomers": "Use structured, clear, and respectful language."
    },
    "tech_savviness": {
        "low": "Avoid jargon. Use plain language with step-by-step phrasing.",
        "medium": "Use basic tech terms with light explanation.",
        "high": "Skip explanations. Use confident, technical terms."
    },
    "culture": {
        "individualist": "Speak to personal benefit and ownership.",
        "collectivist": "Emphasize teamwork and shared goals."
    },
    "tone_pref": {
        "fun": "Use humor, energy, and a playful twist.",
        "formal": "Stick to structured, polished phrasing.",
        "supportive": "Be warm, helpful, and gently encouraging.",
        "direct": "Be confident and get to the point."
    }
}

# ---------------------- FUNCTIONS ----------------------

def blend_tone_traits(profile):
    tone_parts = []
    for trait, rules in TONE_GUIDES.items():
        values = profile.get(trait, [])
        if isinstance(values, str):
            values = [values]
        for value in values:
            tone = rules.get(value)
            if tone:
                tone_parts.append(tone)
    return " ".join(tone_parts)

def generate_word_file(profile_data, ai_output):
    doc = Document()
    title = doc.add_heading("GENERATED CONTENT 📄", level=0)
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    def add_section(label, content):
        para_label = doc.add_paragraph()
        run = para_label.add_run(label)
        run.bold = True
        run.font.size = Pt(12)
        doc.add_paragraph(str(content))

    for k, v in profile_data.items():
        add_section(k.replace("_", " ").title() + ":", v)

    add_section("AI Output:", ai_output)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def extract_profile(user_message):
    prompt = f"""
The user said: "{user_message}"

Based on this, infer and update the following profile traits:
generation, tech_savviness, culture, tone_pref, team_type, project_goal

Use only these labels:
generation: ["Gen Z", "Millennials", "Gen X", "Boomers"]
tech_savviness: ["low", "medium", "high"]
culture: ["individualist", "collectivist"]
tone_pref: ["fun", "formal", "supportive", "direct"]

Return only JSON.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You extract profile traits based on user messages."},
            {"role": "user", "content": prompt}
        ]
    )
    try:
        traits = json.loads(response.choices[0].message.content)
        for k, v in traits.items():
            st.session_state.profile[k] = v
    except Exception:
        st.warning("Couldn't parse profile info.")

# ---------------------- STREAMLIT APP ----------------------

openai.api_key = st.secrets["OPENAI_API_KEY"]
st.set_page_config(page_title="Voice Content Assistant")
st.title("🧠 Voice-Driven Content Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "profile" not in st.session_state:
    st.session_state.profile = {
        "generation": ["Gen X"],
        "tech_savviness": ["medium"],
        "culture": ["collectivist"],
        "tone_pref": ["fun", "supportive"]
    }

user_input = st.text_input("🗣️ What’s your team working on?")

if st.button("Let’s Go") and user_input.strip():
    extract_profile(user_input)  # 🔍 Update user profile

    blended_tone = blend_tone_traits(st.session_state.profile)

    system_msg = f"""
You are a helpful, personality-rich assistant. Use the following tone style:

{blended_tone}

Speak like this for all responses. Adapt as new user info comes in.
"""

    st.session_state.messages.append({"role": "user", "content": user_input})

    messages = [{"role": "system", "content": system_msg}] + st.session_state.messages

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )

    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})

# ---------------------- UI DISPLAY ----------------------

if st.session_state.messages:
    st.markdown("### 💬 Conversation")
    for msg in st.session_state.messages:
        speaker = "👤 You" if msg["role"] == "user" else "🤖 Assistant"
        st.markdown(f"**{speaker}:** {msg['content']}")

    # ✂️ Copy
    st.code(st.session_state.messages[-1]["content"], language="markdown")

    # 📄 Export
    word_file = generate_word_file(st.session_state.profile, st.session_state.messages[-1]["content"])
    st.download_button(
        label="📄 Export as Word Doc",
        data=word_file,
        file_name="generated_content.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # 🧠 Tone used
    st.markdown("### 🧠 Tone Guide Used")
    st.info(blend_tone_traits(st.session_state.profile))
