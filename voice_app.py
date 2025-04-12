import openai
import streamlit as st
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import io
import json

# ---------------------- VOICE RULEBOOK ----------------------
VOICE_RULEBOOK = {
    "generation": {
        "gen_z": "Use slang, emojis, and casual tone.",
        "millennials": "Use friendly, upbeat tone with mild humor.",
        "gen_x": "Be practical and professional, with some warmth.",
        "boomers": "Use clear, respectful, and structured language."
    },
    "tech_savviness": {
        "low": "Avoid jargon, use simple steps.",
        "medium": "Use basic tech terms, explain features lightly.",
        "high": "Use advanced terms and assume fluency."
    },
    "culture": {
        "individualist": "Speak to personal benefit and ownership.",
        "collectivist": "Focus on group success and shared goals."
    },
    "tone_pref": {
        "fun": "Use humor, metaphors, and light tone.",
        "formal": "Stick to polished, professional language.",
        "supportive": "Be warm and empathetic.",
        "direct": "Be brief, clear, and assertive."
    },
    "style_of_work": {
        "office_in_person": "Reference shared physical workspaces.",
        "office_remote": "Highlight asynchronous and virtual collaboration.",
        "office_mixed": "Mention hybrid workflows.",
        "customer_facing": "Prioritize short, clear, practical suggestions.",
        "floor_operations": "Use basic language and short instructions.",
        "field_worker": "Mention mobile-first formats and simplicity."
    },
    "personality": {
        "extrovert": "Favor social and team-based activities.",
        "introvert": "Encourage reflection and solo work.",
        "mixed": "Balance independent and group options."
    }
}

def build_full_tone_instruction(profile):
    tone_parts = []
    for trait_key, rules in VOICE_RULEBOOK.items():
        trait_value = profile.get(trait_key)
        if isinstance(trait_value, list):
            for value in trait_value:
                tone_rule = rules.get(value.lower().replace(" ", "_"))
                if tone_rule:
                    tone_parts.append(tone_rule)
        elif isinstance(trait_value, str):
            tone_rule = rules.get(trait_value.lower().replace(" ", "_"))
            if tone_rule:
                tone_parts.append(tone_rule)
    return "\n".join(tone_parts)

def generate_word_file(profile_data, ai_output):
    doc = Document()
    title = doc.add_heading("GENERATED CONTENT", level=0)
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

def is_profile_complete(profile):
    required_fields = ["generation", "tech_savviness", "culture", "tone_pref", "style_of_work", "personality"]
    return all(profile.get(field) for field in required_fields)

def extract_profile(user_message):
    prompt = f"""
    The user said: "{user_message}"

    Based on this, infer and update the following profile traits:
    generation, tech_savviness, culture, tone_pref, style_of_work, personality

    Use these labels:
    generation: ["Gen Z", "Millennials", "Gen X", "Boomers"]
    tech_savviness: ["low", "medium", "high"]
    culture: ["individualist", "collectivist"]
    tone_pref: ["fun", "formal", "supportive", "direct"]
    style_of_work: ["office_in_person", "office_remote", "office_mixed", "customer_facing", "floor_operations", "field_worker"]
    personality: ["extrovert", "introvert", "mixed"]

    Return only JSON.
    """
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Extract profile traits from the user message."},
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
st.set_page_config(page_title="Voice Assistant", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "profile" not in st.session_state:
    st.session_state.profile = {}

st.title("🗣️ Voice Assistant Playground")

with st.sidebar:
    st.header("🧠 Profile")
    st.write(st.session_state.profile)
    if st.button("Clear Profile & Chat"):
        st.session_state.profile = {}
        st.session_state.messages = []
        st.rerun()

user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    if not is_profile_complete(st.session_state.profile):
        extract_profile(user_input)
        missing_traits = [k for k in VOICE_RULEBOOK if not st.session_state.profile.get(k)]
        followups = {
            "generation": "Gen Z vibes? Millennials? A mysterious mix of both?",
            "tech_savviness": "How’s the tech game — smooth operators, figuring it out, or full-on ‘help me’ mode?",
            "culture": "More independent? Or team-first decision making?",
            "tone_pref": "Playful, clear and direct, buttoned-up, or gently supportive?",
            "style_of_work": "Office-based, remote crew, or in-the-field types?",
            "personality": "Big energy extroverts, thoughtful introverts, or both?"
        }
        reply = "Nice! Tell me a bit more so I can match your tone better:\n\n"
        reply += "\n".join([f"- {followups[trait]}" for trait in missing_traits])
        st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        tone_instructions = build_full_tone_instruction(st.session_state.profile)
        system_msg = f"You are a helpful, witty writing assistant.\nTone instructions based on the user:\n{tone_instructions}\nBe clever, casual, and helpful."
        st.session_state.messages.insert(0, {"role": "system", "content": system_msg})
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=st.session_state.messages
        )
        reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if st.session_state.messages:
    doc = generate_word_file(st.session_state.profile, st.session_state.messages[-1]["content"])
    st.download_button(
        label="📄 Download Word Doc",
        data=doc,
        file_name="content_output.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
