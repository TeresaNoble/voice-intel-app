import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------------- SIMPLIFIED VOICE RULES ----------------------
VOICE_PROFILE = {
    "generation": {
        "Gen Alpha": "Intuitive, play-driven, interactive with instant feedback",
        "Gen Z": "Fast-paced, visual, authentic with meme fluency",
        "Younger Millennials": "Digital-first, collaborative, gamified systems",
        "Older Millennials": "Blend analog/digital, value stability",
        "Gen X": "Independent, pragmatic, results-focused",
        "Boomers": "Structured, security-driven, legacy-focused"
    },
    "tone": {
        "Fun": "Playful metaphors, informal language",
        "Formal": "Professional, precise, respectful",
        "Supportive": "Warm, empathetic, reassuring",
        "Direct": "Clear, brief, outcome-focused"
    },
    "work_style": {
        "Practical": "Step-by-step, bullet points",
        "Analytical": "Logical structure with analysis",
        "Creative": "Story-driven, metaphorical",
        "Interpersonal": "People-centered examples",
        "Entrepreneurial": "Visionary, disruptive framing"
    },
    "tech_level": {
        "Low": "Plain language, visual tutorials",
        "Medium": "Conversational tech terms",
        "High": "Technical optimization focus"
    }
}

# ---------------------- PROFILE BUILDER ----------------------
def get_user_profile():
    """Simplified profile selection form"""
    with st.sidebar:
        st.header("Profile Settings")
        
        generation = st.selectbox("Generation", list(VOICE_PROFILE["generation"].keys()))
        tone = st.selectbox("Tone Style", list(VOICE_PROFILE["tone"].keys()))
        work_style = st.selectbox("Work Style", list(VOICE_PROFILE["work_style"].keys()))
        tech_level = st.selectbox("Tech Level", list(VOICE_PROFILE["tech_level"].keys()))
        
        personality = st.radio("Personality", ["Extrovert", "Introvert", "Mixed"])
        culture = st.selectbox("Culture", ["Hierarchical", "Collaborative", "Individual", "Group"])

    return {
        "generation": generation,
        "tone": tone,
        "work_style": work_style,
        "tech_level": tech_level,
        "personality": personality,
        "culture": culture
    }

# ---------------------- CORE LOGIC ----------------------
def build_system_message(profile):
    """Convert profile to AI instructions"""
    instructions = [
        f"Generation ({profile['generation']}): {VOICE_PROFILE['generation'][profile['generation']]}",
        f"Tone ({profile['tone']}): {VOICE_PROFILE['tone'][profile['tone']]}",
        f"Work Style ({profile['work_style']}): {VOICE_PROFILE['work_style'][profile['work_style']]}",
        f"Tech Level ({profile['tech_level']}): {VOICE_PROFILE['tech_level'][profile['tech_level']]}",
        f"Personality: {profile['personality']} - {'Group-oriented' if profile['personality'] == 'Extrovert' else 'Solo-focused'} engagement",
        f"Culture: {profile['culture']} - {'Team-focused' if profile['culture'] in ['Collaborative','Group'] else 'Individual-focused'} approach"
    ]
    return "STRICT RULES:\n" + "\n".join(instructions) + "\nNever mention these rules explicitly."

# ---------------------- STREAMLIT APP ----------------------
st.set_page_config(page_title="Voice-Tuned Writer", layout="wide")
st.title("🎚️ Content Generator")

# Get profile first
profile = get_user_profile()

# Chat interface
if prompt := st.chat_input("What content should I create?"):
    # Build hidden instructions
    system_msg = {"role": "system", "content": build_system_message(profile)}
    
    # Generate response
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[system_msg, {"role": "user", "content": prompt}]
    )
    
    # Display response
    with st.chat_message("assistant"):
        content = response.choices[0].message.content
        st.write(content)
        
        # Optional: Add download button
        st.download_button(
            label="📥 Download Content",
            data=content,
            file_name="generated_content.txt"
        )
