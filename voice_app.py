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

# Ensure API key is loaded
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except Exception as e:
    st.error("OpenAI key missing or invalid.")
    st.stop()

# ---------------- RULEBOOK ----------------
VOICE_RULEBOOK = {
    "style_of_work": {
        "office_remote": "Avoid in-person activities. Include online collaboration.",
        "office_mixed": "Include both in-person and virtual activities.",
        "customer_facing": "Use tasks that fit into 10–15 min breaks.",
        "field_worker": "Use tasks that work offline or on mobile.",
    },
    "personality": {
        "introvert": "Use reflective or solo activities.",
        "extrovert": "Include presenting and collaboration.",
        "mixed": "Mix solo and group tasks.",
    },
    "tech_savviness": {
        "low": "Avoid jargon. Use step-by-step help.",
        "medium": "Use familiar tech terms.",
        "high": "Use confident technical language.",
    },
    "generation": {
        "gen_x": "Be practical and balanced.",
        "millennials": "Use feedback, social, and gamified ideas.",
        "gen_z": "Use fast, visual, playful responses.",
    },
    "tone_pref": {
        "fun": "Add humor and lightness.",
        "supportive": "Be encouraging and kind.",
        "formal": "Be clear and polished.",
        "direct": "Get to the point confidently.",
    },
    "culture": {
        "individualist": "Emphasize personal achievement.",
        "collectivist": "Highlight teamwork and group wins.",
    }
}

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
    generation, tech_savviness, culture, tone_pref, personality, style_of_work

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

# ---------------- STATE SETUP ----------------
if "profile" not in st.session_state:
    st.session_state.profile = {
        "generation": "Gen X",
        "tech_savviness": "medium",
        "culture": "collectivist",
        "tone_pref": "fun",
        "style_of_work": "office_remote",
        "personality": "introvert"
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- UI + CHAT ----------------
user_input = st.text_input("What’s your team working on?")

if st.button("Let’s Go") and user_input.strip():
    extract_profile(user_input)
    blended_tone = build_full_tone_instruction(st.session_state.profile)

    st.markdown("### 🧠 Tone Settings Used")
    st.info(blended_tone)

    system_msg = f"""
    You are a fun, helpful internal content assistant.
    Use this tone based on the user's context:
    {blended_tone}

    Be brief, clear, and always helpful.
    """

    st.session_state.messages.append({"role": "system", "content": system_msg})
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=st.session_state.messages
        )
        reply = response.choices[0].message["content"]
    except Exception as e:
        st.error("Failed to get response.")
        st.text(str(e))
        st.stop()

    st.session_state.messages.append({"role": "assistant", "content": reply})

    st.markdown("### 💬 Conversation")
    for msg in st.session_state.messages:
        role = "👤 You" if msg["role"] == "user" else "🤖 Assistant"
        st.markdown(f"**{role}:** {msg['content']}")

    word_file = generate_word_file(st.session_state.profile, reply)
    st.download_button(
        label="📄 Export as Word Doc",
        data=word_file,
        file_name="generated_content.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )