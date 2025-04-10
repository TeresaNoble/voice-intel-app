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

def is_profile_complete(profile):
    return all(profile.get(k) for k in required_traits)

followups = {
    "generation": "Gen Z vibes? Millennials? A mysterious mix of both?",
    "tech_savviness": "How’s the tech game — smooth operators, figuring it out, or full-on ‘help me’ mode?",
    "culture": (
        "How does your team usually work — more independent (folks own their lane), "
        "or more collaborative (lots of group alignment and shared decision-making)?"
    ),
    "tone_pref": "What’s your vibe — playful, clear and direct, buttoned-up, or gently supportive?",
    "style_of_work": "Office dwellers, remote warriors, or field folks who never sit still?",
    "personality": (
        "What’s the squad like — "
        "chatty and chaotic (extroverts), quiet and thoughtful (introverts), "
        "or a glorious mess of both?"
    )
}

def build_followup_reply(profile):
    missing = [k for k in required_traits if not profile.get(k)]
    if not missing:
        return None
    message = "Nice start! I can totally work with this. But before I get too clever:\n\n"
    message += "\n".join([f"- {followups[q]}" for q in missing])
    return message

def build_full_tone_instruction(profile):
    tone_parts = []
    for trait, rules in VOICE_RULEBOOK.items():
        value = profile.get(trait, "")
        rule = rules.get(value.lower().replace(" ", "_"))
        if rule:
            tone_parts.append(rule)
    return "\n".join(tone_parts)

def extract_profile(user_message):
    prompt = f"""
    The user said: "{user_message}"

    Guess their traits:
    generation, tech_savviness, culture, tone_pref, style_of_work, personality

    Use JSON only. Example:
    {{
        "generation": "Millennials",
        "tech_savviness": "high",
        ...
    }}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Extract profile traits."},
            {"role": "user", "content": prompt}
        ]
    )
    try:
        traits = json.loads(response.choices[0].message["content"])
        for k, v in traits.items():
            st.session_state.profile[k] = v
    except Exception as e:
        st.warning("Could not parse traits.")
        st.text(str(e))

def generate_word_file(profile_data, ai_output):
    doc = Document()
    doc.add_heading("GENERATED CONTENT 📄", 0).alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    def add_section(label, content):
        para = doc.add_paragraph()
        run = para.add_run(label)
        run.bold = True
        run.font.size = Pt(12)
        doc.add_paragraph(str(content))

    for key, val in profile_data.items():
        add_section(key.replace("_", " ").title() + ":", val)

    add_section("AI Output:", ai_output)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ---------------- UI & LOGIC ----------------

if st.button("🔄 Clear Profile / Restart"):
    st.warning("Resetting profile and chat — starting fresh!")
    st.session_state.profile = {}
    st.session_state.messages = []
    st.session_state.input_text = ""
    st.rerun()

user_input = st.text_area("What’s your team working on?", value=st.session_state.input_text, height=150)

if st.button("Let’s Go") and user_input.strip():
    st.session_state.input_text = ""
    extract_profile(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    if not is_profile_complete(st.session_state.profile):
        reply = build_followup_reply(st.session_state.profile)
    else:
        blended_tone = build_full_tone_instruction(st.session_state.profile)
        system_msg = f"""
        You are a helpful, witty writing assistant.

        Tone instructions based on the user:
        {blended_tone}

        Only start writing when all traits are present.
        Be clever, casual, and helpful.
        """
        st.session_state.messages.append({"role": "system", "content": system_msg})

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=st.session_state.messages
        )
        reply = response.choices[0].message["content"]
        st.session_state.messages.append({"role": "assistant", "content": reply})

# ------------- OUTPUT -----------------

if st.session_state.messages:
    st.markdown("### 💬 Conversation")
    for msg in st.session_state.messages:
        role = "👤 You" if msg["role"] == "user" else "🤖 Assistant"
        st.markdown(f"**{role}:** {msg['content']}")

    if st.session_state.messages[-1]["role"] == "assistant":
        word_file = generate_word_file(st.session_state.profile, st.session_state.messages[-1]["content"])
        st.download_button(
            label="📄 Export as Word Doc",
            data=word_file,
            file_name="generated_content.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )