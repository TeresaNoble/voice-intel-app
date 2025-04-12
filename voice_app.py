import streamlit as st
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import io
import json
from openai import OpenAI  # Updated import

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # New client initialization

# ---------------------- VOICE RULEBOOK ----------------------
VOICE_RULEBOOK = {
    "generation": {
        "boomers": "Keep things straightforward, structured, and focused on job security and recognition.",
        "gen_x": "Focus on practical results, work-life balance, and flexible structure.",
        "millennials": "Include gamified elements, feedback loops, and social interaction.",
        "gen_z": "Expect fast, seamless, visual delivery. Be inclusive, creative, and interactive.",
        "gen_alpha": "Make things intuitive, visual, and reward creativity and play."
    },
    "tone_pref": {
        "fun": "Use humor, metaphors, and light tone.",
        "formal": "Stick to polished, professional language.",
        "supportive": "Be warm and empathetic.",
        "direct": "Be brief, clear, and assertive."
    },
    "place_of_work": {
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
    "hofstede_culture": {
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
    required_fields = ["generation", "tech_savviness", "hofstede_culture", "tone_pref", "place_of_work", "personality"]
    return all(profile.get(field) for field in required_fields)

def extract_profile(user_message):
    prompt = f"""
    The user said: "{user_message}"

    Based on this, infer and update the following profile traits:
    generation, tech_savviness, culture, tone_pref, place_of_work, personality

    Use these labels:
    generation: ["Gen Z", "Millennials", "Gen X", "Boomers"]
    tech_savviness: ["low", "medium", "high"]
    culture: ["individualist", "collectivist"]
    tone_pref: ["fun", "formal", "supportive", "direct"]
    place_of_work: ["office_in_person", "office_remote", "office_mixed", "customer_facing", "floor_operations", "field_worker"]
    personality: ["extrovert", "introvert", "mixed"]

    Return only JSON.
    """
    response = client.chat.completions.create(  # Updated API call
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Extract profile traits from the user message."},
            {"role": "user", "content": prompt}
        ]
    )
    try:
        traits = json.loads(response.choices[0].message.content)  # Updated response access
        for k, v in traits.items():
            st.session_state.profile[k] = v
    except Exception:
        st.warning("Couldn't parse profile info.")

# ---------------------- STREAMLIT APP ----------------------
st.set_page_config(page_title="Custom Content Assistant", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "profile" not in st.session_state:
    st.session_state.profile = {}

st.title("Custom Content Assistant")

with st.sidebar:
    st.header("Profile")
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
        followups = {
            "generation": "Gen Z vibes? Millennials? A mysterious mix of both?",
            "tech_savviness": "How’s the tech game — smooth operators, figuring it out, or full-on ‘help me’ mode?",
            "hofstede_culture": "More independent? Or team-first decision making?",
            "tone_pref": "Playful, clear and direct, buttoned-up, or gently supportive?",
            "place_of_work": "Office-based, remote crew, or in-the-field types?",
            "personality": "Big energy extroverts, thoughtful introverts, or both?"
            "worker_style": "Practical, analytical, creative, interpersonal, or entrepreneurial?",
        }
        missing_traits = [k for k in VOICE_RULEBOOK if not st.session_state.profile.get(k)]
        reply = "Nice! Tell me a bit more so I can match your tone better:\n\n"
        reply += "\n".join([f"- {followups[trait]}" for trait in missing_traits])
        st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        tone_instructions = build_full_tone_instruction(st.session_state.profile)
        system_msg = (
            f"You are a helpful, witty writing assistant.\n"
            f"Tone instructions based on the user:\n{tone_instructions}\n"
            f"Keep it light, use humor, and always add a creative twist. Use casual, conversational language (like talking to a friend). Add humor, metaphors, and pop culture references. Avoid dry, formal language. Instructions should be fun but clear. Keep it short and easy to understand.\n"
            f"Use engaging, playful phrasing (e.g., 'A couple chicken wings short of a bucket there!' "
            f"instead of 'Just missing a few quick things to make sure the tone fits.')"
        )
        st.session_state.messages.insert(0, {"role": "system", "content": system_msg})
        response = client.chat.completions.create(  # Updated API call
            model="gpt-4",
            messages=st.session_state.messages
        )
        reply = response.choices[0].message.content  # Updated response access
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
