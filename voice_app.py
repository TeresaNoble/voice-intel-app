import openai
import streamlit as st
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import io
import json

# ---------------------- TONE GUIDES ----------------------

VOICE_RULEBOOK = {
    "style_of_work": {
        "office_in_person": "Include at least one in-person collaborative activity per interval.",
        "office_remote": "Avoid in-person activities. Include one online collaborative activity per interval.",
        "office_mixed": "Do not require in-person activities. Include one virtual collaborative activity.",
        "customer_facing": "Activities must be short (10–15 min), suitable for breaks. Avoid desktop or mobile reliance.",
        "floor_operations": "Use high school-level instructions, quick (10–15 min), and avoid tech dependence.",
        "field_worker": "Keep activities simple and mobile-accessible. No assumption of full-time screen access."
    },
    "personality": {
        "extrovert": "Include activities involving speaking, presenting, or group collaboration.",
        "introvert": "Focus on solo reflection, writing, or quiet 1:1 conversation.",
        "mixed": "Balance solo and collaborative activities evenly."
    },
    "player_type": {
        "killers": "Include competitive tasks against others or personal bests.",
        "achievers": "Include goal-based tasks and achievement tracking, like badges or social sharing.",
        "explorers": "Include ideation, open-ended problem-solving, or research tasks.",
        "socialisers": "Include activities focused on teamwork, customer stories, and social connections.",
        "default": "Weight activity types as 80% social, 10% explorer, 10% achiever, 1% killer."
    },
    "worker_style": {
        "practical": "Use short, concise bullet-point or numbered step instructions.",
        "analytical": "Be detailed, logical, and include structured thinking tasks.",
        "creative": "Add storytelling, image-based, or expressive content prompts.",
        "interpersonal": "Focus on client service, satisfaction, and human connection.",
        "entrepreneurial": "Use innovation-based, disruptive-thinking challenges."
    },
    "tech_savviness": {
        "low": "Use plain language, avoid jargon. Provide detailed tutorials with step-by-step guidance.",
        "medium": "Use familiar tech terms. Include some intermediate tips.",
        "high": "Use technical terms fluently. Provide advanced customization options."
    },
    "generation": {
        "boomers": "Keep things straightforward, structured, and focused on job security and recognition.",
        "gen_x": "Focus on practical results, work-life balance, and flexible structure.",
        "millennials": "Include gamified elements, feedback loops, and social interaction.",
        "gen_z": "Expect fast, seamless, visual delivery. Be inclusive, creative, and interactive.",
        "gen_alpha": "Make things intuitive, visual, and reward creativity and play."
    },
    "hofstede": {
        "high_power_distance": "Maintain clear roles and hierarchy in tone.",
        "low_power_distance": "Use a collaborative tone. Flatten hierarchy.",
        "individualism": "Emphasize personal achievement and autonomy.",
        "collectivism": "Focus on group success and collaboration.",
        "masculinity": "Include competitive and success-based language.",
        "femininity": "Use cooperative, empathetic, and nurturing language.",
        "high_uncertainty_avoidance": "Keep content structured, rule-based, and predictable.",
        "low_uncertainty_avoidance": "Be flexible, ambiguous, and promote risk-taking.",
        "long_term": "Focus on ongoing growth and sustained goals.",
        "short_term": "Include quick wins and short-term motivators.",
        "indulgence": "Make tone playful, joyful, and rewarding.",
        "restraint": "Be respectful, restrained, and norm-conscious."
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
            {"role": "system", "content": "Extract profile traits based on user messages."},
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
st.title("Voice Content Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "profile" not in st.session_state:
    st.session_state.profile = {
        "generation": "Gen X",
        "tech_savviness": "medium",
        "culture": "collectivist",
        "tone_pref": "fun"
    }

user_input = st.text_input("🗣️ What’s your team working on?")
if st.button("Let’s Go") and user_input.strip():
    extract_profile(user_input)
    blended_tone = build_full_tone_instruction(st.session_state.profile)

    system_msg = f"""
    You are a writing assistant with a bright, funny, and creative personality. You help users write internal content like onboarding, training, or announcements.

    Tone Based on User Profile:
    {blended_tone}
    """
    st.session_state.messages.append({"role": "system", "content": system_msg})
    st.session_state.messages.append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=st.session_state.messages
    )
    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})

    st.markdown("### 💬 Conversation")
    for msg in st.session_state.messages:
        speaker = "👤 You" if msg["role"] == "user" else "🤖 Assistant"
        st.markdown(f"**{speaker}:** {msg['content']}")

    word_file = generate_word_file(st.session_state.profile, st.session_state.messages[-1]["content"])
    st.download_button(
        label="📄 Export as Word Doc",
        data=word_file,
        file_name="generated_content.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )